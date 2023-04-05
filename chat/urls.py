from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.MessageListView.as_view(), name='message_list'),
    path('signup/', views.signup, name='signup'),
    path('meet/', views.UserListView.as_view(), name='users_list'),
    path('inbox/<str:username>/', views.InboxView.as_view(), name='inbox'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(next_page='chat:message_list'), name='logout'),
]