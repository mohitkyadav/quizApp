import json
from django.db import models
from django.utils.six import python_2_unicode_compatible
from channels import Group

from quizzie.settings import MSG_TYPE_MESSAGE


class Room(models.Model):
    title = models.CharField(max_length=255)
    staff_only = models.BooleanField(default=False)
    chat_flag = models.BooleanField(default=False)

    def str(self):
        return self.title

    @property
    def websocket_group(self):
        """
        Returns the Channels Group that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return Group("room-%s" % self.id)

    def send_message(self, message, user, msg_type=MSG_TYPE_MESSAGE):
        """
        Called to send a message to the room on behalf of a user.
        """
        final_msg = {'room': str(self.id), 'message': message, 'username': user.username, 'msg_type': msg_type}

        # Send out the message to everyone in the room
        self.websocket_group.send(
            {"text": json.dumps(final_msg)}
        )


class Answer(models.Model):
    text = models.CharField(max_length=128, verbose_name='Answer\'s text here.')
    correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Question(models.Model):
    question_text = models.CharField(max_length=128, verbose_name='Enter question here.')
    answers = models.ManyToManyField(Answer)
    is_final = models.BooleanField(default=False)

    def __str__(self):
        return '{content} - {published}'.format(content=self.question_text, published=self.is_final)


class Quiz(models.Model):
    name = models.CharField(max_length=64, verbose_name='Name of exam')
    slug = models.SlugField(max_length=64, unique=True)
    questions = models.ManyToManyField(Question)

    def __str__(self):
        return self.name
