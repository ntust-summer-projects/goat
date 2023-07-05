"""djangoTest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
import mainsite.views as view
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

router = DefaultRouter()
router.register(r'users', view.UserViewSet, basename='user')
router.register(r'records', view.RecordViewSet, basename='record')
router.register(r'companys', view.CompanyViewSet, basename='Company')


    
urlpatterns = [
   path('admin/', admin.site.urls),
   path('userTable/', view.getAllUser, name = "userTable"),
   path('inputRecord/', view.postInputRecordForm, name = "inputRecord"),
   path('getRecord/', view.getAllRecord, name = "getAllRecord"),
   re_path(r'^api/', include(router.urls)),
   re_path('^api/users/getRecords/(?P<user_id>.+)/$', view.RecordList.as_view()),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)