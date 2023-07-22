#from django.db import models
from django.contrib.gis.db import models
import geopy.distance
from geopy.geocoders import Nominatim
from django.db.models.signals import pre_delete, post_delete, post_save
from django.dispatch import receiver
import requests
from django.contrib.auth.models import AbstractUser, BaseUserManager
from auditlog.registry import auditlog
from auditlog.models import LogEntry
from django.utils import timezone

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

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        NORMAL = "NORMAL", 'Normal'
        COMPANY = "COMPANY", 'Company'
        
    base_role = Role.ADMIN
    
    phone = models.CharField(max_length=50,null=True,blank=True)
    
    role = models.CharField(max_length=50, choices=Role.choices,default = Role.ADMIN)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args,**kwargs)
 
class NormalManager(BaseUserManager):
    def get_queryset(self,*args,**kwargs):
        result = super().get_queryset(*args,**kwargs).filter(role=User.Role.NORMAL)
        return result
        
class Normal(User):
    
    base_role = User.Role.NORMAL
    
    normal = NormalManager()
    
    @property
    def profile(self):
        return self.normalprofile
    
    class Meta:
        proxy = True

@receiver(post_save, sender=Normal)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "NORMAL":
        NormalProfile.objects.create(user=instance)

class NormalProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100,null=True,blank=True)
    wallet = models.PositiveBigIntegerField(editable=False,default=0)
    carbonProduce = models.DecimalField(max_digits=20,decimal_places=4,default=0.0000)

    

class CompanyManager(BaseUserManager):
    def get_queryset(self,*args,**kwargs):
        result = super().get_queryset(*args,**kwargs).filter(role = User.Role.COMPANY)
        return result
        
class Company(User):
    
    base_role = User.Role.COMPANY
    
    company = CompanyManager()
    
    @property
    def profile(self):
        return self.companyprofile
    
    class Meta:
        proxy = True

@receiver(post_save, sender=Company)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "COMPANY":
        CompanyProfile.objects.create(user=instance)

class CompanyProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    companyName = models.CharField(max_length=100,null=True,blank=True)
    address = models.CharField(max_length=255,null=True,blank=True)
    vatNumber = models.CharField(max_length = 8, unique = True, default = "00000000", primary_key=True)
    chairman = models.CharField(max_length=50,null=True,blank=True)
    
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
        if self.pk:
            self.carbonEmission = self.getEmission()
        super().save(*args, **kwargs)
        #self.getLog()

    def getLog(self):
        print("**************log")
        history = LogEntry.objects.filter(object_id = self.pk)
        
        for entry in history:
            try:
                print(entry.changes)
                print(entry.object_id)
                print(entry.object_repr)
                print(entry.content_type)
                print(entry.timestamp)
                print(entry.actor)
                print(entry.serialized_data)
                print(entry.remote_addr)
                print(entry.additional_data)
            except Exception as e:
                print(f"{e}")
            
        return LogEntry.objects.filter(object_id = self.pk)
    
class Material(models.Model):
    CName = models.CharField(max_length = 50, default = "未知")
    EName = models.CharField(max_length = 50, default = "Unknown")
    carbonEmission = models.FloatField(default = 0.0)
    
    class Meta:
        unique_together = ['CName', 'EName']
    
    def __str__(self):
        return f"{ self.EName } { self.CName }"
    
    def save(self, *args, **kwargs):
        if self.pk and Material.objects.get(pk = self.pk).carbonEmission != self.carbonEmission:
            kwargs['force_update'] = True
            super().save(*args, **kwargs)
            for component in self.component_set.filter(material = self):
                component.save(force_update = True)
        else:  
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
        
        if self.pk and Component.objects.get(pk = self.pk).carbonEmission == self.carbonEmission:
            kwargs['force_update'] = True
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
            self.product.save(force_update = True)
        
        
@receiver(post_delete, sender = Component, dispatch_uid = 'component_delete_signal')
def update_carbonEmission(sender, instance, using, **kwargs):
    instance.product.save(force_update = True)
    
'''
@receiver(pre_delete, sender = TransportationLog, dispatch_uid = 'transportationLog_delete_signal')
def delete_wallet_point(sender, instance, using, **kwargs):
    instance.user.wallet -= instance.point
    instance.user.save()'''
    
@receiver(pre_delete, sender = Product, dispatch_uid = 'product_delete_signal')
def delete_photo(sender, instance, using, **kwargs):
    instance.photo.delete(save = True)    
    
# log model

class Transportation(models.Model):
    name = models.CharField(max_length = 20, unique = True)
    carbonEmission = models.FloatField(default = 0.0)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.pk and Transportation.objects.get(pk = self.pk).carbonEmission != self.carbonEmission:
            super().save(*args, **kwargs)
            for log in self.logtprofile_set.filter(transportation = self):
                log.save()
        else:
            super().save(*args, **kwargs)
        
