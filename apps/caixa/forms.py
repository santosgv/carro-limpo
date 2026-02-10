from django import forms

from .models import Transacao


class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = ('value', 'description', 'type')
    
    def __init__(self, *args, **kwargs):
        self.caixa = kwargs.pop('caixa', None)  # Remove caixa dos kwargs
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True, caixa=None):
        """Salva com caixa opcional no parâmetro ou no __init__"""
        _obj = super().save(commit=False)
        
        # Usa caixa do parâmetro ou do __init__
        if caixa:
            _obj.caixa = caixa
        elif self.caixa:
            _obj.caixa = self.caixa
        # Se não tiver caixa, lança erro
        else:
            raise ValueError("É necessário fornecer um caixa para salvar a transação")
        
        if commit:
            _obj.save()
        
        return _obj


class CaixaFecharForm(forms.Form):
    saldo_fisico = forms.DecimalField(max_digits=10, decimal_places=2)
