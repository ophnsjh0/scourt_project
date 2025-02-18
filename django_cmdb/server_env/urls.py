from django.urls import path
from . import views

urlpatterns = [
    path("", views.ServerEnvs.as_view()),
    path("<int:pk>", views.ServerEnvDetail.as_view()),
]
