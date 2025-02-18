from django.urls import path
from . import views

urlpatterns = [
    path("", views.NetworkVms.as_view()),
    path("<int:pk>", views.NetworkVmDetail.as_view()),
]
