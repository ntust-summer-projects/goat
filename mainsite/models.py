#from django.db import models
from django.contrib.gis.db import models
import geopy.distance
from geopy.geocoders import Nominatim
from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
import requests
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
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

class UserManager(BaseUserManager):
    def create_user(self, name, email, phone, password = None):
        if not email:
            raise ValueError('Users must have an email address')
        
        if not name:
            raise ValueError('Users must have an username')
        user = self.model(
            email = self.normalize_email(email),
            name = name,
            phone = phone,
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, name, email, phone, password = None):
        user = self.create_user(
            email = self.normalize_email(email),
            name = name,
            password = password,
            phone = phone,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using = self._db)
        return user

class User(AbstractBaseUser):
    name = models.CharField(max_length = 20, unique = True)
    password = models.CharField(max_length = 200, default = '')
    email = models.EmailField(max_length = 100,unique = True)
    phone = models.CharField(max_length = 50, unique = True)
    wallet = models.PositiveBigIntegerField(editable = False,default = 0)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)   
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone', 'password']

    objects = UserManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    
    
class Transportation(models.Model):
    name = models.CharField(max_length = 20, unique = True)
    carbonEmission = models.FloatField(default = 0.0)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        try:
            oldData = Transportation.objects.get(pk = self.pk)
            
            if oldData.carbonEmission != self.carbonEmission:
                super().save(*args, **kwargs)
                for record in self.record_set.filter(transportation = self):
                    record.save()
                return
        
        except Transportation.DoesNotExist:
            pass
        super().save(*args, **kwargs)

class Record(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    startPlace = models.PointField(blank = True, default = (0.0, 0.0))
    endPlace = models.PointField(blank = True, default = (0.0, 0.0))
    routeLength = models.FloatField(blank = True, default = 0.0)
    carbonEmission = models.FloatField(editable = False, default = 0.0)
    #point = models.PositiveBigIntegerField(editable = False, default = 0)
    dateTime = models.DateTimeField(auto_now_add = True,null = True)
    start = models.CharField(max_length = 200, null = True, editable = False)
    end = models.CharField(max_length = 200, null = True, editable = False)
    transportation = models.ForeignKey(Transportation, on_delete=models.CASCADE, default = 1)

    def getDistance(self):
        distance = self.startPlace.distance(self.endPlace)
        print((self.startPlace[1], self.startPlace[0]), (self.endPlace[1], self.endPlace[0]))
        return geopy.distance.geodesic((self.startPlace[1], self.startPlace[0]), (self.endPlace[1], self.endPlace[0])).km
    
    def getEmission(self):
        return self.routeLength*self.transportation.carbonEmission

    def save(self, *args, **kwargs):
        if not(self.startPlace == self.endPlace):
            self.routeLength = self.getDistance()
            self.start = geolocator.reverse((self.startPlace.y, self.startPlace.x)).address
            self.end = geolocator.reverse((self.endPlace.y, self.endPlace.x)).address
        
        self.carbonEmission = self.routeLength*self.transportation.carbonEmission
        #self.user.wallet += self.point
        #self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.name} from {self.start} to {self.end}, length = {self.routeLength} km, get {self.point} points."
    
class Company(models.Model):
    name = models.CharField(max_length = 20, editable = False, default = "Unknown")
    vatNumber = models.CharField(max_length = 8, unique = True, default = "00000000", primary_key=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length = 50, unique = True)
    password = models.CharField(max_length = 50)
    
    def __str__(self):
        return f"{self.vatNumber} { self.name }"
    
    def save(self, *args, **kwargs):# use vatNumber to get company name
        self.name = getComponyName(self.vatNumber)
        super().save(*args, **kwargs)
        

# product model
        

class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name = 'products', default = "11111111")
    name = models.CharField(max_length = 20)
    description = models.TextField(blank = True)
    photo = models.ImageField(upload_to = 'product_photo', blank = True)
    materials = models.ManyToManyField(to = 'Material', through = 'Component', related_name = 'products')
    carbonEmission = models.FloatField(editable = False, default = 0.0)
    
    def getEmission(self):
        emission = 0.0
        
        try:
            oldData = Product.objects.get(pk = self.pk)
            
            for component in self.component_set.all():
                emission += component.carbonEmission
            
        except Product.DoesNotExist:
            pass
        return emission
    
    def __str__(self):
        #print(self.materials.all())
        #print(self.component_set.all())
        #print(self.component_set.all()[0].weight)
        #self.getEmission()
        return self.name
    
    def save(self, *args, **kwargs):
        self.carbonEmission = self.getEmission()
        super().save(*args, **kwargs)
    
    
class Material(models.Model):
    CName = models.CharField(max_length = 50, default = "未知")
    EName = models.CharField(max_length = 50, default = "Unknown")
    carbonEmission = models.FloatField(default = 0.0)
    
    unique_together = ('CName', 'EName')
    
    def __str__(self):
        return self.CName
    
    def save(self, *args, **kwargs):
        try:
            oldData = Material.objects.get(pk = self.pk)
            
            if oldData.carbonEmission != self.carbonEmission:
                super().save(*args, **kwargs)
                for component in self.component_set.filter(material = self):
                    component.save()
                return
        
        except Material.DoesNotExist:
            pass
        super().save(*args, **kwargs)
            
    
class Component(models.Model):
    product = models.ForeignKey(to = 'Product', on_delete=models.CASCADE, default = 1)
    material = models.ForeignKey(to = 'Material', on_delete=models.CASCADE, default = 1)
    weight = models.FloatField(default = 0.0)
    description = models.TextField(blank = True)
    carbonEmission = models.FloatField(editable = False, default = 0.0)
    
    class Meta:
        unique_together = ['product', 'material']
    
    def __str__(self):
        return f"{ self.material } { self.weight }"
    
    def getEmission(self):
        return self.weight * self.material.carbonEmission
    
    def save(self, *args, **kwargs):
        self.carbonEmission = self.getEmission()
        
        try:
            oldData = Component.objects.get(pk = self.pk)
        
            if oldData.carbonEmission != self.carbonEmission:
                super().save(*args, **kwargs)
                self.product.save()
                return
                
        except Component.DoesNotExist:
            super().save(*args, **kwargs)
            self.product.save()
            return
        super().save(*args, **kwargs)
        
@receiver(post_delete, sender = Component, dispatch_uid = 'component_delete_signal')
def delete_carbonEmission(sender, instance, using, **kwargs):
    instance.product.save()
    
'''
@receiver(pre_delete, sender = Record, dispatch_uid = 'record_delete_signal')
def delete_wallet_point(sender, instance, using, **kwargs):
    instance.user.wallet -= instance.point
    instance.user.save()'''
    
@receiver(pre_delete, sender = Product, dispatch_uid = 'product_delete_signal')
def delete_photo(sender, instance, using, **kwargs):
    instance.photo.delete(save = True)

 


