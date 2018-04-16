from .models import Quiz, Room, Question, Option, Response


def get_options(question):
    options = Option.objects.all().filter(question=question)
    temp = {}
    cnt = 0
    for option in options:
        temp[str(cnt)] = {
            "text": option.text,
            "correct": option.is_correct
        }
        cnt += 1
    return temp


def get_room(room_id):
    return Room.objects.get(id=room_id)


def get_quiz(room):
    return Quiz.objects.get(room=room)


def get_questions(room_id):
    room = get_room(room_id)
    quiz = get_quiz(room)
    questions = Question.objects.all().filter(quiz=quiz)
    '''
     "0": {
            "rid": room_id,
            "qno": 0,
            "question": question_text,
            "qid": question_id,
            "options": {
                            "0": {
                                    "text": option_text,
                                    "correct": true
                                 },
                            "1": {
                                    "text": option_text,
                                    "correct": true
                                 },
                            "2": {
                                    "text": option_text,
                                    "correct": true
                                 }
                        }
        }
    '''
    quiz_questions = {}
    counter = 0
    for question in questions:
        options = get_options(question)
        temp = {
            "rid": room_id,
            "qno": counter,
            "question": question.question_text,
            "qid": question.id,
            "options": options
        }
        quiz_questions[str(counter)] = temp
        counter += 1
    return quiz_questions


def set_response(q_id, selected_choice, user):
    question = Question.objects.get(id=q_id)
    options = Option.objects.filter(question=question)
    index = int(selected_choice)
    is_correct = options[index-1].is_correct
    response = Response(question=question, user=user, selected_option=options[index-1], is_correct=is_correct)
    response.save()
