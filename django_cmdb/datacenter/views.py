from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import Datacenter
from .serializers import DatacenterSerializer

# Create your views here.

class Datacenters(APIView):
    def get(self, request):
        all_center = Datacenter.objects.all()
        serializer = DatacenterSerializer(all_center, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = DatacenterSerializer(data=request.data)
        if serializer.is_valid():
            Datacenter = serializer.save()
            return Response(
                DatacenterSerializer(Datacenter).data,
            )
        else:
            return Response(serializer.errors)

class DatacenterDetail(APIView):
    def get_objects(self, pk):
        print(pk)
        try:
            return Datacenter.objects.get(pk=pk)
        except Datacenter.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        Datacenter = self.get_objects(pk)
        serializer = DatacenterSerializer(Datacenter)
        return Response(serializer.data)

    def put(self, request, pk):
        Datacenter = self.get_objects(pk)
        serializer = DatacenterSerializer(
            Datacenter,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            update_serializer = serializer.save()
            return Response(
                DatacenterSerializer(update_serializer).data,
            )
        else:
            return Response(serializer.errors)
        
    def delete(self, request, pk):
        Datacenter = self.get_objects(pk)
        Datacenter.delete()
        return Response(status=HTTP_204_NO_CONTENT)