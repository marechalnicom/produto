from django.db import models

# Create your models here.
class Tag(models.Model):
    #mercadologica = models.ManyToManyField(Mercadologica, blank=True)
    tipo = models.CharField(max_length=50)
    tag = models.CharField(max_length=50)
    detalhe = models.CharField(max_length=50)
    def __str__(self) -> str:
        return f'{self.tipo}: {self.tag}'

class Mercadologica(models.Model):
    codigo = models.CharField('Código de Referencia', max_length=15)
    superior = models.BigIntegerField('Código do Superior', null=True, blank=True)
    descricao = models.CharField('Descrição', max_length=50)
    parametro = models.BigIntegerField('Margem Parametro', null=True, blank=True)
    decimo = models.IntegerField('Ultimo Número', null=True, blank=True)
    ncm = models.CharField('NCM de referencia', max_length=8, null=True, blank=True)
    tag = models.ManyToManyField(Tag, blank=True)
    def __str__(self):
        if self.superior==0:
            return f"{self.descricao}"
        else:
            sup=Mercadologica.objects.filter(id=self.superior)
            return f"{sup[0]} > {self.codigo} {self.descricao}"

class Item(models.Model):
    descricao = models.CharField('Descrição', max_length=50)
    barras = models.CharField('Código de Barras', max_length=15, null=True, blank=True)
    ativo = models.BooleanField(default=True)
    composicao = models.BooleanField(default=False)
    ncm = models.CharField('NCM', max_length=8, null=True, blank=True)
    classificacao = models.ForeignKey(Mercadologica, on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ManyToManyField(Tag, blank=True)
    def __str__(self) -> str:
        return self.descricao

class Empresa(models.Model):
    rs = models.CharField('Razão Social', max_length=100)
    cnpj = models.CharField("CNPJ", max_length=18, unique=True)
    fantasia = models.CharField(max_length=100)
    tag = models.ManyToManyField(Tag, blank=True)
    def __str__(self) -> str:
        return f'{self.rs} - {self.cnpj}'

class ItemEmpresa(models.Model):
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    codigo = models.BigIntegerField('Código', null=True, blank=True)
    descricao = models.CharField('Descrição', max_length=50)
    barras = models.CharField('Código de Barras', max_length=15)
    ativo = models.BooleanField(default=True)
    composicao = models.BooleanField(default=False)
    ncm = models.CharField('NCM', max_length=8, null=True, blank=True)
    classificacao = models.ForeignKey(Mercadologica,verbose_name='Classificação Mercadologica', on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ManyToManyField(Tag, blank=True)
    def __str__(self) -> str:
        return self.descricao
    
