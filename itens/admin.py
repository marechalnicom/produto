from django.contrib import admin
from .models import Item, Mercadologica, Empresa, ItemEmpresa, Tag

# Register your models here.
admin.site.register(Mercadologica)
admin.site.register(Item)
admin.site.register(Empresa)
admin.site.register(ItemEmpresa)
admin.site.register(Tag)