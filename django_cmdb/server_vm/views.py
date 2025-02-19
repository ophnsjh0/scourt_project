from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import ServerVm
from .serializers import ServerVmSerializer

# Create your views here.


class ServerVms(APIView):
    def get(self, request):
        all_networkvm = ServerVm.objects.all()
        serializer = ServerVmSerializer(all_networkvm, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ServerVmSerializer(data=request.data)
        if serializer.is_valid():
            ServerVm = serializer.save()
            return Response(
                ServerVmSerializer(ServerVm).data,
            )
        else:
            return Response(serializer.errors)


class NetworkVmDetail(APIView):
    def get_objects(self, pk):
        print(pk)
        try:
            return ServerVm.objects.get(pk=pk)
        except ServerVm.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        ServerVm = self.get_objects(pk)
        serializer = ServerVmSerializer(NetworkVm)
        return Response(serializer.data)

    def put(self, request, pk):
        ServerVm = self.get_objects(pk)
        serializer = ServerVmSerializer(
            ServerVm,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            update_serializer = serializer.save()
            return Response(
                ServerVmSerializer(update_serializer).data,
            )
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        ServerVm = self.get_objects(pk)
        ServerVm.delete()
        return Response(status=HTTP_204_NO_CONTENT)
