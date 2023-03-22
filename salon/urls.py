from django.urls import path
import salon.views

urlpatterns = [
    path('abc/', salon.views.abc),
    path('services/', salon.views.services_handler),
    path('services/<int:service_id>', salon.views.service_id_handler),
]
