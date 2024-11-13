from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from .models import Cliente, Comercial, Pedido
from .serializers import ClienteSerializer, ComercialSerializer, PedidoSerializer
from django.http import JsonResponse
from .models import Comercial
import json
import bcrypt

class ClienteListCreate(generics.ListCreateAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class ClienteRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class ComercialListCreate(generics.ListCreateAPIView):
    queryset = Comercial.objects.all()
    serializer_class = ComercialSerializer

class ComercialRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comercial.objects.all()
    serializer_class = ComercialSerializer

class PedidoListCreate(generics.ListCreateAPIView):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

class PedidoRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    
class ComercialLogin(APIView):
    def post(self, request):
        nombre = request.data.get('nombre')
        password = request.data.get('password')

        # Verifica que se proporcionen ambos campos
        if not nombre or not password:
            return Response({"error": "Nombre y contraseña son requeridos"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Busca el comercial por el nombre
            comercial = Comercial.objects.get(nombre=nombre)
            comercial_data = {
                    "id": comercial.id,
                    "nombre": comercial.nombre,
                    "apellido1": comercial.apellido1,
                    "apellido2": comercial.apellido2
                }
            
            # Verifica la contraseña
            if comercial.check_password(password):
                return Response({"success": "Autenticación exitosa","comercial": comercial_data}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Contraseña incorrecta"}, status=status.HTTP_401_UNAUTHORIZED)
        
        except Comercial.DoesNotExist:
            return Response({"error": "El comercial no existe"}, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
def get_comercial_id(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')
            password = data.get('password')
            
            # Busca el Comercial por nombre
            comercial = Comercial.objects.get(nombre=nombre)
            
            # Verifica la contraseña
            if comercial.check_password(password):
                return JsonResponse({'id': comercial.id}, status=200)
            else:
                return JsonResponse({'error': 'Contraseña incorrecta'}, status=400)
        except Comercial.DoesNotExist:
            return JsonResponse({'error': 'Comercial no encontrado'}, status=404)
        except KeyError:
            return JsonResponse({'error': 'Nombre y contraseña son requeridos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
