from django import forms
from mapwidgets.widgets import GooglePointFieldWidget, GoogleStaticOverlayMapWidget
from .models import *
from django.contrib.gis.forms import PointField


FIRST_WIDGET_SETTINGS = {
    "MapboxPointFieldWidget": (
        ("zoom", 15),
        ("mapCenterLocation", [60.7177013, -22.6300491]),
    ),
}

class RecordForm(forms.ModelForm):
    #location_has_default = PointField(widget=MapboxPointFieldWidget(settings=FIRST_WIDGET_SETTINGS))
    class Meta:
        model = Record
        fields = ("startPlace", "endPlace")
        widgets = {
            'startPlace': GooglePointFieldWidget,
            'endPlace': GooglePointFieldWidget,
        }
