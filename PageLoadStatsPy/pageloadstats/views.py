from django.template import Context, RequestContext, loader
from PageLoadStatsPy.pageloadstats.models import Target, Alert, TargetAlert, Stat, Stat_Rich
from PageLoadStatsPy.pageloadstats.charts import Pls_Chart
from django.core.paginator import Paginator, EmptyPage
from pyofc2 import *
from django.http import HttpResponse
import urllib2
import time
import datetime
from datetime import datetime as datetimefunc
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.utils import simplejson
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.font_manager import FontProperties
import pylab
import numpy
import urlparse

cs_comment_tags = ["request id:", "tag:","server:", "elapsed:", "elapsed2:"]
SCATTER_DAY_RANGE = 14

def target_list(request):
    latest_target_data = Target.objects.filter(active=1).order_by('name')[:50]
    t = loader.get_template('index.html')
    c = Context({
                 'latest_target_data': latest_target_data,
    })
    return HttpResponse(t.render(c))


def manage_targets(request):
    latest_target_data = Target.objects.order_by('name')
    t = loader.get_template('manage_targets.html')
    c= Context({
                'latest_target_data': latest_target_data,
    })
    return HttpResponse(t.render(c))

def edit_target(request, target_id):
    target_data = Target.objects.get(pk=target_id)
    t = loader.get_template('edit_target.html')
    c = RequestContext(request,{
                'target_data': target_data
    })
    return HttpResponse(t.render(c))

## target api calls
###

def target_update(request, target_id):
    target = Target.objects.get(id=target_id)
    target.url = request.POST.get("target_url")
    target.name = request.POST.get("target_name")
    target.active = request.POST.get("target_active")
    target.tags = request.POST.get("target_tags")
    
    for alert in target.alerts.all():
        target_alert = TargetAlert.objects.get(alert = alert.id, target = target.id)
        target_alert.delete()
    
    alert_id = request.POST.get("alert_id")
    alert = Alert.objects.get(id=alert_id)
    target_alert = TargetAlert(target=target,alert=alert,active=1)
    target_alert.save()
    
    target.save()
    response = HttpResponseRedirect("/pls/manage/")
    return response
    
def target_create(request):
    pass

def target_delete(request):
    pass

###
## END target api calls

def chart(request, target_id):
    """
    create a chart page
    """
    target = Target.objects.get(pk=target_id)
    chartTemplate = loader.get_template('chart.html')
    start_date = request.GET.get('start_date',"")
    end_date = request.GET.get("end_date","")
    trim_above = request.GET.get("trim_above","")
    if(trim_above):
        trim_params = "%26trim_above="+trim_above
    else:
        trim_params=""
    c = Context({
        'chart_data_url': "api/ofc2chart/",
        'target_id': target_id,
        'target_name': target.name,
        'target_url': target.url,
        'start_date': start_date,
        'trim_above': trim_above,
        'trim_params': trim_params,
        'start_end_params': "%26start_date="+start_date+"%26end_date="+end_date,
        'end_date': end_date,
    })
    return HttpResponse(chartTemplate.render(c)) 

def  http_errorchart(request):
    t = loader.get_template('httperrorchart.html')
    c = Context({
        'chart_data_url': "api/ofc2chart/httperrors/",
    })
    return HttpResponse(t.render(c)) 

