from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .messages import post_message
from .serializers import MessageRequestSerializer, MessageResponseSerializer


@extend_schema(
    responses=inline_serializer(
        name="HealthResponse", fields={"message": serializers.CharField()}
    )
)
@api_view(["GET"])
def health(request):
    return Response({"message": "pong"})


@extend_schema(request=MessageRequestSerializer, responses=MessageResponseSerializer)
@api_view(["POST"])
def messages(request):
    serializer = MessageRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(post_message(serializer.validated_data))
