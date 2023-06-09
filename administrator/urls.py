from django.urls import path
import administrator.views

urlpatterns = [
    path('panel/', administrator.views.panel),
    path('panel/bookings/', administrator.views.bookings),
    path('panel/specialists/', administrator.views.specialists),
    path('panel/specialists/<int:specialist_id>/', administrator.views.specialist_id_handler),
    path('panel/specialists/<int:specialist_id>/edit_schedule', administrator.views.edit_schedule),
    path('panel/specialists/<int:specialist_id>/masters_booking/', administrator.views.masters_booking),
    path('panel/services/', administrator.views.services_handler),
    path('panel/services/<int:service_id>/', administrator.views.service_id_handler),
]