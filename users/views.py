from users.serializers import RegisterSerializer
from rest_framework.permissions import AllowAny

from rest_framework import generics


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
