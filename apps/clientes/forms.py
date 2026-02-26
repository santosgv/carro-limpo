from django import forms

from .models import Cliente
from carro_limpo.forms import UserRequiredForm


class ClienteCreateForm(UserRequiredForm):
    class Meta:
        model = Cliente
        fields = ["nome", "telefone", "email", "documento", "placa", "marca",
                  "modelo", "cor","desconto",]
        exclude = ('user',)


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        exclude = ('user',)
