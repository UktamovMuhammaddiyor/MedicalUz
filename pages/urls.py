from django.urls import path
from .views import index, setWebHook, getpost

urlpatterns = [
    path('', index, name='index'),
    path('set/', setWebHook, name='set'),
    path('getpost/', getpost, name='getpost')
]
