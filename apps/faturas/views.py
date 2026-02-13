from django.shortcuts import get_object_or_404, render
from django.http.response import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from carro_limpo.views import UpdateViewJson
from apps.clientes.models import Cliente
from apps.servicos.models import Servico
from .models import Fatura
from .forms import FaturaForm


# Create your views here.
class FaturaListarView(LoginRequiredMixin, ListView):
    template_name = "faturas.html"
    context_object_name = "faturas"

    def get_queryset(self):
        return Fatura.objects.all()

    def get_context_data(self, **kwargs):
        context = super(FaturaListarView, self).get_context_data(**kwargs)
        context['servicos'] = Servico.objects.all()
        context['clientes'] = Cliente.objects.all()
        return context


class FaturaFormView(LoginRequiredMixin, FormView):
    form_class = FaturaForm

    def form_valid(self, form):
        form.save(self.request.user)
        return HttpResponseRedirect(reverse("faturas"))


class FaturaDeleteView(LoginRequiredMixin, DeleteView):
    model = Fatura
    success_url = "/"


class FaturaUpdateView(LoginRequiredMixin, UpdateViewJson):
    model = Fatura
    fields = ['pago']
    success_url = "/"


@login_required
def gerar(request, id):
    fatura = get_object_or_404(Fatura, pk=id)

    if not fatura.pago:
        _status = "Pendente"
        fatura.pago = True
        fatura.save()
    else:
        _status = "Pago"

    context = {
        "cliente_nome": fatura.cliente.nome,
        "cliente_tel": fatura.cliente.telefone,
        "cliente_email": fatura.cliente.email,
        "cliente_documento": fatura.cliente.documento,
        "cliente_marca": fatura.cliente.marca,
        "cliente_modelo": fatura.cliente.modelo,
        "cliente_placa": fatura.cliente.placa,
        "servico_nome": fatura.servico.nome,
        "servico_valor": fatura.servico.valor,
        "loja_rs": request.user.loja.nome,
        "loja_tel": request.user.loja.telefone,
        "loja_cnpj": request.user.loja.cnpj,
        "loja_email": request.user.loja.email,
        "loja_endereco": str(request.user.endereco),
        "fatura_valor": fatura.servico.valor,
        "fatura_data": fatura.data,
        "fatura_status": _status,
        "fatura_id": fatura.id
    }

    return render(request, "fatura_print.html", context)
