from django.db import models

# Create your models here.

class CommonModel(models.Model):
    created_at = models.DataField(auto_now_add=True)
    updated_at = models.DataField(auto_now=True)
    
    class Meta:
        abstract = True
        
        