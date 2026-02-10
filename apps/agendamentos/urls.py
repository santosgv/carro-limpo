from django.urls import path
from .views import agendar_view,disponibilidade_view,agendamentos_eventos_json,calendario_admin_view,atualizar_status_agendamento


app_name = 'agendamentos'

urlpatterns = [
    path("", agendar_view, name="agendamento"),
    path('horarios/',disponibilidade_view, name='horarios_disponiveis'),
    path("agenda/", calendario_admin_view, name="agenda"),
    path("eventos/",agendamentos_eventos_json, name="eventos_agendamentos"),
    path("atualiza/<int:ag_id>/status/",atualizar_status_agendamento, name="atualizar_status_agendamento")
]
