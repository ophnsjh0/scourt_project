from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import NetworkVm
from .serializers import NetworkVmSerializer

# Create your views here.


class NetworkVms(APIView):
    def get(self, request):
        all_networkvm = NetworkVm.objects.all()
        serializer = NetworkVmSerializer(all_networkvm, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = NetworkVmSerializer(data=request.data)
        if serializer.is_valid():
            NetworkVm = serializer.save()
            return Response(
                NetworkVmSerializer(NetworkVm).data,
            )
        else:
            return Response(serializer.errors)


class NetworkVmDetail(APIView):
    def get_objects(self, pk):
        print(pk)
        try:
            return NetworkVm.objects.get(pk=pk)
        except NetworkVm.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        NetworkVm = self.get_objects(pk)
        serializer = NetworkVmSerializer(NetworkVm)
        return Response(serializer.data)

    def put(self, request, pk):
        NetworkVm = self.get_objects(pk)
        serializer = NetworkVmSerializer(
            NetworkVm,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            update_serializer = serializer.save()
            return Response(
                NetworkVmSerializer(update_serializer).data,
            )
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        NetworkVm = self.get_objects(pk)
        NetworkVm.delete()
        return Response(status=HTTP_204_NO_CONTENT)
