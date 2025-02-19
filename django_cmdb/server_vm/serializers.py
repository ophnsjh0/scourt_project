from rest_framework.serializers import ModelSerializer
from .models import ServerVm


class ServerVmSerializer(ModelSerializer):

    class Meta:
        model = ServerVm
        fields = "__all__"
        depth = 1
