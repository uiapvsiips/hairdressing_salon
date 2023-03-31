from django.urls import path
import users.views

urlpatterns = [
    path('user/', users.views.user),
    path('booking/', users.views.booking),
    path('booking/services/', users.views.booking_services),
    path('booking/specialists/', users.views.booking_specialists),
    path('booking/services/<int:service_id>/', users.views.booking_to_service),
    path('booking/specialists/<int:specialist_id>/', users.views.booking_to_specialist),
    path('booking/services/<int:service_id>/book/', users.views.end_service_booking),
    path('booking/specialists/<int:specialist_id>/book/', users.views.end_specialist_booking),
    path('login/', users.views.login),
    path('register/', users.views.register),
]