class AbstractLog(models.Model):
    class LogType(models.TextChoices):
        TRANSPORTATION = "TRANSPORTATION", 'transportation'
        ITEM = "ITEM", 'item'
    
    baseType = LogType.TRANSPORTATION
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    logType = models.CharField(max_length=50, choices=LogType.choices,default = LogType.TRANSPORTATION)
    carbonEmission = models.FloatField(editable = False, default = 0.0)
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )
    
    def save(self, *args, **kwargs):
        self.logType = self.baseType
        super().save(*args,**kwargs)
    
class LogTManager(models.Manager):
    def get_queryset(self,*args,**kwargs):
        result = super().get_queryset(*args,**kwargs).filter(logType=AbstractLog.LogType.TRANSPORTATION)
        return result
    
    def create(self, **kwargs):
        log = self.model(user = kwargs.pop('user', None))
        log.save(force_insert = True, **kwargs)
    
class LogT(AbstractLog):
    baseType = AbstractLog.LogType.TRANSPORTATION
    
    objects = LogTManager()
    
    @property
    def profile(self):
        return self.logtprofile
    
    class Meta:
        proxy = True
        
    def __str__(self): 
        return f"{ self.pk }"
    
    def save(self, *args, **kwargs):
        super().save(*args, force_insert = kwargs.pop('force_insert',False), force_update = kwargs.pop('force_update', False))
        try:
            self.logtprofile
        except:
            kwargs.setdefault('distance', 0)
            kwargs.setdefault('transportation', Transportation.objects.get(pk = 1))
            kwargs.setdefault('log', self)
            LogTProfile.objects.create(**kwargs)
        
    

class LogTProfile(models.Model):
    log = models.OneToOneField(LogT, on_delete=models.CASCADE, primary_key=True)
    distance = models.FloatField(blank = True, default = 0.0)
    #point = models.PositiveBigIntegerField(editable = False, default = 0)
    transportation = models.ForeignKey(Transportation, on_delete=models.CASCADE, related_name = 'logs', default = 1)
    
    def getEmission(self):
        return self.distance * self.transportation.carbonEmission
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.log.carbonEmission = self.getEmission()
        self.log.save(force_update = True)
        #self.user.wallet += self.point
        #self.user.save()
        

    def __str__(self):
        return f"{ self.log.pk }"
  
class LogIManager(models.Manager):
    def get_queryset(self,*args,**kwargs):
        result = super().get_queryset(*args,**kwargs).filter(logType=AbstractLog.LogType.ITEM)
        return result
    
    def create(self, **kwargs):
        log = self.model(user = kwargs.pop('user', None))
        log.save(force_insert = True, **kwargs)
        
    
class LogI(AbstractLog):
    baseType = AbstractLog.LogType.ITEM
    
    objects = LogIManager()
    
    @property
    def profile(self):
        return self.logiprofile
    
    class Meta:
        proxy = True
        
    def save(self, *args, **kwargs):
        super().save(*args, force_insert = kwargs.pop('force_insert', False), force_update = kwargs.pop('force_update', False))
        try:
            self.logiprofile
        except:
            kwargs.setdefault('amount', 0)
            kwargs.setdefault('product', Product.objects.get(pk = 1))
            kwargs.setdefault('log', self)
            LogIProfile.objects.create(**kwargs)
        
class LogIProfile(models.Model):
    log  = models.OneToOneField(LogI, on_delete=models.CASCADE, primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default = 1)
    amount = models.PositiveBigIntegerField(default = 0)
    
    def getEmission(self):
        return self.amount * self.product.carbonEmission
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.log.carbonEmission = self.getEmission()
        self.log.save(force_update = True)
        
    def __str__(self):
        return f"{ self.log.pk }"

@receiver(post_delete, sender=LogIProfile)
@receiver(post_delete, sender=LogTProfile)
def delete_log_on_logProfile_delete(sender, instance, **kwargs):
    instance.log.delete()
'''
class Record(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    startPlace = models.PointField(blank = True, default = (0.0, 0.0))
    endPlace = models.PointField(blank = True, default = (0.0, 0.0))
    routeLength = models.FloatField(blank = True, default = 0.0)
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
        return f"{self.user.name} from {self.start} to {self.end}, length = {self.routeLength} km"
'''


    
    
auditlog.register(Product,serialize_data=True)
auditlog.register(Product.materials.through,serialize_data=True)





 
try:
    print("=======test========")
    print(User.objects.get(pk = 1))
    print(Transportation.objects.get(pk = 1))
    LogT.objects.create(user = User.objects.get(pk = 1), distance = 99, transportation = Transportation.objects.get(pk = 1))
    LogT(user=User.objects.get(pk=2)).save(distance = 777, transportation = Transportation.objects.get(pk = 1))
    LogI.objects.create(user = User.objects.get(pk = 1), product = Product.objects.get(pk=1), amount = 99)
    LogI(user = User.objects.get(pk = 2)).save(product = Product.objects.get(pk=2), amount = 101)
except Exception as e:
    print("error : ",f"{ e }")

