from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import Ip
from .serializers import IpSerializer

# Create your views here.


class Ips(APIView):
    def get(self, request):
        all_ips = Ip.objects.all()
        serializer = IpSerializer(all_ips, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = IpSerializer(data=request.data)
        if serializer.is_valid():
            ip = serializer.save()
            return Response(
                IpSerializer(ip).data,
            )
        else:
            return Response(serializer.errors)


class IpDetail(APIView):
    def get_objects(self, pk):
        print(pk)
        try:
            return Ip.objects.get(pk=pk)
        except Ip.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        ip = self.get_objects(pk)
        serializer = IpSerializer(ip)
        return Response(serializer.data)

    def put(self, request, pk):
        ip = self.get_objects(pk)
        serializer = IpSerializer(
            ip,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            update_serializer = serializer.save()
            return Response(
                IpSerializer(update_serializer).data,
            )
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        ip = self.get_objects(pk)
        ip.delete()
        return Response(status=HTTP_204_NO_CONTENT)
