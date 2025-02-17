from django.urls import path
from . import views

urlpatterns = [
    path("", views.Ips.as_view()),
    path("<int:pk>", views.IpDetail.as_view()),
]
