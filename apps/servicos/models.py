from django.db import models
from django.contrib.auth.models import User


class Servico(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50, default=None)
    duracao = models.PositiveIntegerField(default=60)
    valor = models.DecimalField(decimal_places=2, max_digits=12)

    def __str__(self):
        return self.nome
