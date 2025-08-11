from django.urls import path
from .views import csrf_token_view, login_view, logout_view, me_view

urlpatterns = [
    path('csrf', csrf_token_view, name='csrf'),
    path('login', login_view, name='login'),
    path('logout', logout_view, name='logout'),
    path('me', me_view, name='me'),
]


