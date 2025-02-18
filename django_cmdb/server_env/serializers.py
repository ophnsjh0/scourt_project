from rest_framework.serializers import ModelSerializer
from .models import ServerEnv


class ServerEnvSerializer(ModelSerializer):

    class Meta:
        model = ServerEnv
        fields = "__all__"
        depth = 1
