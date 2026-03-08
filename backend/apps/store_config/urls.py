from django.urls import path
from . import views

urlpatterns = [
    path('', views.StoreConfigView.as_view(), name='store-config'),
    path('switch-env/', views.EnvironmentSwitchView.as_view(), name='switch-env'),
]
