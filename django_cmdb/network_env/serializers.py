from rest_framework.serializers import ModelSerializer
from .models import NetworkEnv


class NetworkEnvSerializer(ModelSerializer):

    class Meta:
        model = NetworkEnv
        fields = "__all__"
        depth = 1 
