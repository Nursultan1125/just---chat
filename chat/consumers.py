import json
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from chat.models import Message
from django.contrib.auth import get_user_model

from chat.models import ConnectionPerson
User = get_user_model()


@database_sync_to_async
def increment_count_connection():
    connection = ConnectionPerson.objects.get(id=1)
    connection.count_connection += 1
    connection.save()


@database_sync_to_async
def decrement_count_connection():
    connection = ConnectionPerson.objects.get(id=1)
    connection.count_connection -= 1
    connection.save()


class ChatAsyncConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print("connect")
        await increment_count_connection()

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print("disconnect")
        await decrement_count_connection()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class ChatConsumer(WebsocketConsumer):
    room_group_name = None
    room_name = None

    def fetch_messages(self, data):
        messages = Message.last_10_message()
        content = {
            'messages': self.messages_to_json(messages)
        }
        self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'author': message.author.username,
            'content': message.content,
            'timestamp': str(message.timestamp)
        }

    def new_message(self, data):
        author = data['from']
        author_user = User.objects.filter(usernname=author)
        message = Message.objects.create(
            author=author_user,
            content=data['message']
        )

        content = {
            'command': "new_message",
            'message': self.message_to_json(message)
        }
        self.send(content)

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chats_{self.room_name}'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.room_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.room_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_messages(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
