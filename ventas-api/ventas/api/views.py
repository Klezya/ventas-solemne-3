from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Cliente, Comercial, Pedido
from .serializers import ClienteSerializer, ComercialSerializer, PedidoSerializer
from django.core.mail import send_mail
from django.conf import settings  # Para acceder a las configuraciones de correo
import json


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

    def perform_create(self, serializer):
        # Crear el pedido en la base de datos
        pedido = serializer.save()
        
        # Llamar a la función para enviar correo de confirmación
        self.enviar_correo_confirmacion(pedido)

    def enviar_correo_confirmacion(self, pedido):
        # Obtener detalles del pedido
        cliente = pedido.cliente
        comercial = pedido.comercial
        total = pedido.total

        # Configurar el mensaje del correo
        asunto = "Confirmación de Compra"
        cuerpo = (
            f"Estimado {cliente.nombre} {cliente.apellido1},\n\n"
            f"Su pedido ha sido registrado exitosamente.\n\n"
            f"Detalles del Pedido:\n"
            f"- Comercial: {comercial.nombre} {comercial.apellido1}\n"
            f"- Total: ${total}\n\n"
            "Gracias por su compra."
        )

        # Enviar el correo usando send_mail de Django
        try:
            send_mail(
                subject=asunto,
                message=cuerpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONFIRMATION_EMAIL_RECIPIENT],
                fail_silently=False,
            )
            print("Correo de confirmación enviado exitosamente.")
        except Exception as e:
            print("Error al enviar el correo de confirmación:", e)


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
                return Response({"success": "Autenticación exitosa", "comercial": comercial_data}, status=status.HTTP_200_OK)
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

class PedidosPorComercialView(generics.ListAPIView):
    serializer_class = PedidoSerializer

    def get_queryset(self):
        id_comercial = self.kwargs['id_comercial']
        return Pedido.objects.filter(comercial_id=id_comercial)


