from time import timezone
from django.urls import reverse
from django.http.response import HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, View, TemplateView, DeleteView
from .utils import pode_abrir_caixa
from apps.faturas.models import Fatura
from carro_limpo.helper import error_response, ADD
from django.contrib import messages 
from .models import Caixa, Transacao
from .forms import TransacaoForm, CaixaFecharForm
from .helper import buscar_caixa_atual, caixa_as_dict


# caixa
class CaixaView(LoginRequiredMixin, TemplateView):
    template_name = "caixa.html"

    def get_context_data(self, **kwargs):
        context = super(CaixaView, self).get_context_data(**kwargs)
        _cache = Caixa.objects.filter(user=self.request.user)
        context['fluxo_caixa'] = _cache.filter(aberto=False)
        context['caixa'] = _cache.filter(aberto=True).first()
        return context


class CaixaAbrirView(LoginRequiredMixin, FormView):
    form_class = TransacaoForm
    template_name = "blank.html"
    
    def form_valid(self, form):

            # Verifica se o usuário pode abrir um caixa
        resultado = pode_abrir_caixa(self.request.user)
        if not resultado['pode_abrir']:
            for erro in resultado['erros']:
                messages.error(self.request, erro['mensagem'])
            return HttpResponseRedirect(reverse("caixa"))
        # Cria caixa
        caixa = Caixa.objects.create(user=self.request.user)
        
        # Passa caixa como argumento para save()
        transacao = form.save(caixa=caixa)
        
        return HttpResponseRedirect(reverse("caixa"))


class CaixaGetDataView(LoginRequiredMixin, View):
    def get(self, request):
        caixa = buscar_caixa_atual(request.user)
        return JsonResponse(caixa_as_dict(caixa), status=200)


class CaixaFecharView(LoginRequiredMixin, FormView):
    form_class = CaixaFecharForm  # Certifique-se que este form NÃO é um TransacaoForm
    template_name = "blank.html"

    def get(self, request, *args, **kwargs):
        """Se acessar via GET, redireciona para o caixa"""
        return HttpResponseRedirect(reverse("caixa"))

    def form_valid(self, form):
        try:
            # Busca o caixa atual
            caixa = buscar_caixa_atual(self.request.user)
            if not caixa:
                return HttpResponseRedirect(reverse("caixa"))
            
            # Prepara dados do caixa
            caixa_dict = caixa_as_dict(caixa)

            # Contar número de clientes e serviços
            faturas = Fatura.objects.filter(transacao__caixa=caixa)
            numero_clientes = faturas.values('cliente').distinct().count() if faturas.exists() else 0
            numero_servicos = faturas.count() if faturas.exists() else 0

            # Diferença do saldo físico
            saldo_fisico = float(form.cleaned_data.get("saldo_fisico", 0))
            dif = saldo_fisico - caixa_dict.get("budget", 0)

            # Atualizar objeto caixa
            caixa.aberto = False
            caixa.diferenca = dif
            caixa.clientes = numero_clientes
            caixa.servicos = numero_servicos
            caixa.saldo = caixa_dict.get("budget", 0)
            caixa.receita = caixa_dict.get("totals", {}).get("inc", 0)
            caixa.despesa = caixa_dict.get("totals", {}).get("exp", 0)
            caixa.save()

            return HttpResponseRedirect(reverse("caixa"))

        except Exception as e:
            # Log do erro
            print(f"Erro ao fechar caixa: {str(e)}")
            return HttpResponseRedirect(reverse("caixa"))

    def form_invalid(self, form):
        """Formulário inválido"""
        print("Erros no formulário de fechamento:", form.errors)
        return HttpResponseRedirect(reverse("caixa"))


class CaixaDeleteAllView(LoginRequiredMixin, View):
    def post(self, request):
        caixa = buscar_caixa_atual(request.user)
        transacoes = Transacao.objects.filter(caixa=caixa)
        if transacoes.exists():
            transacoes.delete()
            return JsonResponse({"message": "Todas as transações do caixa \
                                 atual foram deletadas."}, status=200)
        else:
            return JsonResponse({"message": "O caixa já está vazio!"})


# transações
class TransacaoFormView(LoginRequiredMixin, FormView):
    form_class = TransacaoForm
    template_name = 'blank.html'

    def form_valid(self, form):
        _caixa = buscar_caixa_atual(self.request.user)
        if _caixa:
            obj = form.save(caixa=_caixa)

            return JsonResponse({"object": int(obj.id)}, status=201)
        return JsonResponse({"message": "erro: o caixa não encontrado"},
                            status=404)

    def form_invalid(self, form):
        return JsonResponse(error_response(form.errors, ADD), status=400)

class TransacaoDeleteView(LoginRequiredMixin, DeleteView):
    model = Transacao
    success_url = "/"
