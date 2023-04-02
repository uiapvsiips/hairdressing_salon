from django.urls import path
import users.views

urlpatterns = [
    path('user/', users.views.user),
    path('booking/', users.views.booking),
    path('end_booking/', users.views.end_booking),
    path('login/', users.views.login),
    path('register/', users.views.register),
]
