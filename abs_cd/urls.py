"""abs_cd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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

# Disable the navigation sidebar feature.
# See also: https://stackoverflow.com/a/63314138
admin.autodiscover()
admin.site.enable_nav_sidebar = False

from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cd_manager/', include('cd_manager.urls', namespace='cd_manager')),
    path('', RedirectView.as_view(url='cd_manager/', permanent=True))
]
