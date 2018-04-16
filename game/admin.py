from django.contrib import admin
from .models import Room, Question, Option, Quiz, Response, Score


admin.site.register(
    Room,
    list_display=["id", "title", "staff_only", "chat_flag"],
    list_display_links=["id", "title"],
)

admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Quiz)
admin.site.register(Response)
admin.site.register(Score)
