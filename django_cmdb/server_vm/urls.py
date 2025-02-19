from django.urls import path
from . import views

urlpatterns = [
    path("", views.ServerVmd.as_view()),
    path("<int:pk>", views.ServerVmDetail.as_view()),
]
