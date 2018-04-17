import json
from channels import Channel
from channels.auth import channel_session_user_from_http, channel_session_user

from quizzie.settings import MSG_TYPE_LEAVE, MSG_TYPE_ENTER, NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS
from .models import Room, Score
from .utils import get_room_or_error, catch_client_error
from .exceptions import ClientError
from .helpers import get_questions, set_response, set_score


# This decorator copies the user from the HTTP session (only available in
# websocket.connect or http.request messages) to the channel session (available
# in all consumers with the same reply_channel, so all three here)
@channel_session_user_from_http
def ws_connect(message):
    # users = ['test', 'test2']
    message.reply_channel.send({"accept": True})
    # for u in users:
    #     Group("%s" % u).add(message.reply_channel)
    message.channel_session['rooms'] = []


@channel_session_user
def ws_disconnect(message):
    # Unsubscribe from any connected rooms
    for room_id in message.channel_session.get("rooms", set()):
        try:
            room = Room.objects.get(pk=room_id)
            # Removes us from the room's send group. If this doesn't get run,
            # we'll get removed once our first reply message expires.
            room.websocket_group.discard(message.reply_channel)
        except Room.DoesNotExist:
            pass


# Unpacks the JSON in the received WebSocket frame and puts it onto a channel
# of its own with a few attributes extra so we can route it
# This doesn't need @channel_session_user as the next consumer will have that,
# and we preserve message.reply_channel (which that's based on)
def ws_receive(message):
    # All WebSocket frames have either a text or binary payload; we decode the
    # text part here assuming it's JSON.
    # You could easily build up a basic framework that did this encoding/decoding
    # for you as well as handling common errors.
    payload = json.loads(message['text'])
    payload['reply_channel'] = message.content['reply_channel']
    Channel("chat.receive").send(payload)


# Channel_session_user loads the user out from the channel session and presents
# it as message.user. There's also a http_session_user if you want to do this on
# a low-level HTTP handler, or just channel_session if all you want is the
# message.channel_session object without the auth fetching overhead.
@channel_session_user
# @catch_client_error
def chat_join(message):
    # Find the room they requested (by ID) and add ourselves to the send group
    # Note that, because of channel_session_user, we have a message.user
    # object that works just like request.user would. Security!
    # print(message.user)
    room = get_room_or_error(message["room"], message.user)

    # Send a "enter message" to the room if available
    if NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
        room.send_message(None, message.user, MSG_TYPE_ENTER)

    # OK, add them in. The websocket_group is what we'll send messages
    # to so that everyone in the chat room gets them.
    room.websocket_group.add(message.reply_channel)
    message.channel_session['rooms'] = list(set(message.channel_session['rooms']).union([room.id]))
    # Send a message back that will prompt them to open the room
    # Done server-side so that we could, for example, make people
    # join rooms automatically.

    # Get the JSoN for Quiz here

    message.reply_channel.send({
        "text": json.dumps({
            "join": str(room.id),
            "title": room.title,
        }),
    })


@channel_session_user
@catch_client_error
def chat_leave(message):
    # Reverse of join - remove them from everything.
    room = get_room_or_error(message["room"], message.user)

    # Send a "leave message" to the room if available
    if NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
        room.send_message(None, message.user, MSG_TYPE_LEAVE)

    room.websocket_group.discard(message.reply_channel)
    message.channel_session['rooms'] = list(set(message.channel_session['rooms']).difference([room.id]))
    # Send a message back that will prompt them to close the room
    message.reply_channel.send({
        "text": json.dumps({
            "leave": str(room.id),
        }),
    })


@channel_session_user
# @catch_client_error
def chat_send(message):
    if int(message['room']) not in message.channel_session['rooms']:
        raise ClientError("ROOM_ACCESS_DENIED")
    room = get_room_or_error(message["room"], message.user)
    room.send_message(message["message"], message.user)


@channel_session_user
def start_quiz(message):
    room = get_room_or_error(message["room"], message.user)
    quiz = get_questions(message["room"])
    message.reply_channel.send({
        "text": json.dumps({
            "room": str(room.id),
            "start_quiz": True,
            "title": room.title,
            "q_id": quiz['0']['qid'],
            "question": quiz['0']['question'],
            "choice_a": quiz['0']['options']['0']['text'],
            "choice_b": quiz['0']['options']['1']['text'],
            "choice_c": quiz['0']['options']['2']['text'],
        }),
    })


@channel_session_user
def next_question(message):
    room = get_room_or_error(message["room"], message.user)
    quiz = get_questions(message["room"])
    set_response(message["q_id"], message["selected_choice"], message.user)

    quiz = get_questions(message["room"])
    if message["next_q"] < len(quiz):
        q_no = str(message["next_q"])
        print(q_no)
        message.reply_channel.send({
            "text": json.dumps({
                "room": str(room.id),
                "start_quiz": True,
                "title": room.title,
                "q_id": quiz[q_no]['qid'],
                "question": quiz[q_no]['question'],
                "choice_a": quiz[q_no]['options']['0']['text'],
                "choice_b": quiz[q_no]['options']['1']['text'],
                "choice_c": quiz[q_no]['options']['2']['text'],
                "q_no": str(q_no)
            }),
        })
    elif message["next_q"] is len(quiz):
        score = set_score(message["room"], message.user)
        print(score)
        message.reply_channel.send({
            "text": json.dumps({
                "room": str(room.id),
                "end_quiz": True,
                "title": room.title,
                "time": str(score.date),
                "score": str(score.score),
                "max_score": str(score.max_score),
            }),
        })
    else:
        message.reply_channel.send({
            "text": json.dumps({
                "room": str(room.id),
                "end_quiz": True,
                "title": room.title,
                "err": "Something went wrong :/",
            }),
        })
