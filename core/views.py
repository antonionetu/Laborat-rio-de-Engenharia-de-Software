from django.http import JsonResponse
from .models import Cliente

def get_endereco_cliente(request, cliente_id):
    print(cliente_id)
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        return JsonResponse({'endereco': cliente.endereco})
        
    except Cliente.DoesNotExist:
        return JsonResponse({'endereco': ''})