def chart_httperrors(request):
    urlList = [] #store urls for mapping to y-axis
    today = datetime.datetime.now()
    daysAgo =today - datetime.timedelta(days=SCATTER_DAY_RANGE)
    stats = Stat_Rich.objects.filter(http_status__gt="200").filter(timestamp__gt=time.mktime(daysAgo.timetuple()) )
    jsonStats = {}
    jsonStats["elements"]=[]
    type={}
    type["type"]="scatter"
    type["colour"]="#FFD600"
    dotStyle = {}
    dotStyle["type"]="anchor"
    dotStyle["colour"]="#D600ff"
    dotStyle["dot-size"]="2"
    dotStyle["rotation"]="45"
    dotStyle["sides"]= "4"
    type["dot-style"]=dotStyle
    
    #jsonStats["elements"].append(type)
    values={}
    type["values"]=[]
    
    oldestDay = datetime.datetime.fromtimestamp(stats[0].timestamp).timetuple().tm_yday
    newestDay = datetime.datetime.fromtimestamp(stats[len(stats)-1].timestamp).timetuple().tm_yday
    tsList = [] #to hold a list of timestamps from the stats set
    for stat in stats:
        tsList.append(stat.timestamp)
        jsonStat = {}
       # jsonStat["url"] = stat.url
        if( stat.url not in urlList):
            urlList.append(stat.url)
        jsonStat["y"]=urlList.index(stat.url) + 1
        tenthOfDay=str(datetime.datetime.fromtimestamp(stat.timestamp).timetuple().tm_hour / 2.4).replace(".","")
        jsonStat["x"]= str(datetime.datetime.fromtimestamp(stat.timestamp).timetuple().tm_yday) +"." + tenthOfDay +str(datetime.datetime.fromtimestamp(stat.timestamp).timetuple().tm_min)
        parsedurl = urlparse.urlparse(stat.url)
        tippath = parsedurl.path
        if(parsedurl.query):
            tippath += "?" + parsedurl.query
        if(len(tippath)>100):
            tippath = tippath[:100]+"..." 
        tiphost = parsedurl.hostname
        jsonStat["tip"] = "host: " + tiphost +"\ndate: "+stat.request_date +"\nstatus: "+str(stat.http_status)+  "\npath: "+tippath
        type["values"].append(jsonStat)
    jsonStats["elements"].append(type)
    title={}
    title["text"]="experimental display of http errors by page/day"
    jsonStats["title"]=title
    x_axis = {}
    #x_axis["min"]=oldestDay-1
    #x_axis["max"]=newestDay+1
    x_axis["labels"] = {}
   # x_axis["steps"] = "1"
    x_label_obj = {}
    x_labels = []
    for day in range(SCATTER_DAY_RANGE-1,-1,-1):
        date = datetime.datetime.now()
        labelDate = date-datetime.timedelta(days=day)
        dateString = labelDate.strftime('%m/%d/%Y')
        label = dateString
        if(label not in x_labels):
            x_labels.append(label)
    x_label_obj = {}
    x_label_obj["labels"] = x_labels
   # x_axis["labels"] = x_label_obj
    jsonStats["x_axis"]=x_axis
    y_axis = {}
    y_axis["min"]="0"
    y_axis["max"]=len(urlList)
    jsonStats["y_axis"]=y_axis
    
        
    return HttpResponse(simplejson.dumps(jsonStats), mimetype="application/json")


def http_errors(request):
    page=1
    if(request.GET.get('page')):
        page = request.GET.get('page')
    t = loader.get_template('httperrors.html')
    c = Context({
        'page': page,
    })
    return HttpResponse(t.render(c)) 

def get_http_errors(request):
    rpp = 50
    page=1
    if(request.GET.get('page')):
        page = request.GET.get('page')
    errorListAll = Stat.objects.filter(http_status__gt="200").order_by("-timestamp")
    # contact_list = Contacts.objects.all()
    paginator = Paginator(errorListAll, rpp)
    try:
        errorList = paginator.page(page)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    #return render_to_response('list.html', {"contacts": contacts})
    response_data = {}
    response_data['errors'] = []
    response_data['page'] = page
    response_data["num_pages"] = paginator.num_pages
    for error in errorList:
        error_dict  = {}
        error_dict["id"] = error.id
        error_dict["url"] = error.url
        error_dict["http_status"] = error.http_status
        error_dict["request_date"] =  error.request_date
        response_data["errors"].append(error_dict)
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")


def matlab_chart(request, target_id):
    target = Target.objects.get(pk=target_id)
    t = loader.get_template('chart_image.html')
    start_date = request.GET.get('start_date',"")
    end_date = request.GET.get("end_date","")
    trim_above = request.GET.get("trim_above","")    
    if(trim_above):
        trim_params = "%26trim_above="+trim_above
    else:
        trim_params = ""
    c = Context({
        'chart_data_url': "api/matlabchartimage/",
        'target_id': target_id,
        'target_name': target.name,
        'target_url': target.url,
        'start_date': start_date,
        'trim_above': trim_above,
        'end_date': end_date,
    })
    return HttpResponse(t.render(c))  

