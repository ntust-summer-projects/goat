from django.contrib.gis import admin
from mainsite.models import *
from django.contrib.gis.db import models
from mapwidgets.widgets import MapboxPointFieldWidget
# Register your models here.

@admin.register(User)
class UserAdmin(admin.GISModelAdmin):
    list_display = ('name','email','phone','wallet')

@admin.register(Record)
class RecordAdmin(admin.GISModelAdmin):
    list_display = ('user','start','end','routeLength')
    formfield_overrides = {
        models.PointField: {"widget": MapboxPointFieldWidget}
    }
    
@admin.register(Company)
class CompanyAdmin(admin.GISModelAdmin):
    list_display = ('vatNumber','name','email','phone')
    
@admin.register(Product)
class ProductAdmin(admin.GISModelAdmin):
    list_display = ('id','name','description','photo','carbonEmission','company')
    
@admin.register(Component)
class ComponentAdmin(admin.GISModelAdmin):
    list_display = ('id','product','material','weight','carbonEmission')

@admin.register(Material)
class MaterialAdmin(admin.GISModelAdmin):
    list_display = ('CName','EName','carbonEmission')

    
