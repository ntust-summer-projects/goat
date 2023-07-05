#from django.db import models
from django.contrib.gis.db import models
import geopy.distance
from geopy.geocoders import Nominatim
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django_enumfield import enum
import requests
# Create your models here.

geolocator = Nominatim(user_agent="djangoTest, email = ian523411756@gmail.com")
geolocator.headers = {'Accept-Language': 'en'}

def getComponyName(vatNumber):
    url = f"https://data.gcis.nat.gov.tw/od/data/api/9D17AE0D-09B5-4732-A8F4-81ADED04B679?$format=json&$filter=Business_Accounting_NO eq { vatNumber }&$skip=0&$top=50"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            company_name = data[0]['Company_Name']
            return company_name
        except:
            pass
    return "Unknown"

class User(models.Model):
    name = models.CharField(max_length = 20, unique = True)
    passwd = models.CharField(max_length = 50)
    email = models.CharField(max_length = 50, unique = True)
    phone = models.CharField(max_length = 50, unique = True)
    wallet = models.PositiveBigIntegerField(editable = False,default = 0)

    def __str__(self):
        return self.name

class Record(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    startPlace = models.PointField()
    endPlace = models.PointField()
    routeLength = models.FloatField(editable = False)
    point = models.PositiveIntegerField(editable = False)
    dateTime = models.DateTimeField(auto_now_add = True,null = True)
    start = models.CharField(max_length = 200, null = True, editable = False)
    end = models.CharField(max_length = 200, null = True, editable = False)

    def getDistance(self):
        distance = self.startPlace.distance(self.endPlace)
        print((self.startPlace[1], self.startPlace[0]), (self.endPlace[1], self.endPlace[0]))
        return geopy.distance.geodesic((self.startPlace[1], self.startPlace[0]), (self.endPlace[1], self.endPlace[0])).km

    def save(self, *args, **kwargs):
        self.routeLength = self.getDistance()
        self.point = int(self.routeLength*10)
        self.start = geolocator.reverse((self.startPlace.y, self.startPlace.x)).address
        self.end = geolocator.reverse((self.endPlace.y, self.endPlace.x)).address
        self.user.wallet += self.point
        self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.name} from {self.start} to {self.end}, length = {self.routeLength} km, get {self.point} points."
    
class Company(models.Model):
    name = models.CharField(max_length = 20, editable = False, default = "Unknown")
    vatNumber = models.CharField(max_length = 8, unique = True, default = "00000000", primary_key=True)
    email = models.CharField(max_length = 50, unique = True)
    phone = models.CharField(max_length = 50, unique = True)
    password = models.CharField(max_length = 50)
    
    def __str__(self):
        return f"{self.vatNumber} { self.name }"
    
    def save(self, *args, **kwargs):# use vatNumber to get company name
        self.name = getComponyName(self.vatNumber)
        super().save(*args, **kwargs)
        

class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name = 'products',null = True)
    name = models.CharField(max_length = 20)
    description = models.TextField(blank = True)
    photo = models.ImageField(upload_to = 'product_photo', blank = True)
    carbonEmission = models.FloatField(default = 0.0, editable = False)
    
    def __str__(self):
        return self.name
    
    
    
class materials(enum.Enum):
    a = 1
    b = 2
    c = 3
    
    
class Component(models.Model):
    product = models.ForeignKey(to = 'Product', on_delete=models.CASCADE, related_name = 'components',null = True)
    name = models.CharField(max_length = 20)
    material = enum.EnumField(materials, default = materials.a)
    weight = models.FloatField(default = 0.0)
    carbonEmission = models.FloatField(default = 0.0, editable = False)
    
    def __str__(self):
        return self.name
    
    def calculateCarbonEmission(self):
        self.carbonEmission += self.weight * 0.1

    def save(self, *args, **kwargs):
        self.calculateCarbonEmission()
        self.product.carbonEmission += self.carbonEmission
        self.product.save()
        super().save(*args, **kwargs)
    
    
    

        

@receiver(pre_delete, sender = Record, dispatch_uid = 'record_delete_signal')
def delete_wallet_point(sender, instance, using, **kwargs):
    instance.user.wallet -= instance.point
    instance.user.save()
    
@receiver(pre_delete, sender = Product, dispatch_uid = 'product_delete_signal')
def delete_photo(sender, instance, using, **kwargs):
    instance.photo.delete(save = True)
    
@receiver(pre_delete, sender = Component, dispatch_uid = 'component_delete_signal')
def delete_carbonEmission(sender, instance, using, **kwargs):
    instance.product.carbonEmission -= instance.carbonEmission
    instance.product.save()

