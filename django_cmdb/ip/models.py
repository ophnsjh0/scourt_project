from django.db import models
from common.models import CommonModel

# Create your models here.

class Ip(CommonModel):
    vrf = models.CharField(max_length=50, default='')
    network = models.CharField(max_length=50, default="")
    ip = models.CharField(max_length=50, default="", unique=True)
    mac = models.CharField(max_length=50, default="")
    node = models.CharField(max_length=50, default="")
    interface = models.CharField(max_length=50, default="")
    host = models.CharField(max_length=50, default="")
    connect = models.CharField(max_length=50, default="")
    
    def __str__(self) -> str:
        return self.ip
    
    class Meta:
        verbose_name_plural = "IP"
