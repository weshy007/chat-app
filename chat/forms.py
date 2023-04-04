from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile


class UserCreation(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'email']

    def save(self, commit=True):
        user = super(UserCreation, self).save(commit=False)
        if commit:
            user.is_active = True
            user.save()

        return user
