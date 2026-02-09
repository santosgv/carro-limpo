from haystack import indexes

from .models import Servico


class ServicoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    nome = indexes.CharField(model_attr="nome")
    valor = indexes.DecimalField(model_attr="valor")
    duracao = indexes.DecimalField(model_attr="duracao")
    model_verbose = indexes.CharField(model_attr="_meta__verbose_name_plural")

    def get_model(self):
        return Servico

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
