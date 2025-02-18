from django.db import models
from common.models import CommonModel

# Create your models here.


class NetworkVm(CommonModel):

    class CategoryChoice(models.TextChoices):
        L2SWITCH = ("L2스위치", "L2스위치")
        L3SWITCH = ("L3스위치", "L3스위치")
        L4SWITCH = ("L4스위치", "L4스위치")

    category = models.CharField(
        max_length=50,
        choices=CategoryChoice.choices,
    )
    khost = models.CharField(max_length=300, default="")
    host = models.CharField(max_length=100, default="")
    ip = models.ManyToManyField(
        "ip.Ip",
        blank=True,
    )
    os = models.CharField(max_length=100, default="")
    uphost = models.ForeignKey(
        "network_env.NetworkEnv",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return self.host
