from django.urls import path
from . import views

urlpatterns = [
    path("", views.Racks.as_view()),
    path("<int:pk>", views.RackDetail.as_view()),
]
