from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import FileResponse, Http404
from django.urls import include, path, re_path

admin.site.site_header = 'Lost & Found Log: OSAS'
admin.site.site_title = 'Lost & Found Log'
admin.site.index_title = 'Administration'

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/', include('lostfound.urls')),
]

# Sa development lang. Sa production, ang web server (hal. nginx) ang magse-serve ng /media/.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


def frontend_index(request, *args, **kwargs):
    """Para sa mga address ng React app (hal. /items/5, /admin/claims): ibinabalik ang index.html
    para ang React Router ang pumili ng page. Gumagana lang kapag may na-build na frontend."""
    index = settings.FRONTEND_DIST / 'index.html'
    if not index.exists():
        raise Http404('Walang na-build na frontend.')
    response = FileResponse(open(index, 'rb'), content_type='text/html; charset=utf-8')
    response['Cache-Control'] = 'no-cache'
    return response


# Ang admin ng Django ay nasa /django-admin/, kaya malaya ang /admin/... ng React.
# Huwag isama ang api, static, media, at django-admin.
if (settings.FRONTEND_DIST / 'index.html').exists():
    urlpatterns += [re_path(r'^(?!api/|static/|media/|django-admin/).*$', frontend_index)]