def chart_multi_by_tag(request, tag):
    """
    create a page with a multi-target chart based on TAGs sent in the url params
    """
    targets = Target.objects.filter(tags__contains=tag).filter(active=1)
    target_id_list = ""
    separator=""
    for target in targets:
        target_id_list = target_id_list+separator+str(target.id)
        separator = ","
        
    return chart_multi_by_id(request, target_id_list)

def chart_multi_by_id(request, target_id_list):
    """
    create a page to display a multi-target chart
    """
    #target_id_list = request.GET.get("target_id_list")
    chartTemplate = loader.get_template('chart.html')
    start_date = request.GET.get('start_date',"")
    end_date = request.GET.get("end_date","")
    trim_above = request.GET.get("trim_above","")
    if(trim_above):
        trim_params = "%26trim_above="+trim_above
    else:
        trim_params = ""
    c = Context({
        'chart_data_url': "api/ofc2chart/",
        'target_id': target_id_list,
        'target_name': "multiple targets",
        'start_date': start_date,
        'trim_above': trim_above,
        'trim_params': trim_params,
        'start_end_params': "%26start_date="+start_date+"%26end_date="+end_date,
        'end_date': end_date,
    })
    return HttpResponse(chartTemplate.render(c))

def daily_avgs(request,tags=["home", "bpp", "browse", "deals", "srp", "api"],days=4):
    t = loader.get_template('perfdaily.html')
    start_date = request.GET.get('start_date',"")
    end_date = request.GET.get("end_date","")
    start_date=""
    end_date=""
    days = range(1,int(days)+1)
    if(type(tags) != list):
        tags = tags.split(",")
    c = Context({
        'start_end_params': "%26start_date="+start_date+"%26end_date="+end_date,
        'days': days,
        'tags':tags,
    })
    return HttpResponse(t.render(c))  

def get_daily_avg_by_id(request, target_id, days_ago):
    now = int(time.time())
    days_offset = int(days_ago) -1
    ending_midnight = now - (now % (24 * 60 * 60)) - ((24*60*60)*days_offset)
    starting_midnight = ending_midnight - (24 * 60 * 60)
    #print now
    #print ending_midnight
    #print starting_midnight
    stats = Stat_Rich.objects.filter(timestamp__gte=starting_midnight).filter(timestamp__lte=ending_midnight).filter(target_id=target_id)

    
    sumElapsed = 0
    avgElapsed = 0
    sumLoad = 0
    avgLoad = 0
    target_name = ""
    
    for stat in stats:
        sumLoad += int(stat.page_load_time) if stat.page_load_time else 0
        sumElapsed += int(stat.elapsed) if stat.elapsed else 0
        if(hasattr(stat,"query_time")): # solr queries dont have elapsed times, but do have an equivilent query_time
            sumElapsed += int(stat.query_time) if stat.query_time else 0
        if(hasattr(stat,"name")):
            target_name = stat.name()
    
    #if there is data, calculate the averages, else stick with defaults of ZERO
    if(len(stats)>0):
        avgLoad = sumLoad / len(stats)
        avgElapsed = sumElapsed / len(stats)
    
    
    response_data = {}
    response_data['data_type'] = "daily averages for id" 
    response_data['id'] = target_id
    response_data['days_ago'] = days_ago
    response_data['load'] = avgLoad
    response_data['elapsed'] = avgElapsed
    response_data['target_name'] = target_name
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

