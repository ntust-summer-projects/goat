# goat

### models.py
- table Product:
  
  ```python
  company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name = 'products',null = True)
  name = models.CharField(max_length = 20)
  description = models.TextField(blank = True)
  photo = models.ImageField(upload_to = 'product_photo', blank = True)
  carbonEmission = models.FloatField(default = 0.0, editable = False)# sum of component's carbonEmission
  ```
- table Component:
  
  ```python
  product = models.ForeignKey(to = 'Product', on_delete=models.CASCADE, related_name = 'components',null = True)
  material = enum.EnumField(materials, default = materials.a)
  weight = models.FloatField(default = 0.0)
  carbonEmission = models.FloatField(default = 0.0, editable = False)
  ```
- create log:
  # warning : 盡可能使用 create 創建log 或在 save argument 加入 force_insert = True, 否則會跳 warning : log maybe be changed
  
- create all log:

  ```python
  LogManager.create(user = currentuser_object, logType = AbstractLog.LogType_member, ...log_argument)
  # or
  AbstractLog.objects.create(user = currentuser_object, logType = AbstractLog.LogType_member, ...log_argument)
  # or
  AbstractLog(user, logtype).save(...log_argument)
  ```
- create transportation log:

  ```python
  LogT.objects.create(user = currentuser_object, distance = number, transportation = Transportation_object)
  # or
  log = LogT(user =  currentuser_object)
  log.save(distance = number, transportation = Transportation_object)
  ```
- create item log:

  ```python
  LogI.objects.create(user = currentuser_object, product = Product_object, amount = number)
  # or
  log = LogI(user =  currentuser_object)
  log.save(product = Product_object, amount = number)
  ```
