from django.conf.urls.defaults import patterns, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('pageloadstats.views',
    url(r'^target/$', 'target_list'),
    url(r'^chart/(?P<target_id>\d+)/$', 'chart'),
    url(r'^chart_data/(?P<target_id>\d+)/$', 'chart_data'), #this one returns the data for the chart page
    url(r'^check/(?P<target_id>\d+)/$', 'check'),
    url(r'^check/(?P<target_id>all)/$', 'check'),
)
