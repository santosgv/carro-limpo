from django.urls import path
from .views import (agendar_view,disponibilidade_view,agendamentos_eventos_json,
                    calendario_admin_view,atualizar_status_agendamento,
                    BusinessHoursListView,BusinessHoursCreateView,BusinessHoursUpdateView,BusinessHoursDeleteView)


app_name = 'agendamentos'

urlpatterns = [
    path("", agendar_view, name="agendamento"),
    path('horarios/',disponibilidade_view, name='horarios_disponiveis'),
    path("agenda/", calendario_admin_view, name="agenda"),
    path("eventos/",agendamentos_eventos_json, name="eventos_agendamentos"),
    path("atualiza/<int:ag_id>/status/",atualizar_status_agendamento, name="atualizar_status_agendamento"),
    path('business/',BusinessHoursListView.as_view(), name='business_hours_list'),
    path('novo/', BusinessHoursCreateView.as_view(), name='business_hours_create'),
    path('<int:pk>/editar/', BusinessHoursUpdateView.as_view(), name='business_hours_update'),
    path('<int:pk>/excluir/',BusinessHoursDeleteView.as_view(), name='business_hours_delete'),
]
