from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, viewsets
from my_methods.auth import check_login
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.settings import CUSTOM_ACCESS_TOKEN_NAME
from ticket.models import *
from ticket.serializers import *


class TicketAPIView(APIView):
    def get(self, request):
        user = check_login(request)
        if user[0]:
            user = user[1]
        elif user[1] == 'Invalid token':
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
        elif user[1] == 'Token expired':
            return Response("Token expired", status=status.HTTP_400_BAD_REQUEST)
        elif user[1] == 'Access Token Required':
            return Response("Access Token Required", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
        if user.role != 'superuser' and user.role != 'ticket_admin':
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
        tickets = Ticket.objects.all()
        if not tickets:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)
