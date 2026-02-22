from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from users import views as user_views
from users.forms import CustomAuthenticationForm

urlpatterns = [

    # Custom Register View
    path('register/', user_views.register_view, name='register'),

    # Built-in Login View with Custom Form
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),

    # Built-in Logout View
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Home Page
    path('', user_views.home_view, name='home'),
]