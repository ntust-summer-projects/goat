from django.contrib.gis import admin
from mainsite.models import *
from django.contrib.gis.db import models
from mapwidgets.widgets import MapboxPointFieldWidget
# Register your models here.
'''
@admin.register(User)
class UserAdmin(admin.GISModelAdmin):
    list_display = ('name','email','phone')

@admin.register(Record)
class TRecordAdmin(admin.GISModelAdmin):
    list_display = ('user','start','end','routeLength')
    formfield_overrides = {
        models.PointField: {"widget": MapboxPointFieldWidget}
    }
    
@admin.register(Company)
class CompanyAdmin(admin.GISModelAdmin):
    list_display = ('vatNumber','name','email','phone')'''
    
@admin.register(Product)
class ProductAdmin(admin.GISModelAdmin):
    list_display = ('id','name','description','photo','carbonEmission','company')
    
@admin.register(Component)
class ComponentAdmin(admin.GISModelAdmin):
    list_display = ('id','product','material','weight','carbonEmission')

@admin.register(Material)
class MaterialAdmin(admin.GISModelAdmin):
    list_display = ('CName','EName','carbonEmission')
    
@admin.register(Transportation)
class TransportationAdmin(admin.GISModelAdmin):
    list_display = ('id','name','carbonEmission')

@admin.register(LogT)
class LogTAdmin(admin.GISModelAdmin):
    list_display = ('id','user','logType','carbonEmission','timestamp')
    
@admin.register(User)
class UserAdmin(admin.GISModelAdmin):
    list_display = ('id','username','email','phone')
    
@admin.register(LogTProfile)
class LogTProfileAdmin(admin.GISModelAdmin):
    list_display = ('log','distance','transportation')
    
@admin.register(AbstractLog)
class AbstractLogAdmin(admin.GISModelAdmin):
    list_display = ('id','user','logType','carbonEmission','timestamp')
    
@admin.register(LogI)
class LogIAdmin(admin.GISModelAdmin):
    list_display = ('id','user','logType','carbonEmission','timestamp')
    
@admin.register(LogIProfile)
class LogIProfileAdmin(admin.GISModelAdmin):
    list_display = ('log','product','amount')

    
admin.site.register(Company)