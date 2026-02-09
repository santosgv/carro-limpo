from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from .models import BusinessHours, Agendamento

def get_available_slots(date, servico):
    """
    Retorna lista de datetimes (start) disponíveis para o serviço no date.
    """
    weekday = date.weekday()
    bh = BusinessHours.objects.filter(weekday=weekday).first()
    if not bh or bh.is_closed:
        return []

    # monta o intervalo do dia no timezone atual
    tz = timezone.get_current_timezone()
    day_start = timezone.make_aware(datetime.combine(date, bh.start_time), tz)
    day_end = timezone.make_aware(datetime.combine(date, bh.end_time), tz)

    duration = timedelta(minutes=servico.duracao)
    step = timedelta(minutes=bh.slot_minutes)

    # pega agendamentos do dia (apenas scheduled)
    day_appts = Agendamento.objects.filter(
        status="scheduled",
        inicio_data_hora__lt=day_end,
        fim_data_hora__gt=day_start,
    ).values("inicio_data_hora", "fim_data_hora")

    intervals = [(a["inicio_data_hora"], a["fim_data_hora"]) for a in day_appts]

    slots = []
    current = day_start

    while current + duration <= day_end:
        candidate_start = current
        candidate_end = current + duration

        conflict = any(candidate_start < end and candidate_end > start for start, end in intervals)
        if not conflict:
            slots.append(candidate_start)

        current += step

    return slots