def get_daily_avg_by_tag(request, tag, days_ago):
    now = int(time.time())
    days_offset = int(days_ago) -1
    ending_midnight = now - (now % (24 * 60 * 60)) - ((24*60*60)*days_offset)
    starting_midnight = ending_midnight - (24 * 60 * 60)
    #print now
    #print ending_midnight
    #print starting_midnight
    stats = Stat_Rich.objects.filter(timestamp__gte=starting_midnight).filter(timestamp__lte=ending_midnight).filter(target__tags__icontains=tag)

    
    sumElapsed = 0
    avgElapsed = 0
    sumLoad = 0
    avgLoad = 0
    
    for stat in stats:
        sumLoad += int(stat.page_load_time) if stat.page_load_time else 0
        sumElapsed += int(stat.elapsed) if stat.elapsed else 0
        if(hasattr(stat,"query_time")): # solr queries dont have elapsed times, but do have an equivilent query_time
            sumElapsed += int(stat.query_time) if stat.query_time else 0
    
    #if there is data, calculate the averages, else stick with defaults of ZERO
    if(len(stats)>0):
        avgLoad = sumLoad / len(stats)
        avgElapsed = sumElapsed / len(stats)
    
    
    response_data = {}
    response_data['data_type'] = "daily average for tag" 
    response_data['tag'] = tag
    response_data['days_ago'] = days_ago
    response_data['load'] = avgLoad
    response_data['elapsed'] = avgElapsed
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")
        

