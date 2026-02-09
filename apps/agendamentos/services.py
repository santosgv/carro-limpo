# apps/agendamentos/services.py
from datetime import datetime, timedelta
from django.utils import timezone

from .models import BusinessHours, Agendamento

def get_business_hours_for_date(date):
    """Retorna BusinessHours do user para a data informada."""
    weekday = date.weekday()  # 0=segunda..6=domingo
    return BusinessHours.objects.filter(weekday=weekday).first()

def is_slot_available(servico, start_dt):
    """
    Valida se start_dt é um horário disponível:
      - Dentro do BusinessHours do dia
      - Alinhado ao slot (ex.: 15 em 15)
      - Não conflita com outro agendamento (scheduled)
    """
    tz = timezone.get_current_timezone()
    if timezone.is_naive(start_dt):
        start_dt = timezone.make_aware(start_dt, tz)

    bh = get_business_hours_for_date(start_dt.date())
    if not bh or bh.is_closed:
        return False, "Empresa fechada nesse dia."

    duration = timedelta(minutes=servico.duracao)
    end_dt = start_dt + duration

    day_start = timezone.make_aware(datetime.combine(start_dt.date(), bh.start_time), tz)
    day_end = timezone.make_aware(datetime.combine(start_dt.date(), bh.end_time), tz)

    # 1) Dentro do expediente
    if start_dt < day_start or end_dt > day_end:
        return False, "Fora do horário de funcionamento."

    # 2) Respeita o step do slot (ex.: 15 min)
    #    Regra: (start - day_start) deve ser múltiplo de slot_minutes
    slot_delta = int(bh.slot_minutes)
    minutes_from_open = int((start_dt - day_start).total_seconds() // 60)
    if minutes_from_open % slot_delta != 0:
        return False, "Horário inválido (não está alinhado ao slot)."

    # 3) Sem conflito com agendamentos existentes
    conflict = Agendamento.objects.filter(
        status="scheduled",
        inicio_data_hora__lt=end_dt,
        fim_data_hora__gt=start_dt,
    ).exists()
    if conflict:
        return False, "Este horário não está mais disponível."

    return True, ""