from django.urls import path
from . import views

urlpatterns = [
    path("", views.NetworkEnvs.as_view()),
    path("<int:pk>", views.NetworkEnvDetail.as_view()),
]
