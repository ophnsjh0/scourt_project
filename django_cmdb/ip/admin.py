from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import path
from .models import Ip
from .forms import ExcelUploadForm
import pandas as pd

# Register your models here.

@admin.action(description="Upload File")
def upload_excel(modeladmin, request, queryset):
    if request.method == "POST":
        if 'apply' in request.POST:
            excel_file = request.FILES['excel_file']
            sheet_name = request.POST.get('sheet_name')
            
            try:
                df = pd.read_excel(excel_file, sheet_name=sheet_name, engine='opnpyxl')
                
                for _, row in df.iterrows():
                    print(row['vrf'])
                    Ip.objects.update_or_create(
                        vrf=row['vrf'],
                        network=row['network'],
                        ip=row['ip'],
                        mac=row['mac'],
                        node=row['node'],
                        interface=row['interface'],
                        host=row['host'],
                        connect=row['connect'],
                    )
                messages.success(request, "Excel File Uploaded Successfully")
            except Exception as e:
                messages.error(request, f"Error Processing file: {e}")
            return redirect('..')
        
    form = ExcelUploadForm()
    return render(request, 'ip/excel_upload.html', {'form': form})

@admin.register(Ip)
class IpAdmin(admin.ModelAdmin):
    list_display = ('vrf', 'network', 'ip', 'mac', 'node', 'interface', 'host', 'connect')
    list_filter = ('vrf', 'network', 'node', 'connect')
    search_fields = ('ip', 'mac', 'host', 'node', 'network', 'connect')
    action = [upload_excel]
    
    def chagelist_view(self, request, extra_context=None):
        if request.method == "POST":
            if 'apply' in request.POST or request.POST['action'] !='delete_selected':
                return upload_excel(self, request, None)
        return super().chagelist_view(request, extra_context)
