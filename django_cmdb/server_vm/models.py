from django.db import models
from common.models import CommonModel

# Create your models here.

class ServerVm(CommonModel):
    class CategoryChoice(models.TextChoices):
        WINDOW = ("Windows Server(가상화)", "Windows Server(가상화)")
        LINUX = ("Linux Server(가상화)", "Linux Server(가상화)")
        UNIX = ("Unix Server(가상화)", "Unix Server(가상화)")

    category = models.CharField(max_length=50, choices=CategoryChoice.choices)
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
