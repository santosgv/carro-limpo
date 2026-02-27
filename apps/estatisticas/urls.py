
from django.urls import path

from .views import EstatisticasView,vendas

urlpatterns = [
    path("", EstatisticasView.as_view(), name="home"),
    path("vendas/", vendas, name="vendas"),
]
