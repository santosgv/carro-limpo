from datetime import timedelta
from django.db import models
from django.forms import ValidationError
from apps.servicos.models import Servico
from django.db.models import Q


class BusinessHours(models.Model):
    weekday = models.IntegerField(
        choices=[
            (0, 'Segunda'),
            (1, 'Terça'),
            (2, 'Quarta'),
            (3, 'Quinta'),
            (4, 'Sexta'),
            (5, 'Sábado'),
            (6, 'Domingo'),
        ]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_closed = models.BooleanField(default=False)
    slot_minutes = models.PositiveIntegerField(default=15)

    class Meta:
        # SOLUÇÃO MAIS EXPLÍCITA: unique_together
        unique_together = ['weekday']  # Garante que cada dia aparece apenas uma vez

    def clean(self):
        if not self.is_closed and self.end_time <= self.start_time:
            raise ValidationError("Fim deve ser maior que Inicio")


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

    
    class Meta:
        indexes = [
            models.Index(fields=["inicio_data_hora"]),
            models.Index(fields=["fim_data_hora"]),
        ]


    
    def save(self, *args, **kwargs):
        if not self.fim_data_hora:
            self.fim_data_hora = self.inicio_data_hora + timedelta(
                minutes=self.servico.duracao
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.placa} - {self.inicio_data_hora.strftime('%d/%m %H:%M')} ate {self.fim_data_hora.strftime('%d/%m %H:%M')}"