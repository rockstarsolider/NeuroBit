from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import AnonymousUser
from django.template.loader import get_template

GROUP_NAME_TEMPLATE = "notifications_user_{user_id}"


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope.get("user", None)
        if user is None or isinstance(user, AnonymousUser) or not user.is_authenticated:
            # Reject anonymous
            self.close(code=4401)  # unauthorized
            return
        self.user = user
        self.group_name = GROUP_NAME_TEMPLATE.format(user_id=self.user.pk)

        # add to group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        if self.user or self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name, self.channel_name
            )

    def notification_created(self, event):
        html = get_template("notifications/notification_partial.html").render(
            context={"message": event["text"]}
        )
        self.send(text_data=html)