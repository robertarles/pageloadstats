from django.template import Context, loader
from PageLoadStatsPy.pageloadstats.models import Target, Alert, Stat
from PageLoadStatsPy.pageloadstats.charts import Pls_Chart
from django.http import HttpResponse
import urllib2
from pyofc2 import *
import time

cs_comment_tags = ["request id:", "tag:","server:", "elapsed:", "elapsed2:"]

def target_list(request):
    latest_target_data = Target.objects.filter(active=1).order_by('id')[:50]
    t = loader.get_template('index.html')
    c = Context({
                 'latest_target_data': latest_target_data,
    })
    return HttpResponse(t.render(c))

def chart(request, target_id):
    t = loader.get_template('chart.html')
    c = Context({
        'target_id': target_id,
    })
    return HttpResponse(t.render(c))    

def chart_data(request, target_id):
    pls_chart = Pls_Chart("http://robert.arles.us?some=someval&other=otherVal&booyah=argh")
    pls_chart.init_param_vars()
    t = title(text=time.strftime('%a %Y %b %d') + " for Target ID:" + target_id )
    largest_load_time = 100
    stats = Stat.objects.filter(target_id=target_id).order_by("-timestamp")[:100]
    stats.reverse() # stats need to be placed on the chart from oldest to newest to get the timeline right
    
    load_times_values = []
    elapsed_times_values = []
    for stat in stats:
        load_times_values.append(stat.page_load_time)
        if(hasattr(stat, 'elapsed')):
            elapsed_times_values.append(stat.elapsed)
        if(stat.page_load_time > largest_load_time):
            largest_load_time = stat.page_load_time
            
    load_times_line = line()
    load_times_line.values = load_times_values
    load_average = sum(load_times_values) / len(load_times_values)
    load_times_line.text = "load("+str(load_average)+")"

    elapsed_times_line = line()
    elapsed_times_line.values = elapsed_times_values
    elapsed_times_line.colour = '#458B74'
    elapsed_times_line.text = "elapsed"
    
    y_axis_step_size = largest_load_time / 5
    y = y_axis()
    y.min, y.max, y.steps = 0, largest_load_time, y_axis_step_size
    
    
    chart = open_flash_chart()
    chart.title = t
    chart.add_element(load_times_line)
    chart.add_element(elapsed_times_line)
    chart.y_axis = y
    return HttpResponse(chart.render())
    
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
        if(line.contains("<!--")):
            in_comment = True
        if(in_comment == True):
            for tag in cs_comment_tags:
                if(line.startswith(tag)):
                    tag_name = tag.replace(" ", "_")
                    comment_dict[tag_name] = "value" 
                    # TODO: check how this line is split and saved in the old pls
        if(line.contains("-->")):
            in_comment = False
            
    return comment_dict