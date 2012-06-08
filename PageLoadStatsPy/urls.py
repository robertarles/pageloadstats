from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'PageLoadStatsPy.views.home', name='home'),
    # url(r'^PageLoadStatsPy/', include('PageLoadStatsPy.foo.urls')),
    
    url(r'^pls/', include('PageLoadStatsPy.pageloadstats.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
