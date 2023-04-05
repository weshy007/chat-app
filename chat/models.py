from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class UserProfile(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'chat_users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Message(models.Model):
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sender')
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='recipient')
    message = models.TextField()
    date = models.DateField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message

    class Meta:
        db_table = 'chat_messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Message'
        ordering = ('-date', )

    # Get messages between two user
    def get_all_messages(self, id_1, id_2):
        messages = []

        # Messages got sorted by date
        # (sender to recipient)
        message1 = Message.objects.filter(sender_id=id_1, recepient_id=id_2).order_by('-date')
        for x in range(len(message1)):
            messages.append(message1[x])

        # Recipient to sender
        message2 = Message.objects.filter(sender_id=id_2, receipient_id=id_1).order_by('-date')
        for x in range(len(message2)):
            messages.append(message2[x])

        # Because the function is called when viewing the chat, we'll return all messages as read
        for x in range(len(messages)):
            messages[x].is_read = True

        # Sort by date
        messages.sort(key=lambda x: x.date, reverse=False)
        return messages

    def get_message_list(self, u):
        # get all messages
        m = []  # stores messages sorted by newst
        j = []  # stores all usernames after removing duplicates
        k = []  # stores sorted messages form sorted usernames

        for message in Message.objects.all():
            for_you = message.recipient == u  # message received by user
            from_you = message.sender == u  # message sent by user

            if for_you or from_you:
                m.append(message)
                m.sort(key=lambda x: x.sender.username)  # sort messages by senders
                m.sort(key=lambda x: x.date, reverse=True)  # sort the messages by date

        # remove duplicates usernames and get single message(latest) per username(other user) (between you & other user)
        for i in m:
            if i.sender.username not in j or i.recipient.username not in j:
                j.append(i.sender.username)
                j.append(i.recipient.username)
                k.append(i)

        return k
