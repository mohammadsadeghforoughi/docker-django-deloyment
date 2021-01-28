from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework import routers
from account.api import UserViewSet

router = routers.DefaultRouter()

router.register(r'users', UserViewSet)

urlpatterns = [
                  path('api/', include(router.urls)),
                  path('admin/', admin.site.urls),
                  path('', include('blog.urls')),
                  path('accounts/', include('account.urls')),
                  path('api-auth/', include('rest_framework.urls'))
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
                                                                                           document_root=settings.MEDIA_ROOT)