def chart_data(request, target_id):
    """
    Return the html/javascript vars required to generate a SINGLE TARGET Open Flash Chart
    """
    #pls_chart = Pls_Chart("http://robert.arles.us?some=someval&other=otherVal&booyah=argh")
    #pls_chart.init_param_vars()
    
    target = Target.objects.get(pk=target_id)
    
    t = title(text=time.strftime( '%a %Y %b %d') + " for Target ID:" + target_id + " Name: " + target.name )  # @UndefinedVariable
    
    largest_load_time = 100
    chart_range = 100  # default number of data points to show if no date range is specified
    start_date = request.GET.get('start_date')
    end_date = request.GET.get("end_date")
    trim_above = request.GET.get("trim_above")

    stats_rs = get_stats(target_id, start_date, end_date, trim_above)
    stats=[]
    
    #reverse the results for display on the chart, increasing date, left to right
    for stat in stats_rs:
        stats.insert(0,stat)
        
    load_times_values = []
    elapsed_times_values = []
    elapsed2_times_values = []
    load_time_request_dates = []
    alert_times_level = []
    alert_val = None
    
    for stat in stats:
        
        if (numpy.isnan(stat.page_load_time)): next
        load_times_values.append(stat.page_load_time)
            
        fmt = "%Y/%m/%d %H:%M:%S"
        load_date = datetimefunc.strptime(stat.request_date, fmt)
        
        #shift 8 hours to pacific time
        tz_shift = 0
        # removing TZ adjustment
        #tz_offset = request.COOKIES.get("tz_offset")
        #if(tz_offset != None):
        #    tz_shift = int(tz_offset)
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
    y = pls_chart.y_axis
    y.min, y.max, y.steps = 0, largest_load_time, y_axis_step_size
    y.min =0 
    y.max =largest_load_time + 100
    y.steps = y_axis_step_size
    pls_chart.y_axis = y
    
    
    # setup the x axis
    x = pls_chart.x_axis
    x_axis_step_size = len(load_time_request_dates)/15
    xlabels = x_axis_labels(steps=x_axis_step_size, rotate='vertical')  # @UndefinedVariable

    start_date_dt = load_time_request_dates[0]
    end_date_dt = load_time_request_dates[-1]
    xlabels.labels = pls_chart.get_x_axis_array( start_date_dt, end_date_dt, 15)
    x.labels = xlabels
    pls_chart.x_axis = x
    
    #### Create the chart line objects

        
    # LOAD average for the legend
    load_average = sum(load_times_values) / len(load_times_values)
    # Create LOAD time line
    pls_chart.add_line("load", "load("+str(load_average)+")", load_times_values, load_time_request_dates, '#458B00')

    # Create the SMA line
    sma_values = get_sma(stats, 96, "page_load_time")
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
##
# Return the html/javascript vars required to generate a SINGLE TARGET Open Flash Chart
##
def matlab_chart_image(request, target_id):
    SMA_WINDOW_SIZE= 100    
    target = Target.objects.get(pk=target_id)
    t = text=time.strftime( '%a %Y %b %d') + " for Target ID:" + target_id + " Name: " + target.name
    start_date = request.GET.get('start_date')
    end_date = request.GET.get("end_date")
    trim_above = request.GET.get("trim_above")
    if(trim_above==None): trim_above=999999
    earliestTimestamp = None
    latestTimestamp = None
    
    stats_rs = get_stats(target_id, start_date, end_date, trim_above)
    
    pageLoads=[]
    pageElapsed=[]
    
    for stat in stats_rs:
        alertLevel = stat.alert_level()
        if(latestTimestamp==None):
            latestTimestamp=stat.timestamp
        earliestTimestamp = stat.timestamp
        if (stat.page_load_time!=None and stat.page_load_time < trim_above):
            pageLoads.insert(0,int(stat.page_load_time)) 
        else:
            pageLoads.insert(0,np.ma.masked)  # @UndefinedVariable
            
        if (stat.elapsed!=None and stat.page_load_time < trim_above): 
            pageElapsed.insert(0,int(stat.elapsed))  
        else:
            pageElapsed.insert(0,np.ma.masked)  # @UndefinedVariable
            
    startEntry = datetime.datetime.fromtimestamp(earliestTimestamp)
    endEntry = datetime.datetime.fromtimestamp(latestTimestamp)
    
    #pageLoads_m=ma.masked_where(isnan(pageLoads),pageLoads)
    pageLoads_avg=0
    if(len(pageLoads)>0): pageLoads_avg = sum(pageLoads)/len(pageLoads)
    pageElapsed_avg=0
    if(len(pageElapsed)>0): pageElapsed_avg = sum(pageElapsed)/len(pageElapsed)
    # Create the SMA lines for elapsed times
    smaElapsed = get_sma_new(stats_rs, SMA_WINDOW_SIZE, "elapsed")
    smaElapsed_avg = 0
    if(len(smaElapsed)>0): smaElapsed_avg = sum(smaElapsed) / len(smaElapsed)
    smaPageLoads = get_sma_new(stats_rs, SMA_WINDOW_SIZE, "page_load_time")
    smaPageLoads_avg = 0
    if(len(smaPageLoads)>0): smaPageLoads_avg = sum(smaPageLoads) / len(smaPageLoads)
    
    xAxis = range(0,len(pageLoads))
    alertLevels=[]
    if(alertLevel != None):
        for i in range(len(pageLoads)):
            alertLevels.append(alertLevel)
    plt.figure(figsize=(13,5.5), dpi=400, facecolor="white", edgecolor="darkslategray")
    
    if(len(pageLoads)>0):
        plt.plot(xAxis,pageLoads, color='blue', linewidth=0.5, antialiased=True)
    if(len(smaPageLoads)>0):
        plt.plot(xAxis,smaPageLoads,color='black', linestyle="-", linewidth=0.5, antialiased=True)
    if(len(pageElapsed)>0):
        plt.plot(xAxis,pageElapsed, color='green', linewidth=0.5, antialiased=True)
    if(len(smaElapsed)>0):
        plt.plot(xAxis,smaElapsed,color='black', linestyle="-", linewidth=0.5, antialiased=True)
    if(len(alertLevels)>0):
        plt.plot(xAxis,alertLevels, color='red', linewidth=0.5, antialiased=True)
        
    plt.xlabel('date+time', fontsize=14, color='blue')
    plt.ylabel('ms', fontsize=14, color='blue')
    plt.autoscale(True,"both",True)
    
    fontP = FontProperties()
    fontP.set_size('small')
    #legend([plot1], "title", prop = fontP)
    ax = plt.subplot(111)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.97, box.height])
    plt.subplots_adjust(left=.05, right=.99)
    plt.legend((
                'Load('+str(pageLoads_avg)+')',
                'Load SMA('+str(smaPageLoads_avg)+')',
                'Elapsed('+str(pageElapsed_avg)+')',
                'Elapsed SMA('+str(smaElapsed_avg)+')',
                'Alert At ' + str(alertLevel),),
                'upper left',
                shadow=True,
                fancybox=True,
                prop=fontP,
                bbox_to_anchor=(.025,1.14))
    plt.title(t, fontsize=16, color='black')
    plt.grid(True)
    plt.legend()
    
    #plt.text(60, .025, r'$\mu=100,\ \sigma=15$') label on the chart
    
    canvas = FigureCanvasAgg(plt.figure(1)) 
    plt.close()   
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def chart_multi_data_by_tag(request,tag):
    """
    generate the javascript to create a chart for multiple target urls based on the TAGs 
    """
    targets = Target.objects.filter(tags__contains=tag).filter(active=1)
    target_id_list = ""
    separator=""
    for target in targets:
        target_id_list = target_id_list+separator+str(target.id)
        separator = ","
        
    return chart_multi_data_by_ids(request,target_id_list)

