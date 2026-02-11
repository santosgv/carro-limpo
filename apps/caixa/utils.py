from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Caixa

def pode_abrir_caixa(user):
    """Verifica se o usuário pode abrir um caixa"""
    erros = []
    
    # Verifica caixa aberto
    if Caixa.objects.filter(user=user, aberto=True).exists():
        caixa = Caixa.objects.filter(user=user, aberto=True).first()
        erros.append({
            'tipo': 'caixa_aberto',
            'mensagem': f'Você já possui um caixa aberto (ID: {caixa.id}).',
            'caixa_id': caixa.id
        })
    
    # Verifica caixa na data de hoje
    hoje = timezone.now().date()
    if Caixa.objects.filter(user=user, data=hoje).exists():
        caixa = Caixa.objects.filter(user=user, data=hoje).first()
        erros.append({
            'tipo': 'caixa_hoje',
            'mensagem': f'Já existe um caixa registrado para hoje.',
            'caixa_id': caixa.id,
            'data': hoje
        })
    
    return {
        'pode_abrir': len(erros) == 0,
        'erros': erros
    }
