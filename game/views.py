from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Room, Quiz, Score, Room, Question


@login_required
def index(request):
    rooms = Room.objects.order_by("title")

    # Render that in the index template
    return render(request, "index.html", {
        "rooms": rooms,
    })


def quiz_leaderboard(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    scores = Score.objects.filter(quiz=quiz).order_by("score")
    questions = Question.objects.filter(quiz=quiz)
    print(questions)
    return render(request, "quiz/quiz_leaderboard.html", {
        "quiz_id": quiz_id,
        "quiz_name": quiz.name,
        "questions": questions,
        "scores": reversed(scores),
    })
