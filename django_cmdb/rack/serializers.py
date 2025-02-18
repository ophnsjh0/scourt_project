from rest_framework.serializers import ModelSerializer
from .models import Rack


class RackSerializer(ModelSerializer):

    class Meta:
        model = Rack
        fields = "__all__"
        depth = 1
