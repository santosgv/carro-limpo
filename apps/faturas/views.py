from django.shortcuts import get_object_or_404, render
from django.http.response import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import Payload
from carro_limpo.views import UpdateViewJson
from apps.clientes.models import Cliente
from apps.servicos.models import Servico
from .models import Fatura
from .forms import FaturaForm
from io import BytesIO
import base64
import qrcode

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

    txid = f"FAT{id}{request.user.id}"[-25:]

    payload = Payload(
                nome=str(request.user.loja.nome[:17]),
                chavepix=str(request.user.loja.chave_pix),
                valor=f'{fatura.servico.valor:.2f}',
                cidade='Brasil',
                txtId=txid
            )
    string_pix = payload.gerarPayload(gerar_qrcode=False)

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(string_pix)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converte a imagem para base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    if not fatura.pago:
        _status = "Pendente"
        fatura.pago = True
        #fatura.save()
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
        "fatura_id": fatura.id,
        "string_pix": string_pix,
        "qr_code_base64": img_base64,
    }

    return render(request, "fatura_print.html", context)
