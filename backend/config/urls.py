from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = 'Lost & Found Log: OSAS'
admin.site.site_title = 'Lost & Found Log'
admin.site.index_title = 'Administration'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('lostfound.urls')),
]

# Sa development lang. Sa production, ang web server (hal. nginx) ang magse-serve ng /media/.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
