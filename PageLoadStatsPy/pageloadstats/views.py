from django.template import Context, loader
from PageLoadStatsPy.pageloadstats.models import Target, Alert, Stat
from django.http import HttpResponse
import urllib2
from pyofc2  import *
import time

def target_list(request):
    latest_target_data = Target.objects.filter(active=1).order_by('id')[:5]
    t = loader.get_template('pageloadstats/index.html')
    c = Context({
                 'latest_target_data': latest_target_data,
    })
    return HttpResponse(t.render(c))

def chart(request, target_id):
    t = loader.get_template('pageloadstats/chart.html')
    c = Context({
        'target_id': target_id,
    })
    return HttpResponse(t.render(c))    

def chart_data(request, target_id):
    t = title(text=time.strftime('%a %Y %b %d') + " for Target ID:" + target_id )
    largest_load_time = 100
    stats = Stat.objects.filter(target_id=target_id)[:50]
    load_times_values = []
    elapsed_times_values = []
    for stat in stats:
        load_times_values.append(stat.load_time)
        if(hasattr(stat, 'elapsed_time')):
            elapsed_times_values.append(stat.elapsed_time)
        if(stat.load_time > largest_load_time):
            largest_load_time = stat.load_time
            
    load_times_line = line()
    load_times_line.values = load_times_values

    elapsed_times_line = line()
    elapsed_times_line.values = elapsed_times_values
    elapsed_times_line.colour = '#56acde'
    
    y_axis_step_size = largest_load_time / 5
    y = y_axis()
    y.min, y.max, y.steps = 0, largest_load_time, y_axis_step_size
    
    
    
    chart = open_flash_chart()
    chart.title = t    
    chart.add_element(load_times_line)
    chart.add_element(elapsed_times_line)
    chart.y_axis = y
    return HttpResponse(chart.render())
    

def check(request, target_id):
    check_output = getCheckOutput(target_id)
    return HttpResponse(check_output, mimetype = "application/json")    
    
    
def getCheckOutput(target_id):
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
            endTime = time.time()
            loadTime = int((endTime-startTime)*1000) # get the download time in milliseconds        
            s = Stat(url=target.url, target_id=target.id,elapsed=0,elapsed2=0,result_count=0,query_time=0,timestamp=startTime, load_time=loadTime, http_status=str(status))
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

