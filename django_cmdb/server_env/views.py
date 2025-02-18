from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import ServerEnv
from .serializers import ServerEnvSerializer

# Create your views here.


class ServerEnvs(APIView):
    def get(self, request):
        all_serverenv = ServerEnv.objects.all()
        serializer = ServerEnvSerializer(all_serverenv, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ServerEnvSerializer(data=request.data)
        if serializer.is_valid():
            ServerEnv = serializer.save()
            return Response(
                ServerEnvSerializer(ServerEnv).data,
            )
        else:
            return Response(serializer.errors)


class ServerEnvDetail(APIView):
    def get_objects(self, pk):
        print(pk)
        try:
            return ServerEnv.objects.get(pk=pk)
        except ServerEnv.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        ServerEnv = self.get_objects(pk)
        serializer = ServerEnvSerializer(ServerEnv)
        return Response(serializer.data)

    def put(self, request, pk):
        ServerEnv = self.get_objects(pk)
        serializer = ServerEnvSerializer(
            ServerEnv,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            update_serializer = serializer.save()
            return Response(
                ServerEnvSerializer(update_serializer).data,
            )
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        ServerEnv = self.get_objects(pk)
        ServerEnv.delete()
        return Response(status=HTTP_204_NO_CONTENT)
