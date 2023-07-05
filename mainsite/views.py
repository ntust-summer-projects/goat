from django.shortcuts import render
from django.http import HttpResponse
from .models import User, Record
from .forms import *
from rest_framework import viewsets, generics
from mainsite.serializers import *


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
class ComponentViewSet(viewsets.ModelViewSet):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
      
class RecordList(generics.ListAPIView):
    serializer_class = RecordSerializer
    def get_queryset(self):
        queryset = Record.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id is not None:
            queryset = queryset.filter(user=user_id)
        return queryset
    
# User.objects.all()
# User.objects.filter()
# User.objects.get(id = x) primary key

def getAllUser(request):
    users = User.objects.all()
    
    return render(request, "mainsite/templates/UserTable.html", { "users": users })


def postInputRecordForm(request):
    
    return render(request, "mainsite/templates/InputRecord.html", { "form": RecordForm })

def getAllRecord(request):
    records = list(Record.objects.values())
    
    for record in records:
        record['name'] = User.objects.get(id = record['user_id']).name
        
    data = { "records": records}
    return render(request , "mainsite/templates/map-extend.html", data)

def printRecord(request, result):
    return render(request , "mainsite/templates/map-extend.html", {"Record":result})
