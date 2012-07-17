from django.template import Context, loader
from PageLoadStatsPy.pageloadstats.models import Target, Alert, Stat, Stat_Rich
from PageLoadStatsPy.pageloadstats.charts import Pls_Chart
from pyofc2 import *
from django.http import HttpResponse
import urllib2
import time

cs_comment_tags = ["request id:", "tag:","server:", "elapsed:", "elapsed2:"]

def target_list(request):
    latest_target_data = Target.objects.filter(active=1).order_by('name')[:50]
    t = loader.get_template('index.html')
    c = Context({
                 'latest_target_data': latest_target_data,
    })
    return HttpResponse(t.render(c))

def chart(request, target_id):
    target = Target.objects.get(pk=target_id)
    t = loader.get_template('chart.html')
    c = Context({
        'target_id': target_id,
        'target_name': target.name,
    })
    return HttpResponse(t.render(c))    

##
# Return the html/javascript vars required to generate a SINGLE TARGET Open Flash Chart
##
def chart_data(request, target_id):
    #pls_chart = Pls_Chart("http://robert.arles.us?some=someval&other=otherVal&booyah=argh")
    #pls_chart.init_param_vars()
    
    target = Target.objects.get(pk=target_id)
    
    t = title(text=time.strftime( '%a %Y %b %d') + " for Target ID:" + target_id + " Name: " + target.name )
    
    largest_load_time = 100
    
    stats_rs = Stat_Rich.objects.filter(target_id=target_id).order_by("-timestamp")[:100] # get the latest
    stats=[]
    for stat in stats_rs:
        stats.insert(0,stat)
        
    load_times_values = []
    elapsed_times_values = []
    elapsed2_times_values = []
    load_time_request_dates = []
    alert_times_level = []
    alert_val = None
    for stat in stats:
        load_times_values.append(stat.page_load_time)
        load_time_request_dates.append(stat.request_date)
        if(hasattr(stat, 'elapsed') and stat.elapsed!="null" and stat.elapsed!=None):
            elapsed_times_values.append(int(stat.elapsed))   
        if(hasattr(stat, 'elapsed2') and stat.elapsed2!="null" and stat.elapsed2!=None):
            elapsed2_times_values.append(int(stat.elapsed2))   
        if(hasattr(stat, 'query_time') and stat.query_time!="null" and stat.query_time!=None):
            elapsed_times_values.append(int(stat.query_time))  
        if(stat.page_load_time > largest_load_time):
            largest_load_time = stat.page_load_time
        # !! lets not run the stat.alert_level() query EVERY time we run through this loop.
        if(alert_val==None):
            alert_val = stat.alert_level()
        if(alert_val):
            alert_times_level.append(int(alert_val))

    #### Create the chart line objects
    # create an instance of the pageloadstats chart object
    pls_chart = Pls_Chart()
        
    # LOAD average for the legend
    load_average = sum(load_times_values) / len(load_times_values)
    # Create LOAD time line
    pls_chart.add_line("load", "load("+str(load_average)+")", load_times_values, load_time_request_dates, '#458B00')

    # Create the SMA line
    sma_values = get_sma_values(stats, 96)
    sma_avg = sum(sma_values) / len(sma_values)
    if(sma_values!=None and len(sma_values)>0):
        pls_chart.add_line("SMA", "SMA("+str(sma_avg)+")", sma_values, load_time_request_dates, "#0000FF")
        
    # ELAPSED average of the times for the legend
    elapsed_average = 0
    if(len(elapsed_times_values) >0):
        elapsed_average = sum(elapsed_times_values) / len(elapsed_times_values)
    # Create ELAPSED time line
    pls_chart.add_line("elapsed", "elapsed("+str(elapsed_average)+")",elapsed_times_values, load_time_request_dates, '#BF3EFF' )
    
    # ELAPSED2 average of the times for the legend
    elapsed2_average = 0
    if(len(elapsed2_times_values) >0):
        elapsed2_average = sum(elapsed2_times_values) / len(elapsed2_times_values)
    # Create ELAPSED2 time line
    pls_chart.add_line("elapsed2", "elapsed2("+str(elapsed2_average)+")",elapsed2_times_values, load_time_request_dates, '#CD6600' )
    
    # Create ALERT level line
    alert_level = 0
    if(len(alert_times_level) > 0):
        alert_level = alert_times_level[0]
    pls_chart.add_line("Alert Level", "Alert at "+str(alert_level)+"ms", alert_times_level, load_time_request_dates, "#DC143C")
    

    
    # setup the y axis
    y_axis_step_size = largest_load_time / 5
    y = y_axis()
    y.min, y.max, y.steps = 0, largest_load_time, y_axis_step_size
    y.min =0 
    y.max =largest_load_time
    y.steps = y_axis_step_size
    pls_chart.y_axis = y
    
    
    # setup the x axis
    x = x_axis()        
    x_axis_step_size = len(load_time_request_dates)/15
    xlabels = x_axis_labels(steps=x_axis_step_size, rotate='vertical')
    xlabels.labels = pls_chart.get_x_axis_array( load_time_request_dates[0], load_time_request_dates[len(load_time_request_dates)-1], 15)
    x.labels = xlabels
    pls_chart.x_axis = x
    
 
    pls_chart.title = t
    return HttpResponse(pls_chart.render())

    
