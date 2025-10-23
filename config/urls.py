from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', include('pages.urls')),
    path('', include('courses.urls')),
]

# serve media in development
if settings.DEBUG:
    # from debug_toolbar.toolbar import debug_toolbar_urls
    from django.conf.urls.static import static
    import debug_toolbar
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
    # urlpatterns += debug_toolbar_urls()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
