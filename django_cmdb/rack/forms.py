from django import forms


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()
    sheet_name = forms.CharField(
        max_length=255, help_text="Enter the sheet name to import data from."
    )
