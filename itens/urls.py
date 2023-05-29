from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name="index"),
    path('em/', views.MercacologicaView.as_view(), name='mercadologica'),
    path('sp/', views.SomarPaesView.as_view(), name='somapaes'),
    path('ie/', views.ItensEmpresaView.as_view(), name='itensemp'),
    path('empresa/', views.EmpresaView.as_view(), name='empresa'),
]