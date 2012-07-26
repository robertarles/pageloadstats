from pyofc2 import *
import datetime
from datetime import datetime as datetimefunc
from pytz import timezone

class Pls_Chart(object):
	"""
	A chart object using open_flash_charts 2 via pyofc2
	"""
	
	def __init__(self):
		self.chart = open_flash_chart()
		self.chart_lines = []
		self.x_axis = x_axis()
		self.y_axis = y_axis()
		self.title = "Page Load Stats"
		self.line_width = 1
		
	
	def init_param_vars(self):
		"""
		get a list of url parameters
		"""
		param_string = self.url.split("?")[1]
		param_array = param_string.split("&")
		for param in param_array:
			key,value = param.split("=")
			print("%s : %s" % (key,value) )
			
	
	def add_line(self, name, legend_entry, values, dates, color):
		"""
		Add a line to this chart object
		return boolean as fail/succeed message
		"""
		chart_line = self.get_line(name, legend_entry, values, dates, color)
		self.chart_lines.append(chart_line)
		return(True)
	
	
	def get_line(self, name, legend_entry, values, dates, color):
		"""
		Create and return a line object
		return a pyOfc2 line object
		"""
		chart_line = line()
		dots = []
		fmt1 = "%Y/%m/%d %H:%M:%S"
		fmt2 = "%Y-%m-%d %H:%M:%S"
		i=0
		date_end_index = len(values)
		for i in range(date_end_index):
			dateStr = ""
			if(i < len(dates)):
				dateStr = dates[i]
			txt = name + "<br>" + dateStr + "<br>" + "#val#ms"
			dot = dot_value(value=values[i], tip=txt)
			# if the dots date value is more than 15 minutes (the chart resolution) ahead of 
			# this point on the x-axis of the chart plop, try the next spot
			datestr1 = dateStr
			dot_date = datetimefunc.strptime(datestr1, fmt1)
			if(i < len(self.date_array)):
				datestr2 = self.date_array[i]
			xaxis_date = datetimefunc.strptime(datestr2, fmt2)
			
			delta = dot_date - xaxis_date
			
			if(delta > datetime.timedelta(minutes=15)): # is this data later than the current spot (some data missing, likely)
				pass

			if(dot_date > xaxis_date): # do we have more data for the previous date spot on the chart?
				pass
			
			dots.append(dot)
		
		chart_line.values = dots
		chart_line.colour = color
		chart_line.text = legend_entry
		chart_line.width = self.line_width
		
		return(chart_line)
	
	
	def set_x_axis(self, start, end, interval):
		"""
		create and return an x-axis for a date range, defaulting to a 15 minute interval
		"""
		self.x_axis = self.get_x_axis(start, end, interval)
		
		
	def get_x_axis_array(self, start, end, interval):
		"""
		create and return an x-axis for a date range
		@param start: The first date on the chart
		@param end: The last date on the chart
		@param interval: the number of minutes desired between the x-axis points (the chart granularity
		"""
		fmt = "%Y/%m/%d %H:%M:%S"
		start_dt = datetimefunc.strptime(start, fmt)
		end_dt = datetimefunc.strptime(end, fmt)
		date_array = []
				
		current_dt = start_dt - datetime.timedelta(minutes=start_dt.minute % 15,
                             seconds=start_dt.second,
                             microseconds=start_dt.microsecond)
		
		while(current_dt <= end_dt):
			#readable_dt = str(current_dt.month) + "/" + str(current_dt.day) + " " + str(current_dt.hour) + ":" + str(current_dt.minute)
			date_array.append(str(current_dt))
			current_dt += datetime.timedelta(seconds=900)
		date_array.append(str(current_dt))
		self.date_array = date_array
		return date_array
		
			
	def render(self):
		"""
		render the chart as json output
		x and y axis must already be defined in self.x_axis and self.y_axis
		"""
		for line in self.chart_lines:
			self.chart.add_element(line)
			
		self.chart.x_axis = self.x_axis
		self.chart.y_axis = self.y_axis
		self.chart.title = self.title
		
		return(self.chart.render())

