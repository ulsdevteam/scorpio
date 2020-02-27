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
from django.urls import include, path
from rest_framework.schemas import get_schema_view

from .routers import ScorpioRouter
from .views import DataObjectViewSet, IndexAddView, IndexDeleteView, MergeView

router = ScorpioRouter()
router.register(r'objects', DataObjectViewSet, basename='objects')
schema_view = get_schema_view(
    title="Scorpio API",
    description="Endpoints for Scorpio microservice application.",
    urlconf='indexer.urls'
)

urlpatterns = [
    path(r'', include(router.urls)),
    path('index/add/', IndexAddView.as_view(), name='index-add'),
    path('index/delete/', IndexDeleteView.as_view(), name='index-delete'),
    path('merge/', MergeView.as_view(), name='merge'),
    path('status/', include('health_check.api.urls')),
    path('schema/', schema_view, name='schema'),

]
