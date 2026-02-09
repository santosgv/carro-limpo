from django import forms
from .models import Agendamento
from apps.servicos.models import Servico
import re

class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['placa', 'servico', 'inicio_data_hora']
        widgets = {
            'placa': forms.TextInput(attrs={
                'class': 'form-control form-control-lg', 
                'placeholder': 'ABC1234',
                'style': 'text-transform: uppercase;'
            }),
            'servico': forms.Select(attrs={'class': 'form-select form-select-lg'}),
                        'inicio_data_hora': forms.DateTimeInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'type': 'datetime-local'
                },
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def clean_placa(self):
        placa = self.cleaned_data.get('placa').upper()
        # Regex simples para validar padrão antigo e Mercosul
        if not re.match(r'^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$', placa):
            # Se não quiser ser rígido no MVP, pode remover essa validação
            pass 
        return placa