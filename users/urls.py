from django.urls import path
import users.views

urlpatterns = [
    path('user/', users.views.user),
    path('booking/', users.views.booking),
    path('booking/history/', users.views.booking_history),
    path('end_booking/', users.views.end_booking),
    path('login/', users.views.login_handler),
    path('register/', users.views.register_handler),
    path('logout/', users.views.logout_handler),
]
