from django.db import models
from common.models import CommonModel

# Create your models here.

class ServerEnv(CommonModel):

    class AreaChoices(models.TextChoices):
        OPERATION = ("운영", "운영")
        DEVELOPMENT = ("개발", "개발")
        VERIFICATION = ("검증", "검증")

    class CategoryChoice(models.TextChoices):
        VIRTUAL_SERVER = ("물리 가상화 서버", "물리 가상화 서버")
        SINGLE_SERVER = ("서버", "서버")

    class SubCategoryChoice(models.TextChoices):
        VMWARE_SINGLE = ("단독VMware Server", "단독VMware Server")
        VMESTR_MILTI = ("다중복합VMware Server", "다중복합VMware Server")
        LINUX = ("Linux Server", "Linux Server")
        UNIX = ("Unix Server", "Unix Server")
        HCI = ("다중복합 플랫폼박스", "다중복합 플랫폼박스")
        
    area = models.CharField(max_length=50, choices=AreaChoices.choices)
    category = models.CharField(max_length=100, choices=CategoryChoice.choices)
    subcategory = models.CharField(max_length=100, choices=SubCategoryChoice.choices)
    khost = models.CharField(max_length=300, default='')
    host = models.CharField(max_length=100, default='')
    ip = models.ManyToManyField(
        "ip.Ip",
        null = True,
        blank = True,
    )
    vendor = models.CharField(max_length=100, default='')
    model = models.CharField(max_length=100, defualt='')
    serial = models.CharField(max_length=100, default='')
    os = models.CharField(max_length=100, default='')
    rack = models.ForeignKey(
        'rack.Rack',
        null = True,
        blank = True,
        on_delete=models.SET_NULL
    )
    
    def __str__(self) -> str:
        return self.host
