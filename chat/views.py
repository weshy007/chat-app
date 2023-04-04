from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .forms import UserCreationForm


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
