
from datetime import datetime, time, timedelta
from django.shortcuts import render,redirect
from .models import Agendamento

from .forms import AgendamentoForm
from .models import Agendamento

def agendar_view(request):
    if request.method == 'POST':
        form = AgendamentoForm(request.POST)
        if form.is_valid():
            agendamento = form.save()
            
            # Lógica extra: Se a placa já estiver cadastrada em 'Cliente', 
            # você pode futuramente enviar um WhatsApp automático para o dono.
            # cliente_existe = Cliente.objects.filter(placa=agendamento.placa).first()
            
            return render(request, 'sucesso.html', {'agendamento': agendamento})
    else:
        form = AgendamentoForm()
    
    return render(request, 'agendar.html', {'form': form})