##
# This function calls getCheckOutput.  (TODO: Why is it merely a proxy for getCheckOutput()? and why did it need the request object?)
# @param request the http request
# @param target_id the target id to check stats on (an ID or 'all' to check them ALL!)
def check(request, target_id):
    check_output = get_check_output(target_id)
    return HttpResponse(check_output, mimetype = "application/json")    

    
##
# Get the stats for the requested target (or 'all' targets)
# @param target_id the ID of the target to check, or 'all' to check them all.
def get_check_output(target_id):
    retVal = "{"
    targets = None
    
    if(target_id=="all"):
        targets = Target.objects.filter(active=1)
    else:
        targets = Target.objects.filter(id=target_id).filter(active=1)

    for target in targets:
        request = urllib2.Request(target.url)
        status = 200
        try:
            startTime = time.time()
            response = urllib2.urlopen(request)
            cs_comment_list = get_cs_comments(response)
            endTime = time.time()
            loadTime = int((endTime-startTime)*1000) # get the download time in milliseconds        
            s = Stat(url=target.url, target_id=target.id,elapsed=0,elapsed2=0,result_count=0,query_time=0,timestamp=startTime, page_load_time=loadTime, http_status=str(status))
            s.save()
        
            retVal += "{'id':'" + target.url + "', 'load_time':'" + str(loadTime) + "', 'http_status':'" + str(status)+"'},"

        except IOError, e:
            if hasattr(e, 'reason'):
                retVal+= '{"We failed to reach target '+ str(target_id) +'. Reason":"'+ str(e.reason) + '"}'
            elif hasattr(e, 'code'):
                retVal+= '{The server couldn\'t fulfill the request.Error code":"'+ str(e.code) +'"}'
                status = e.code
        else:
            retVal +=""

    retVal = retVal.strip(",")
    retVal += "}"
    return retVal

##
# grab a list of the citysearch comments from the current page.  These include server, release, elapsed...
# @parameter response the page's HTML source
# @return a dict of Citysearch comments
def get_cs_comments(response):
    in_comment = False
    comment_dict = None
    
    for line in response:
        line = line.strip()
        if(line.find("<!--")):
            in_comment = True
        if(in_comment == True):
            for tag in cs_comment_tags:
                if(line.startswith(tag)):
                    tag_name = tag.replace(" ", "_")
                    comment_dict[tag_name] = "value" 
                    # TODO: check how this line is split and saved in the old pls
        if(line.find("-->")):
            in_comment = False
            
    return comment_dict

##
# Get a simple moving average for the current id
def get_sma_values(stats, sma_window_size):
    sma_values = []
    
    stat_one=None
    for stat in stats:
        stat_one = stat
        break
    
    start_ts = stat_one.timestamp
    target_id = stat_one.target_id
    historic_values = Stat_Rich.objects.filter(target_id=target_id).filter(timestamp__lt=start_ts).order_by("-timestamp")[:sma_window_size]
    #print("* current("+str(len(current_values))+")")
    #for stat in current_values:
    #    print(str(stat.timestamp))
    #print("* history("+str(len(historic_values))+")")
    #for stat in historic_values:
    #    print(str(stat.timestamp))
    
    # calculate an SMA for the first values
    sma_cavg = []
    for stat in historic_values:
        sma_cavg.append(stat.page_load_time)
        
    #sma_values.append( sum(sma_cavg) )
    # now begin walking through the values, appending the sma as we go
    for stat in stats:
        sma_cavg.append(stat.page_load_time)
        sma_cavg.pop(0)
        sma_values.append(sum(sma_cavg)/len(sma_cavg))

    return sma_values
    
    
    