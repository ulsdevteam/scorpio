"""scorpio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from asterism.views import PingView
from django.contrib import admin
from django.urls import include, re_path
from rest_framework.schemas import get_schema_view

from indexer.views import (IndexAddView, IndexDeleteView, IndexResetView,
                           IndexRunViewSet)

from .routers import ScorpioRouter

router = ScorpioRouter()
router.register(r'index-runs', IndexRunViewSet, 'indexrun')

schema_view = get_schema_view(
    title="Scorpio API",
    description="Endpoints for Scorpio microservice application."
)

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^index/add/', IndexAddView.as_view(), name='index-add'),
    re_path(r'^index/delete/', IndexDeleteView.as_view(), name='index-delete'),
    re_path(r'^index/reset/', IndexResetView.as_view(), name='index-reset'),
    re_path(r'^status/', PingView.as_view(), name='ping'),
    re_path(r'^schema/', schema_view, name='schema'),
    re_path(r'^', include(router.urls)),
]
