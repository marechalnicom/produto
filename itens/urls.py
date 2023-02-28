from django.urls import path
from . import views

urlpatterns = [
    path('itens/', views.itens, name="itens"),
]