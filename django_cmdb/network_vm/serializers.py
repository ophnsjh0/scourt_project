from rest_framework.serializers import ModelSerializer
from .models import NetworkVm


class NetworkVmSerializer(ModelSerializer):

    class Meta:
        model = NetworkVm
        fields = "__all__"
        depth = 1
