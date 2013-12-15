from django.conf.urls import patterns, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('PageLoadStatsPy.pageloadstats.views',
    url(r'^$', 'daily_avgs'),                              # default view url
    url(r'^targets/$', 'target_list'),                      # a list of targets in the db
    
    url(r'^chart/(?P<target_id>\d+)/$', 'chart'),           # the chart for target # <target_id>
    url(r'^chartimage/(?P<target_id>\d+)/$', 'matlab_chart'),           # the matlab based chart for target # <target_id>
    url(r'^chart/(?P<tag>\w+)/$', 'chart_multi_by_tag'),      # the chart for multiple targets
    url(r'^chart/(?P<target_id_list>[0-9]+,[0-9,]+)/$', 'chart_multi_by_id'),      # the chart for multiple targets by id
    url(r'^dailyavgs/$', 'daily_avgs'),              # show the current daily overall performance stats
    #url(r'^dailyavgs/(?P<days>[0-9]+)/$', 'daily_avgs'),              # show the current daily overall performance stats
    url(r'^dailyavgs/(?P<tags>[\w,]+)/(?P<days>[0-9]+)/$', 'daily_avgs'),              # show the current daily overall performance stats
    url(r'^httperrors/$', 'http_errors'), # show stats of tests that did not return http 200
    url(r'^httperrorchart/$', 'http_errorchart'), # get a chart of  http errors
    url(r'^manage/targets/$', 'manage_targets'),
    url(r'^manage/alerts/$', 'manage_alerts'),
    url(r'^target/edit/(?P<target_id>\d+)/$', 'edit_target'),
    url(r'^target/add/$', 'add_target'),
    url(r'^alert/edit/(?P<alert_id>\d+)/$','edit_alert'),
    url(r'^alert/add/$', 'add_alert'),
    
    url(r'^chart/$', 'flot'),
    url(r'^api/chartline/$', 'flot_line'),
     
    # API for OFC2 charting
    url(r'^api/ofc2chart/httperrors/$', 'chart_httperrors'),        # API this one returns the data for the chart_multi view
    url(r'^api/ofc2chart/(?P<target_id>\d+)/$', 'chart_data'), # API this one returns the data for the chart view
    url(r'^api/matlabchartimage/(?P<target_id>\d+)/$', 'matlab_chart_image'), # API this one returns the data for the chart view
    url(r'^api/ofc2chart/(?P<target_id_list>[0-9,]+)/$', 'chart_multi_data_by_ids'),        # API this one returns the data for the chart_multi view
    url(r'^api/ofc2chart/(?P<tag>\w+)/$', 'chart_multi_data_by_tag'),        # API this one returns the data for the chart_multi view
    
    # API 
    url(r'^api/tags/$', 'get_tags'), # API get a list of tags in use
    url(r'^api/targets/all/(?P<return_type>)\w+/$', 'get_targets_all'), # API get a lis of all active targets
    url(r'^api/targets/(?P<tag>\w+)/(?P<return_type>)\w+/$', 'get_targets_by_tag'), # API get a list of targets for the given tag
    
    url(r"^api/target/update/(?P<target_id>\d+)/$", "target_update"), # save changes to a target record
    url(r"^api/target/delete/(?P<target_id>\d+)/$", "target_delete"), # delete a target ACTUAL DELETION, you probably want to deactivate, not delete
    url(r"^api/target/create/", "target_create"), # add a new target
    url(r"^api/alert/update/(?P<alert_id>\d+)/$", "alert_update"), # save changes to a target record
    url(r"^api/alert/delete/(?P<alert_id>\d+)/$", "alert_delete"), # delete a target ACTUAL DELETION, you probably want to deactivate, not delete
    url(r"^api/alert/create/", "alert_create"), # add a new target
       
    url(r'^api/dailyavg/(?P<target_id>\d+)/(?P<days_ago>\d+)/$', 'get_daily_avg_by_id'),
    url(r'^api/dailyavg/(?P<tag>[\w,]+)/(?P<days_ago>\d+)/$', 'get_daily_avg_by_tag'),              # show the current daily overall performance stats
    
    url(r'^api/httperrors/$', 'get_http_errors'), # get a page of  http errors
    
    # request app to run checks against targets 
    url(r'^check/(?P<target_id>\d+)/$', 'check'),           # run a target stat check on tartet # <target_id>
    url(r'^check/(?P<target_id>all)/$', 'check'),           # run a target stat check on everything in the DB
    
    url(r'^user_logout/$', 'user_logout'),           # log a user out
)
