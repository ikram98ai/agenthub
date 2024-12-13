from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


admin.site.site_header = "AgentHub's Admin"
admin.site.index_title = 'Admin'


urlpatterns = [
    path('', include('agents.urls')),
    path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [  path("__debug__/", include("debug_toolbar.urls")), ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
 

