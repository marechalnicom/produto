from django.urls import path
from . import views

urlpatterns = [
    path('', views.itens, name="index"),
    path('em/', views.MercacologicaView.as_view(), name='mercadologica')
]