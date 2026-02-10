from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from .forms import AgendamentoForm
from apps.servicos.models import Servico
from apps.clientes.models import Cliente
from .models import Agendamento
from .services import is_slot_available,get_business_hours_for_date
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST

def agendar_view(request):
    if request.method == 'POST':
        form = AgendamentoForm(request.POST)

        if form.is_valid():
            agendamento = form.save(commit=False)
            agendamento = agendamento

            placa = form.cleaned_data['placa'].upper()

            cliente_cadastrado = Cliente.objects.filter(placa__iexact=placa).first()


            # ✅ calcula fim_data_hora antes de validar (sua modelagem usa isso)
            # (se seu model já calcula no save, aqui a gente calcula para validar conflito/expediente)
            agendamento.fim_data_hora = agendamento.inicio_data_hora + timezone.timedelta(
                minutes=agendamento.servico.duracao
            )

            # ✅ valida disponibilidade (expediente + slot + conflito)
            ok, msg = is_slot_available(
                servico=agendamento.servico,
                start_dt=agendamento.inicio_data_hora
            )
            if not ok:
                form.add_error('inicio_data_hora', msg)
            else:
                # ✅ roda validações de domínio (clean/full_clean do model)
                # Isso pega:
                # - conflito (se você colocou no clean)
                # - serviço do mesmo user, etc.
                try:
                    agendamento.full_clean()
                    agendamento.save()
                    tem_beneficio = False
                    desconto = 0
                    
                    if cliente_cadastrado != None:
                        agendamento.cliente = cliente_cadastrado
                        desconto = agendamento.servico.valor - 10
                        tem_beneficio = True
                    return render(request, 'sucesso.html', {'agendamento': agendamento,
                                                            'beneficio': tem_beneficio,
                                                            'desconto':desconto
                                                           })
                except ValidationError as e:
                    # joga os erros no form
                    if hasattr(e, "message_dict"):
                        for field, errors in e.message_dict.items():
                            for err in errors:
                                form.add_error(field if field in form.fields else None, err)
                    else:
                        form.add_error(None, e.messages)

    else:
        form = AgendamentoForm()

    return render(request, 'agendar.html', {
        'form': form,
        'today': timezone.localdate(),
    })

def disponibilidade_view(request):
    servico_id = request.GET.get("servico")
    date_str = request.GET.get("data")

    servico = get_object_or_404(Servico, pk=servico_id)
    date = parse_date(str(date_str))


    if not date:
        return JsonResponse({"error": "Data inválida"}, status=400)


    bh = get_business_hours_for_date(date)
    if not bh or bh.is_closed:
        return JsonResponse({"slots": []})

    tz = timezone.get_current_timezone()
    day_start = timezone.make_aware(datetime.combine(date, bh.start_time), tz)
    day_end = timezone.make_aware(datetime.combine(date, bh.end_time), tz)

    step = timedelta(minutes=bh.slot_minutes)
    duration = timedelta(minutes=servico.duracao)

    slots = []
    current = day_start
    while current + duration <= day_end:
        ok, _ = is_slot_available(servico, current)
        if ok:
            slots.append(current.isoformat())
        current += step

    return JsonResponse({"slots": slots})

def staff_required(user):
    # se você quiser apenas staff/admin
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(staff_required)
def calendario_admin_view(request):
    """
    Renderiza a página do calendário para o admin.
    """
    return render(request, "admin_calendario.html")


@login_required
@user_passes_test(staff_required)
def agendamentos_eventos_json(request):

    start_str = request.GET.get("start")
    end_str = request.GET.get("end")

    start_dt = parse_datetime(start_str) if start_str else None
    end_dt = parse_datetime(end_str) if end_str else None

    # Garante timezone-aware
    tz = timezone.get_current_timezone()
    if start_dt and timezone.is_naive(start_dt):
        start_dt = timezone.make_aware(start_dt, tz)
    if end_dt and timezone.is_naive(end_dt):
        end_dt = timezone.make_aware(end_dt, tz)

    qs = Agendamento.objects.filter(
    ).select_related("servico").order_by("inicio_data_hora")

    # filtra pelo range solicitado pelo calendário
    if start_dt and end_dt:
        qs = qs.filter(
            inicio_data_hora__lt=end_dt,
            fim_data_hora__gt=start_dt,
        )

    # Monte os eventos
    events = []
    for ag in qs:
        # título
        title = f"{ag.servico.nome} • {ag.placa}"

        # cores por status
        if ag.status == "scheduled":
            color = "#0d6efd"  # azul bootstrap
        elif ag.status == "completed":
            color = "#198754"  # verde
        elif ag.status == "canceled":
            color = "#dc3545"  # vermelho
        else:
            color = "#6c757d"  # cinza

        events.append({
            "id": ag.id,
            "title": title,
            "start": ag.inicio_data_hora.isoformat(),
            "end": ag.fim_data_hora.isoformat() if ag.fim_data_hora else None,
            "color": color,
            "extendedProps": {
                "placa": ag.placa,
                "servico": ag.servico.nome,
                "status": ag.status,
                "inicio": timezone.localtime(ag.inicio_data_hora).strftime("%d/%m/%Y %H:%M"),
                "fim": timezone.localtime(ag.fim_data_hora).strftime("%d/%m/%Y %H:%M") if ag.fim_data_hora else "",
                "valor": str(ag.servico.valor) if hasattr(ag.servico, "valor") else "",
            }
        })

    return JsonResponse(events, safe=False)

@require_POST
def atualizar_status_agendamento(request, ag_id):
    # Evita redirect HTML: verifique auth e retorne JSON
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "Não autenticado."}, status=401)

    ag = get_object_or_404(Agendamento, pk=ag_id)

    status = request.POST.get("status")
    if status is None and request.content_type == "application/json":
        import json
        try:
            payload = json.loads(request.body or "{}")
            status = payload.get("status")
        except Exception:
            return HttpResponseBadRequest("JSON inválido")

    allowed = dict(Agendamento.STATUS_CHOICES).keys()
    if status not in allowed:
        return JsonResponse({"ok": False, "error": "Status inválido."}, status=400)

    ag.status = status
    ag.save(update_fields=["status"])

    return JsonResponse({"ok": True})
