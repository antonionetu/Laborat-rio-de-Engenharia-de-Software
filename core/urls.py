from django.urls import path
from . import views

urlpatterns = [
    path('api/admin/entrega/add/auto-complete-endereco/<int:cliente_id>/', views.get_endereco_cliente, name='get_endereco_cliente'),
]