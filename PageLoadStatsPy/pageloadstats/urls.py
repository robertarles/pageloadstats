from django.conf.urls.defaults import patterns, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('PageLoadStatsPy.pageloadstats.views',
    url(r'^$', 'target_list'),                              # default view url
    url(r'^targets/$', 'target_list'),                      # a list of targets in the db
    url(r'^chart/(?P<target_id>\d+)/$', 'chart'),           # the chart for target # <target_id>
    url(r'^chart_data/(?P<target_id>\d+)/$', 'chart_data'), # this one returns the data for the chart view
    url(r'^chart_multi/$', 'chart_multi'),           # the chart for multiple targets
    url(r'^chart_multi_data/$', 'chart_multi_data'), # this one returns the data for the chart_multi view
    url(r'^check/(?P<target_id>\d+)/$', 'check'),           # run a target stat check on tartet # <target_id>
    url(r'^check/(?P<target_id>all)/$', 'check'),           # run a target stat check on everything in the DB
    url(r'^perfdaily/$', 'perf_daily'),              # show the current daily overall performance stats
    url(r'^dailyavg/(?P<tag>.+)/(?P<days_ago>\d+)/$', 'daily_avg'),              # show the current daily overall performance stats
    url(r'^user_logout/$', 'user_logout'),           # log a user out
)
