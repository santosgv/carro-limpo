from django.db import models


class Servico(models.Model):
    nome = models.CharField(max_length=50, default=None)
    duracao = models.PositiveIntegerField(default=60)
    valor = models.DecimalField(decimal_places=2, max_digits=12)

    def __str__(self):
        return self.nome
