from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import NetworkEnv
from .serializers import NetworkEnvSerializer

# Create your views here.


class NetworkEnvs(APIView):
    def get(self, request):
        all_networkenv = NetworkEnv.objects.all()
        serializer = NetworkEnvSerializer(all_networkenv, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = NetworkEnvSerializer(data=request.data)
        if serializer.is_valid():
            NetworkEnv = serializer.save()
            return Response(
                NetworkEnvSerializer(NetworkEnv).data,
            )
        else:
            return Response(serializer.errors)


class NetworkEnvDetail(APIView):
    def get_objects(self, pk):
        print(pk)
        try:
            return NetworkEnv.objects.get(pk=pk)
        except NetworkEnv.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        NetworkEnv = self.get_objects(pk)
        serializer = NetworkEnvSerializer(NetworkEnv)
        return Response(serializer.data)

    def put(self, request, pk):
        NetworkEnv = self.get_objects(pk)
        serializer = NetworkEnvSerializer(
            NetworkEnv,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            update_serializer = serializer.save()
            return Response(
                NetworkEnvSerializer(update_serializer).data,
            )
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        NetworkEnv = self.get_objects(pk)
        NetworkEnv.delete()
        return Response(status=HTTP_204_NO_CONTENT)
