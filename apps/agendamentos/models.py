from datetime import timedelta
from django.db import models
from apps.servicos.models import Servico

# Create your models here.
class Agendamento(models.Model):

    STATUS_CHOICES = (
        ('scheduled', 'Agendado'),
        ('canceled', 'Cancelado'),
        ('completed', 'Concluído'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    placa = models.CharField(max_length=8)
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    inicio_data_hora = models.DateTimeField()
    fim_data_hora = models.DateTimeField(blank=True)
    
    def save(self, *args, **kwargs):
        # Calcula o horário final automaticamente
        if not self.fim_data_hora:
            self.fim_data_hora = self.inicio_data_hora + timedelta(
                minutes=self.servico.duracao
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.placa} - {self.inicio_data_hora.strftime('%d/%m %H:%M')} ate {self.fim_data_hora.strftime('%d/%m %H:%M')}"