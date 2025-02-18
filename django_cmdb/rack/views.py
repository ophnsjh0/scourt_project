from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import Rack
from .serializers import RackSerializer

# Create your views here.


class Racks(APIView):
    def get(self, request):
        all_rack = Rack.objects.all()
        serializer = RackSerializer(all_rack, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RackSerializer(data=request.data)
        if serializer.is_valid():
            Rack = serializer.save()
            return Response(
                RackSerializer(Rack).data,
            )
        else:
            return Response(serializer.errors)


class RackDetail(APIView):
    def get_objects(self, pk):
        print(pk)
        try:
            return Rack.objects.get(pk=pk)
        except Rack.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        Rack = self.get_objects(pk)
        serializer = RackSerializer(Rack)
        return Response(serializer.data)

    def put(self, request, pk):
        NetworkVm = self.get_objects(pk)
        serializer = RackSerializer(
            Rack,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            update_serializer = serializer.save()
            return Response(
                RackSerializer(update_serializer).data,
            )
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        Rack = self.get_objects(pk)
        Rack.delete()
        return Response(status=HTTP_204_NO_CONTENT)
