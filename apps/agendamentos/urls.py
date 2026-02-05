from django.urls import path
from .views import agendar_view

urlpatterns = [
    path("", agendar_view, name="agendamento"),
    #path('agendar/<str:placa>/',agendar_servico, name='agendar_com_placa'),
]
