from django.db import models
from common.models import CommonModel

# Create your models here.

class NetworkEnv(CommonModel):

    class AreaChoices(models.TextChoices):
        OPERATION = ("운영", "운영")
        DEVELOPMENT = ("개발", "개발")
        VERIFICATION = ("검증", "검증")

    class CategoryChoice(models.TextChoices):
        L2SWITCH = ("L2스위치", "L2스위치")
        L3SWITCH = ("L3스위치", "L3스위치")
        L4SWITCH = ("L4스위치", "L4스위치")
        VHOST = ("가상화호스트", "가상화호스트")

    area = models.CharField(max_length=50, choices=AreaChoices.choices,)
    category = models.CharField(max_length=50, choices=CategoryChoice.choices,)
    khost = models.CharField(max_length=300, default='')
    host = models.CharField(max_length=100, default='')
    ip = models.ManyToManyField(
        "ip.Ip",
        blank= True,
    )
    vendor = models.CharField(max_length=100, default='')
    model = models.CharField(max_length=100, default='')
    serial = models.CharField(max_length=100, default="")
    os = models.CharField(max_length=100, default="")
    rack = models.ForeignKey(
        'rack.Rack',
        null = True,
        blank = True,
        on_delete=models.SET_NULL,
    )
    
    def __str__(self) -> str:
        return self.host
