from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path
from .models import Datacenter
import pandas as pd

# Register your models here.

@admin.register(Datacenter)
class DatacenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'address', 'role')
    list_filter = ('name', 'location', 'address', 'role')
    
    