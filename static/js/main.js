$(function () {
    // Correctly decide between ws:// and wss://
    var ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    var ws_path = ws_scheme + '://' + window.location.host + "/chat/stream/";
    console.log("Connecting to " + ws_path);
    var socket = new ReconnectingWebSocket(ws_path);

    // Helpful debugging
    socket.onopen = function () {
        console.log("Connected to chat socket");
    };
    socket.onclose = function () {
        console.log("Disconnected from chat socket");
    };

    socket.onmessage = function (message) {
        // Decode the JSON
        console.log("Got websocket message " + message.data);
        var data = JSON.parse(message.data);
        // Handle errors
        if (data.error) {
            alert(data.error);
            return;
        }
        // Handle joining
        if (data.join) {
            console.log("Joining room " + data.join);
            var q_no = 0;
            var roomdiv = $(
                "<div class='room' id='room-" + data.join + "'>" +
                    "<h2>" + data.title + "</h2>" +
                    "<div class='message' q_id=''>" +
                    "<span class='body'></span>" +
                        "<h3 choice='' id='choice_a' class='choice'></h3>" +
                        "<h3 choice='' id='choice_b' class='choice'></h3>" +
                        "<h3 choice='' id='choice_c' class='choice'></h3>" +
                    "</div>" +
                    //"<input><button>Send</button>" +
                    "<button>start</button>" +
                "</div>"
            );
            // chat send
            // $("#chats").append(roomdiv);
            // roomdiv.find("button").on("click", function () {
            //     socket.send(JSON.stringify({
            //         "command": "send",
            //         "room": data.join,
            //         "message": roomdiv.find("input").val()
            //     }));
            //     roomdiv.find("input").val("");
            // });
            $("#chats").append(roomdiv);
            roomdiv.find("button").on("click", function () {
                socket.send(JSON.stringify({
                    "command": "start_quiz",
                    "room": data.join
                }));
            });
// Respond when a choice is clicked
            var choice_first = roomdiv.find("#choice_a");
            var choice_second = roomdiv.find("#choice_b");
            var choice_third = roomdiv.find("#choice_c");

            choice_first.on("click", function () {
                var res_q_id = roomdiv.find(".body")[0].getAttribute("q_id");
                q_no = q_no + 1;
                console.log(q_no);
                socket.send(JSON.stringify({
                    "command": "submit",
                    "room": data.join,
                    "q_id": res_q_id,
                    "selected_choice": "1",
                    "next_q": q_no
                }));
            });
            choice_second.on("click", function () {
               var res_q_id = roomdiv.find(".body")[0].getAttribute("q_id");
               q_no = q_no + 1;
                socket.send(JSON.stringify({
                    "command": "submit",
                    "room": data.join,
                    "q_id": res_q_id,
                    "selected_choice": "2",
                    "next_q": q_no
                }));
            });
            choice_third.on("click", function () {
               var res_q_id = roomdiv.find(".body")[0].getAttribute("q_id");
               q_no = q_no + 1;
                socket.send(JSON.stringify({
                    "command": "submit",
                    "room": data.join,
                    "q_id": res_q_id,
                    "selected_choice": "3",
                    "next_q": q_no
                }));
            });
// Respond when a choice is clicked
            // Handle leaving
        } else if (data.leave) {
            console.log("Leaving room " + data.leave);
            $("#room-" + data.leave).remove();
        } else if(data.start_quiz) {
            var msgDiv = $("#room-" + data.room + " .body");
            var q_id = data.q_id;
            msgDiv[0].innerHTML = data.question;
            msgDiv[0].setAttribute("q_id", data.q_id);
            var choices = $("#room-" + data.room + " .choice");
            choices[0].innerHTML = data.choice_a;
            choices[1].innerHTML = data.choice_b;
            choices[2].innerHTML = data.choice_c;

            choices[0].setAttribute("choice", data.choice_a);
            choices[1].setAttribute("choice", data.choice_b);
            choices[2].setAttribute("choice", data.choice_c);

            //msgdiv.scrollTop(msgdiv.prop("scrollHeight"));

        } else if(data.end_quiz) {
            console.log("Thanks for your precious time.")
        }
        else if (data.message || data.msg_type !== 0) {
            var msgdiv = $("#room-" + data.room + " .messages");
            var ok_msg = "";
            // msg types are defined in chat/settings.py
            // Only for demo purposes is hardcoded, in production scenarios, consider call a service.
            switch (data.msg_type) {
                case 0:
                    // Message
                    ok_msg = "<div class='message'>" +
                        "<span class='username'>" + data.username + "</span>" +
                        "<span class='body'>" + data.message + "</span>" +
                        "</div>";
                    break;
                case 1:
                    // Warning/Advice messages
                    ok_msg = "<div class='contextual-message text-warning'>" + data.message + "</div>";
                    break;
                case 2:
                    // Alert/Danger messages
                    ok_msg = "<div class='contextual-message text-danger'>" + data.message + "</div>";
                    break;
                case 3:
                    // "Muted" messages
                    ok_msg = "<div class='contextual-message text-muted'>" + data.message + "</div>";
                    break;
                case 4:
                    // User joined room
                    ok_msg = "<div class='contextual-message text-muted'>" + data.username + " joined the room!" + "</div>";
                    break;
                case 5:
                    // User left room
                    ok_msg = "<div class='contextual-message text-muted'>" + data.username + " left the room!" + "</div>";
                    break;
                default:
                    console.log("Unsupported message type!");
                    return;
            }
            msgdiv.append(ok_msg);
            msgdiv.scrollTop(msgdiv.prop("scrollHeight"));

        } else {
            console.log("Cannot handle message!");
        }
    };

    // Says if we joined a room or not by if there's a div for it
    function inRoom(roomId) {
        return $("#room-" + roomId).length > 0;
    }

    // Room join/leave
    $("li.room-link").click(function () {
        var roomId = $(this).attr("data-room-id");
        if (inRoom(roomId)) {
            // Leave room
            $(this).removeClass("joined");
            socket.send(JSON.stringify({
                "command": "leave",  // determines which handler will be used (see chat/routing.py)
                "room": roomId
            }));
        } else {
            // Join room
            $(this).addClass("joined");
            socket.send(JSON.stringify({
                "command": "join",
                "room": roomId
            }));
        }
    });
});