def chart_multi_data_by_ids(request,target_id_list):
    """
    generate the javascript to create a chart for multiple target urls
    """
    #target_id_value = request.GET.get("target_id_list")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    trim_above = request.GET.get("trim_above")
    COLOR_LIST = ("#6495ED", "#FF6347", "#BA55D3", "#6B8E23", "#D2691E", "#DB7093", "#666699", "#33cc33")
    color_index = 0

    target_id_list = target_id_list.split(",")
    chart_range = 100
    largest_load_time = 100

    pls_chart = Pls_Chart()

    chart_axis_set = False
    if(target_id_list == None):
        return False
    
    for target_id in target_id_list:
            
        stats_rs= []
        stats_list= []
        target_id = int(target_id)
        load_times = []
        date_range = []
        date_range_set = False
        
        target = Target.objects.get(pk=target_id)

        stats_rs = get_stats(target_id, start_date, end_date,trim_above)
            
        for stat in stats_rs: # reverse the list to get them oldest to newest for display on the chart
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
        if(len(date_range)<5):
            date_range.append("1001/01/01 01:01:01")
        # setup the x axis
        if(chart_axis_set == False):
            x = x_axis()        # @UndefinedVariable
            x_axis_step_size = len(date_range)/15
            xlabels = x_axis_labels(steps=x_axis_step_size, rotate='vertical')  # @UndefinedVariable
            xlabels.labels = pls_chart.get_x_axis_array( date_range[0], date_range[-1], 15)
            x.labels = xlabels
            pls_chart.x_axis = x
            
            chart_axis_set = True
                
        line_avg = 0
        if (len(load_times)>0):
            line_avg = sum(load_times)/len(load_times)
            
        pls_chart.add_line(target.name, target.name+"("+str(line_avg)+")", load_times, date_range, COLOR_LIST[color_index])
        
        color_index += 1 # move to the next line color for the chart
        if(color_index >= len(COLOR_LIST)):
            color_index = 0
        
    # setup the y axis
    y_axis_step_size = largest_load_time / 5
    y = y_axis()  # @UndefinedVariable
    y.min, y.max, y.steps = 0, largest_load_time, y_axis_step_size
    y.min =0 
    y.max =largest_load_time + 100
    y.steps = y_axis_step_size
    pls_chart.y_axis = y
        
    pls_chart.title =  title(text="Multi Target Chart")  # @UndefinedVariable
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

def get_sma(stats, sma_window_size, column):
    """
    Get a simple moving average for the current id
    return a list of sma values for the supplied stats list
    @param stats A result set of stats
    @param sma_window_size A number specifying how large of a historic data sample to be used to calculate each sma point. 
    """
    
    start_ts = stats[0].timestamp
    target_id = stats[0].target_id
    historic_stats = Stat_Rich.objects.filter(target_id=target_id).filter(timestamp__lt=start_ts).order_by("-timestamp")[:sma_window_size]
    
    # calculate an SMA for the first values
    sma_cavg = []
    sma_window = []
    
    # load up the sma window
    for stat in historic_stats:
        if(getattr(stat,column) != None):
            sma_window.append(int(getattr(stat,column)))
    
    # for each stat point, add it to the sma window and calculate the current average, insert into array of averages.  (also removing the oldest data point in the window queue) 
    for stat in stats:
        if(getattr(stat,column)==None): stat["column"] = 0
        if(len(sma_window)>=sma_window_size):
            sma_window.pop(0)
        sma_window.append(int(getattr(stat,column)))
        sma_cavg.append(sum(sma_window) / len(sma_window))

    return sma_cavg

