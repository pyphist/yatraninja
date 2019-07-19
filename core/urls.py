from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from user import urls as user_urls
from companion import urls as companion_urls
from notification import urls as notification_urls

admin.site.site_title = "Yatra Ninja"
admin.site.site_header = admin.site.site_title
admin.site.index_title = "Yatra Ninja Administration"

urlpatterns = [
                  url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),
                  url(r'^user/', include(user_urls)),
                  url(r'^companion/', include(companion_urls)),
                  path('admin/', admin.site.urls),
                  url(r'^notification/', include(notification_urls)),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
