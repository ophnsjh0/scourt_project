from rest_framework.serializers import ModelSerializer
from .models import Datacenter

class DatacenterSerializer(ModelSerializer):
    
    class Meta:
        model = Datacenter
        fields = "__all__"