def get_sma_new(stats, sma_window_size, column):
    """
    Get a simple moving average for the current id
    return a list of sma values for the supplied stats list
    @param stats A result set of stats
    @param sma_window_size A number specifying how large of a historic data sample to be used to calculate each sma point. 
    @param column the column from the db result set to create an SMA for
    """
    
    start_ts = stats[0].timestamp
    target_id = stats[0].target_id
    historic_stats = Stat_Rich.objects.filter(target_id=target_id).filter(timestamp__lt=start_ts).order_by("-timestamp")[:sma_window_size]
    
    # calculate an SMA for the first values
    sma_cavg = []
    sma_window = []
    # load up the sma window history
    for hstat in historic_stats:
        if(getattr(hstat,column) != None):
            sma_window.insert(0,int(getattr(hstat,column)))
        else:
            sma_window.insert(0,0)
            
    reversedStats = []
    for stat in stats:
        reversedStats.insert(0,stat)
    # for each stat point, add it to the sma window and calculate the current average, insert into array of averages.  (also removing the oldest data point in the window queue) 
    for stat in reversedStats:
        value = int(getattr(stat,column))
        print column +" "+ str(value)
        if(value==None): value = 0
        while(len(sma_window)>=sma_window_size):
            sma_window.pop(0)
        sma_window.append(value)
        avgValue = sum(sma_window) / len(sma_window)
        sma_cavg.append(avgValue)
        print "average " + str(avgValue)
    return sma_cavg

def get_tags(request):
        
    targets = Target.objects.filter(active=1)
    
    tag_dict = {}
    # get a list of tags in use on the targets
    for target in targets:
        target_tags = target.tags.split(",")
        for tag in target_tags:
            tag_dict[tag] = "placing the tag as a key ensures it will be unique, no dupe's"
    tag_list = tag_dict.keys()
    
    response_data = {}
    response_data['tags']=[]
    response_data['tags'].extend(tag_list)
    response_data['subject']="targets"
    
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

def get_targets_all(request, return_type):
    targets = Target.objects.filter(active=1)

    response_data = {}
    response_data['targets'] = []
    response_data['subject'] = "all_targets"
    
    for target in targets:
        target_dict  = {}
        target_dict["id"] = target.id
        target_dict["name"] = target.name
        target_dict["target_url"] = target.url
        target_dict["tags"] = target.tags
        response_data["targets"].append(target_dict)
        
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

def get_targets_by_tag(request, tag, return_type):
    targets = Target.objects.filter(active=1).filter(tags__contains=tag)

    response_data = {}
    response_data['targets'] = []
    response_data['with_tag'] = tag
    response_data['subject'] = "targets_with_tag"
    
    for target in targets:
        target_dict  = {}
        target_dict["id"] = target.id
        target_dict["name"] = target.name
        target_dict["target_url"] = target.url
        target_dict["tags"] = target.tags
        response_data["targets"].append(target_dict)
        
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

def user_logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/accounts/login/?next=/pls/')

def get_stats(target_id, start_date, end_date, trim_above):
    default_chart_range=100;
    if( start_date and end_date and trim_above):
        stats_rs = Stat_Rich.objects.filter(target_id=target_id).filter(timestamp__gte=start_date).filter(timestamp__lte=end_date).filter(page_load_time__lte=trim_above).exclude(page_load_time__isnull=True).order_by("-timestamp")
    elif (start_date and end_date):
        stats_rs = Stat_Rich.objects.filter(target_id=target_id).filter(timestamp__gte=start_date).filter(timestamp__lte=end_date).exclude(page_load_time__isnull=True).order_by("-timestamp")
    elif (trim_above):
        stats_rs = Stat_Rich.objects.filter(target_id=target_id).filter(page_load_time__lte=trim_above).exclude(page_load_time__isnull=True).order_by("-timestamp")[:default_chart_range]
    else:
        stats_rs = Stat_Rich.objects.filter(target_id=target_id).exclude(page_load_time__isnull=True).order_by("-timestamp")[:default_chart_range] # get the latest
    return stats_rs
    
    
    
    