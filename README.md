# goat

models.py

table Company:

vatNumber = models.CharField(max_length = 8, unique = True, default = "00000000", primary_key=True)#統一編號#
name = models.CharField(max_length = 20, editable = False, default = "Unknown")
email = models.CharField(max_length = 50, unique = True)
phone = models.CharField(max_length = 50, unique = True)
password = models.CharField(max_length = 50)

table Product:

company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name = 'products',null = True)
name = models.CharField(max_length = 20)
description = models.TextField(blank = True)
photo = models.ImageField(upload_to = 'product_photo', blank = True)
carbonEmission = models.FloatField(default = 0.0, editable = False)# sum of component's carbonEmission

table Component:

product = models.ForeignKey(to = 'Product', on_delete=models.CASCADE, related_name = 'components',null = True)
name = models.CharField(max_length = 20)
material = enum.EnumField(materials, default = materials.a)
weight = models.FloatField(default = 0.0)
carbonEmission = models.FloatField(default = 0.0, editable = False)
