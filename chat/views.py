from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.http import JsonResponse
from django.shortcuts import render, redirect

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

        other_users = [] # list of other users

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