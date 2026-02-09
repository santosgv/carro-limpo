
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.estatisticas.urls')),
    path('perfil/', include('apps.perfil.urls')),
    path('clientes/', include('apps.clientes.urls')),
    path('servicos/', include('apps.servicos.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('caixa/', include('apps.caixa.urls')),
    path('faturas/', include('apps.faturas.urls')),
    path('pesquisar/', include('apps.pesquisar.urls')),
    path('agendamento/', include('apps.agendamentos.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
