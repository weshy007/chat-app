from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import UserCreationForm
from .models import Message, UserProfile


# Create your views here.
def signup(request):
    userform = UserCreationForm()
    if request.method == 'POST':
        if userform.is_valid():
            uf = userform.save(commit=False)
            uf.save()

            # Login user and redirect to home
            if uf is not None:
                if uf.is_active:
                    login(request, uf)  # Login the user
                    return redirect('chat:message_list')  # redirect to home
        else:
            errors = {}

            for field in userform:
                for error in field.errors:
                    errors[field.name]  # add the error to the dictionary as the value and the field name as the key
            return JsonResponse({"status": False, "errors": userform})

    else:
        userform = UserCreationForm()

    return render(request, 'auth/signup.html', {"form": userform})


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'chat/messages_list.html'
    login_url = '/login/'

    # Display messages
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = UserProfile.objects.get(pk=self.request.user.pk)  # get the pk
        messages = Message.get_message_list(user)  # getting messages from you and other user

        other_users = []  # list of other users

        # getting the other person's name from the message list and adding them to a list
        for i in range(len(messages)):
            if messages[i].sender != user:
                other_users.append(messages[i].sender)
            else:
                other_users.append(messages[i].recipient)

        context['messages_list'] = messages
        context['other_users'] = other_users
        context['you'] = user

        return context


class UserListView(LoginRequiredMixin, ListView):
    model = UserProfile
    template_name = 'chat/users_list.html'
    context_object_name = 'users'
    login_url = '/login/'

    # context data for users list
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = UserProfile.objects.get(pk=self.request.user.pk)
        context['users'] = UserProfile.objects.exclude(pk=user.pk)  # get all users except you
        return context


class InboxView(ListView):
    model = Message
    template_name = 'chat/inbox.html'
    login_url = '/login/'
    queryset = UserProfile.objects.all()

    # to send a message (pass the username instead of the primary key to the post function)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    # override detail view default request pk or slug to get username instead
    def get_object(self):
        user_name = self.kwargs.get('username')
        return get_object_or_404(UserProfile, usernmae=user_name)

    # context data for the chat view
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = UserProfile.objects.get(pk=self.request.user.pk)
        other_user = UserProfile.objects.get(username=self.kwargs.get("username"))
        messages = Message.get_message_list(user)  # get all messages between the users

        other_users = []

        for i in range(len(messages)):
            if messages[i].sender != user:
                other_users.append(messages[i].sender)
            else:
                other_users.append(messages[i].recipient)

        sender = other_user  # the sender will be the recipient of the most recent message after it's sent
        recipient = user  # the recipient of the message will be the sender of the most recent message after it's sent

        context['messages'] = Message.get_all_messages(sender, recipient)  # get all the messages between the sender(you) and the recipient (the other user)
        context['messages_list'] = messages  # for MessagesListView template
        context['other_person'] = other_user  # get the other person you are chatting with from the username provided
        context['you'] = user
        context['other_users'] = other_users

        return context

    # send message
    def post(self, request, *args, **kwargs):
        sender = UserProfile.objects.get(pk=request.POST.get('you'))  # get the sender of the message(the person sending it)
        recipient = UserProfile.objects.get(pk=request.POST.get('recipient'))
        message = request.POST.get('message')

        # if the sender is logged in, send the message
        if request.user.is_authenticated:
            if request.method == 'POST':
                if message:
                    Message.objects.create(sender=sender, recipient=recipient, message=message)
            return redirect('chat:inbox', username=recipient.username)  # redirect to the inbox of the recipient

        else:
            return render(request, 'auth/login.html')
