from django.db import models
from common.models import CommonModel

# Create your models here.
 
class Rack(CommonModel):
    
    class LocationChoices(models.TextChoices):
        BDEAST = ("분당3층동관", "분당3층동관")
        BDWEST = ("분당3층서관", "분당3층서관")
        BDSOUTH = ("분당3층중간방", "분당3층중간방")
        SJ3F = ("세종3층", "세종3층")
        SJ4F = ("세종4층", "세종4층")
        
    class RackTypeChoices(models.TextChoices):
        STANDARD = ("표준", "표준")
        CUSTOM = ("전용", "전용")
    
    class PartChoices(models.TextChoices):
        SYSTEM = ("시스템", "시스템")
        WINDOW = ("윈도우", "윈도우")
        VDI = ("VDI", "VDI")
        MORNITOR = ("관제", "관제")
        NETWORK = ("네트워크", "네트워크")
        SECURITY = ("정보보안", "정보보안")
        COMMUNICATION = ("통신망", "통신망")
        
    class JobChoices(models.TextChoices):
        SCOOURT = ("사법", "사법")
        IROS = ("등기", "등기")
        FAMILY = ("가족", "가족")
        CYBER = ("사이버보안", "사이버보안")
        
    datacenter = models.ForeignKey(
        'datacenter.Datacenter',
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=100, choices=LocationChoices.choices)
    racktype = models.CharField(max_length=200, choices=RackTypeChoices.choices)
    size = models.CharField(max_length=50)
    phase = models.CharField(max_length=50)
    voltage = models.CharField(max_length=50)
    current = models.CharField(max_length=50)
    pdu_count = models.IntegerField(null=True)
    a_panel = models.CharField(max_length=100)
    b_panel = models.CharField(max_length=100)
    part = models.CharField(max_length=50, choices=PartChoices.choices,)
    job = models.CharField(max_length=50, choices=JobChoices.choices,)
    
    def __str__(self) -> str:
        return self.name

