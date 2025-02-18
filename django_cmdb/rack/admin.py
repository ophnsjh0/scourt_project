from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import path
from .models import Rack
from datacenter.models import Datacenter
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
                    datacenter_name = row['datacenter']
                    datacenter, _ = Datacenter.objects.get_or_create(name=datacenter_name)

                    Rack.objects.update_or_create(
                        defaults={
                            "datacenter": datacenter,
                        },
                        name=row["name"],
                        location=row["location"],
                        racktype=row["racktype"],
                        size=row["size"],
                        phase=row['phase'],
                        voltage=row['voltage'],
                        current=row['current'],
                        pdu_count=row['pdu_count'],
                        a_panel=row['a_panel'],
                        b_panel=row['b_panel'],
                        part=row['part'],
                        job=row['job']
                    )

                messages.success(request, "Excel File Uploaded Successfully")
            except Exception as e:
                messages.error(request, f"Error Processing file: {e}")
            return redirect("..")

    form = ExcelUploadForm()
    return render(request, "rack/excel_upload.html", {"form": form})


@admin.register(Rack)
class RackAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "part", "job")
    list_filter = ("datacenter", "location", "part", "job")
    search_fields = ("name", "location", "part", "job")
    action = [upload_excel]

    def chagelist_view(self, request, extra_context=None):
        if request.method == "POST":
            if "apply" in request.POST or request.POST["action"] != "delete_selected":
                return upload_excel(self, request, None)
        return super().chagelist_view(request, extra_context)
