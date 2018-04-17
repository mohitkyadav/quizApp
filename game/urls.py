from django.conf.urls import url
from django.views.generic.base import RedirectView
from . import views

app_name = 'game'

urlpatterns = [
    url(r'^leaderboard/(?P<quiz_id>.+)/$', views.quiz_leaderboard, name='quiz_leaderboard'),
    url(r'^profile/$', views.profile, name='profile')
]
