from django.db import models
from common.models import CommonModel

# Create your models here.

class Datacenter(CommonModel):
    
    class LocationChoices(models.TextChoices):
        BUNDANG = ("분당전산정보센터", "분당전산정보센터")
        SEJONG = ("세종등기정보센터", "세종등기정보센터")
        
    class RoleChoices(models.TextChoices):
        DATA = ("데이터센터", "데이터센터")
        BACKUP = ("백업센터", "백업센터")
        
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=50, choices=LocationChoices.choices,)
    address = models.TextChoices()
    role = models.CharField(max_length=50, choices=RoleChoices.choices,)
    
    def __str__(self) -> str:
        return self.name

