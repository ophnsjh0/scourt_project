from django.urls import path
from . import views

urlpatterns = [
    path("", views.Datacenters.as_view()),
    path("<int:pk>", views.DatacenterDetail.as_view()),
]