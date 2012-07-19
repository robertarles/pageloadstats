from pyofc2 import *
import datetime
from datetime import datetime as datetimefunc
from pytz import timezone
##
# A chart object using open_flash_charts 2 via pyofc2
#
class Pls_Chart(object):
		
	def __init__(self):
		self.chart = open_flash_chart()
		self.chart_lines = []
		self.x_axis = x_axis()
		self.y_axis = y_axis()
		self.title = "Page Load Stats"
		self.line_width = 1
		
	
	## get a list of url parameters
	def init_param_vars(self):
		param_string = self.url.split("?")[1]
		param_array = param_string.split("&")
		for param in param_array:
			key,value = param.split("=")
			print("%s : %s" % (key,value) )
			
			
	# Add a line to this chart object
	def add_line(self, name, legend_entry, values, dates, color):
		chart_line = self.get_line(name, legend_entry, values, dates, color)
		self.chart_lines.append(chart_line)
		return(True)
	
	# Create and return a line object
	def get_line(self, name, legend_entry, values, dates, color):
		chart_line = line()
		dots = []
		for i in range(len(values)-1):
			txt = name + "<br>" + dates[i] + "<br>" + "#val#ms"
			dot = dot_value(value=values[i], tip=txt)
			dots.append(dot)
		chart_line.values = dots
		chart_line.colour = color
		chart_line.text = legend_entry
		chart_line.width = self.line_width
		
		return(chart_line)
	
	# create and return an x-axis for a date range, defaulting to a 15 minute interval
	def set_x_axis(self, start, end, interval):
		self.x_axis = self.get_x_axis(start, end, interval)
	
	##
	# create and return an x-axis for a date range
	# @param start: The first date on the chart
	# @param end: The last date on the chart
	# @param interval: the number of minutes desired between the x-axis points (the chart granularity
	def get_x_axis_array(self, start, end, interval):
		fmt = "%Y/%m/%d %H:%M:%S"
		start_dt = datetimefunc.strptime(start, fmt)
		end_dt = datetimefunc.strptime(end, fmt)
		date_array = []
		
		current_dt = start_dt 
		
		while(current_dt <= end_dt):
			#readable_dt = str(current_dt.month) + "/" + str(current_dt.day) + " " + str(current_dt.hour) + ":" + str(current_dt.minute)
			date_array.append(str(current_dt))
			current_dt += datetime.timedelta(seconds=910)
		return date_array
		
			
	
	# render the chart 
	def render(self):
		
		for line in self.chart_lines:
			self.chart.add_element(line)
			
		self.chart.x_axis = self.x_axis
		self.chart.y_axis = self.y_axis
		self.chart.title = self.title
		
		return(self.chart.render())

