import json
import uuid
from django.db import models
from channels import Group

from quizzie.settings import MSG_TYPE_MESSAGE


class Room(models.Model):
    title = models.CharField(max_length=255)
    staff_only = models.BooleanField(default=False)
    chat_flag = models.BooleanField(default=False)

    def __str__(self):
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


class Quiz(models.Model):
    name = models.CharField(max_length=64, verbose_name='Name of exam')
    id = models.CharField(unique=True, default=uuid.uuid4,
                          editable=False, max_length=50, primary_key=True)
    slug = models.SlugField(max_length=64, unique=True)
    room = models.OneToOneField(Room, null=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    id = models.CharField(unique=True, default=uuid.uuid4,
                          editable=False, max_length=50, primary_key=True)
    question_text = models.CharField(max_length=128, verbose_name='Enter question here.')
    is_final = models.BooleanField(default=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return '{content} - {published}'.format(content=self.question_text, published=self.is_final)


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    text = models.CharField(max_length=128, verbose_name='Answer\'s text here.')
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
