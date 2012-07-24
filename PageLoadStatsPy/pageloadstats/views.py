from django.template import Context, loader
from PageLoadStatsPy.pageloadstats.models import Target, Alert, Stat, Stat_Rich
from PageLoadStatsPy.pageloadstats.charts import Pls_Chart
from pyofc2 import *
from django.http import HttpResponse
import urllib2
import time
import datetime
from datetime import datetime as datetimefunc
from django.contrib import auth
from django.http import HttpResponseRedirect

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
    start_date = request.GET.get('start_date',"")
    end_date = request.GET.get("end_date","")
    c = Context({
        'chart_data_url': "chart_data",
        'target_id_list_param': "&target_id_list=",
        'target_id': target_id,
        'target_name': target.name,
        'start_date': start_date,
        'start_end_params': "%26start_date="+start_date+"%26end_date="+end_date,
        'end_date': end_date,
    })
    return HttpResponse(t.render(c))  

def chart_multi(request):
    target_id_list = request.GET.get("target_id_list")
    t = loader.get_template('chart.html')
    start_date = request.GET.get('start_date',"")
    end_date = request.GET.get("end_date","")
    c = Context({
        'chart_data_url': "chart_multi_data",
        'target_id_list_param': "%26target_id_list="+target_id_list,
        'start_date': start_date,
        'start_end_params': "%26start_date="+start_date+"%26end_date="+end_date,
        'end_date': end_date,
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
    chart_range = 100  # default number of data points to show if no date range is specified
    start_date = request.GET.get('start_date')
    end_date = request.GET.get("end_date")

    if( start_date and end_date):
        stats_rs = Stat_Rich.objects.filter(target_id=target_id).filter(timestamp__gte=start_date).filter(timestamp__lte=end_date).order_by("-timestamp")
    else:
        stats_rs = Stat_Rich.objects.filter(target_id=target_id).order_by("-timestamp")[:chart_range] # get the latest
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
            
        fmt = "%Y/%m/%d %H:%M:%S"
        load_date = datetimefunc.strptime(stat.request_date, fmt)
        
        #shift 8 hours to pacific time
        tz_shift = 0
        tz_offset = request.COOKIES.get("tz_offset")
        if(tz_offset != None):
            tz_shift = int(tz_offset)
        load_date += datetime.timedelta(hours=-tz_shift)
        load_str = datetimefunc.strftime(load_date,fmt)

        
        load_time_request_dates.append(load_str)
        #have to check for entries with a string value of "null" (mySql return value)
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
            if(hasattr(stat, 'alert_level')):
                alert_val = stat.alert_level()
        if(alert_val):
            alert_times_level.append(int(alert_val))
           
    # create an instance of the pageloadstats chart object
    pls_chart = Pls_Chart()
    
    # setup the y axis
    y_axis_step_size = largest_load_time / 5
    y = y_axis()
    y.min, y.max, y.steps = 0, largest_load_time, y_axis_step_size
    y.min =0 
    y.max =largest_load_time + 100
    y.steps = y_axis_step_size
    pls_chart.y_axis = y
    
    
    # setup the x axis
    x = x_axis()        
    x_axis_step_size = len(load_time_request_dates)/15
    xlabels = x_axis_labels(steps=x_axis_step_size, rotate='vertical')
    xlabels.labels = pls_chart.get_x_axis_array( load_time_request_dates[0], load_time_request_dates[-1], 15)
    x.labels = xlabels
    pls_chart.x_axis = x
    
    #### Create the chart line objects

        
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
    
 
    pls_chart.title = t
    return HttpResponse(pls_chart.render())

def chart_multi_data(request):
    
    target_id_value = request.GET.get("target_id_list")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    COLOR_LIST = ("#6495ED", "#BDB76B", "#BA55D3", "#6B8E23", "#D2691E", "#DB7093", "#FF6347", "#6B8E23")
    color_index = 0

    
    target_id_list = target_id_value.split(",")
    chart_range = 100
    largest_load_time = 100
    date_range = []
    date_range_set = False


    pls_chart = Pls_Chart()

    chart_axis_set = False
    
    for target_id in target_id_list:
            
        stats_rs_list= []
        stats_list= []
        target_id = int(target_id)
        load_times = []
        
        target = Target.objects.get(pk=target_id)
        if(start_date and end_date):
            stats_rs_list = Stat_Rich.objects.filter(target_id=target_id).filter(timestamp__gte=start_date).filter(timestamp__lte=end_date).order_by("-timestamp")
        else:
            stats_rs_list = Stat_Rich.objects.filter(target_id=target_id).order_by("-timestamp")[:chart_range]
        
            
        for stat in stats_rs_list: # reverse the list to get them oldest to newest
            stats_list.insert(0,stat) 
        
        for stat in stats_list:
            if(stat.page_load_time > largest_load_time):
                largest_load_time = stat.page_load_time
            load_times.append(stat.page_load_time) 
            if(date_range_set==False):           
                fmt = "%Y/%m/%d %H:%M:%S"
                load_date = datetimefunc.strptime(stat.request_date, fmt)
                #shift 8 hours to pacific time
                tz_shift = 0
                tz_offset = request.COOKIES.get("tz_offset")
                if(tz_offset != None):
                    tz_shift = int(tz_offset)
                load_date += datetime.timedelta(hours=-tz_shift)
                load_str = datetimefunc.strftime(load_date,fmt)
                date_range.append(load_str)
            
        date_range_set=True # once we've parsed a stat list, the date range is filled in.
        
        # setup the x axis
        if(chart_axis_set == False):
            x = x_axis()        
            x_axis_step_size = len(date_range)/15
            xlabels = x_axis_labels(steps=x_axis_step_size, rotate='vertical')
            xlabels.labels = pls_chart.get_x_axis_array( date_range[0], date_range[-1], 15)
            x.labels = xlabels
            pls_chart.x_axis = x
            
            chart_axis_set = True
                
        line_avg = 0
        if (len(load_times)>0):
            line_avg = sum(load_times)/len(load_times)
            
        pls_chart.add_line(target.name, target.name+"("+str(line_avg)+")", load_times, date_range, COLOR_LIST[color_index])
        
        color_index += 1 # move to the next line color for the chart
        
    # setup the y axis
    y_axis_step_size = largest_load_time / 5
    y = y_axis()
    y.min, y.max, y.steps = 0, largest_load_time, y_axis_step_size
    y.min =0 
    y.max =largest_load_time + 100
    y.steps = y_axis_step_size
    pls_chart.y_axis = y
        
    pls_chart.title =  title(text="Multi Target Chart")
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

def get_sma_values(stats, sma_window_size):
    """
    Get a simple moving average for the current id
    return a list of sma values for the supplied stats list
    @param stats A result set of stats
    @param sma_window_size A number specifying how large of a historic data sample to be used to calculate each sma point. 
    """
    
    start_ts = stats[0].timestamp
    target_id = stats[0].target_id
    historic_stats = Stat_Rich.objects.filter(target_id=target_id).filter(timestamp__lt=start_ts).order_by("-timestamp")[:sma_window_size]
    #print("* current("+str(len(current_values))+")")
    #for stat in current_values:
    #    print(str(stat.timestamp))
    #print("* history("+str(len(historic_values))+")")
    #for stat in historic_values:
    #    print(str(stat.timestamp))
    
    # calculate an SMA for the first values
    sma_cavg = []
    sma_window = []
    
    # load up the sma window
    for stat in historic_stats:
        sma_window.append(stat.page_load_time)
    
    # for each stat point, add it to the sma window and calculate the current average, insert into array of averages.  (also removing the oldest data point in the window queue) 
    for stat in stats:
        if(len(sma_window)>=sma_window_size):
            sma_window.pop(0)
        sma_window.append(stat.page_load_time)
        sma_cavg.append(sum(sma_window) / len(sma_window))

    return sma_cavg

def user_logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/accounts/login/?next=/pls/')
    
    
    
    