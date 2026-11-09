from rest_framework import serializers


class MessageRequestSerializer(serializers.Serializer):
    message = serializers.CharField()
    lat = serializers.FloatField(required=False, allow_null=True)
    lon = serializers.FloatField(required=False, allow_null=True)
    is_point = serializers.BooleanField(required=False, allow_null=True)
    language = serializers.CharField(required=False, allow_null=True, default="en")


class MessageResponseSerializer(serializers.Serializer):
    response = serializers.CharField()
    ward = serializers.CharField(allow_null=True)
