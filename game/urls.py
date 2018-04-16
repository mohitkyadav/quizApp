from django.conf.urls import url
from django.views.generic.base import RedirectView
from . import views

app_name = 'game'

urlpatterns = [
    url(r'^(?P<quiz_id>.+)/$', views.quiz_leaderboard, name='quiz_leaderboard'),
]
