from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import path
from .models import NetworkEnv
from rack.models import Rack
from ip.models import Ip
from .forms import ExcelUploadForm
import pandas as pd

# Register your models here.


@admin.action(description="Upload File")
def upload_excel(modeladmin, request, queryset):
    if request.method == "POST":
        if "apply" in request.POST:
            excel_file = request.FILES["excel_file"]
            sheet_name = request.POST.get("sheet_name")

            try:
                df = pd.read_excel(excel_file, sheet_name=sheet_name, engine="opnpyxl")

                for _, row in df.iterrows():
                    rack_name = row['rack']
                    rack, _ = Rack.objects.get_or_create(name=rack_name)

                    NetworkEnv.objects.update_or_create(
                        defaults={
                            'rack' : rack,
                        },
                        area=row['area'],
                        category=row['category'],
                        khost=row['khost'],
                        host=row['host'],
                        vendor=row['vendor'],
                        model=row['model'],
                        serial=row['serial'],
                        os=row['os'],
                    )
                    
                    network_env, _ = NetworkEnv.objects.get_or_create(host=row['host'])
                    ip_names = row['ip'].split(',') if pd.notna(row['ip']) else []
                    
                    ips = []
                    for ip_name in ip_names:
                        ip, _ = Ip.objects.get_or_create(ip=ip_name.strip())
                        ips.append(ip)
                        
                    network_env.ip.set(ips)

                messages.success(request, "Excel File Uploaded Successfully")
            except Exception as e:
                messages.error(request, f"Error Processing file: {e}")
            return redirect("..")

    form = ExcelUploadForm()
    return render(request, "networkenv/excel_upload.html", {"form": form})


@admin.register(NetworkEnv)
class NetworkEnvAdmin(admin.ModelAdmin):
    list_display = ('area', 'category', 'khost', 'host', 'vendor', 'model', 'rack')
    list_filter = ('area', 'category', 'vendor', 'model', 'rack')
    search_fields = ("area", "category", "khost", "host", "vendor", "model")
    action = [upload_excel]

    def chagelist_view(self, request, extra_context=None):
        if request.method == "POST":
            if "apply" in request.POST or request.POST["action"] != "delete_selected":
                return upload_excel(self, request, None)
        return super().chagelist_view(request, extra_context)
