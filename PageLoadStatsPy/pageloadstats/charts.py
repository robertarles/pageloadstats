from pyofc2 import *
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
	
	## get a list of url parameters
	def init_param_vars(self):
		param_string = self.url.split("?")[1]
		param_array = param_string.split("&")
		for param in param_array:
			key,value = param.split("=")
			print("%s : %s" % (key,value) )

	def add_line(self, name, values, dates, color):
		chart_line = self.get_line(name, values, dates, color)
		self.chart_lines.append(chart_line)
		return(True)
	
	def get_line(self, name, values, dates, color):
		chart_line = line()
		dots = []
		for elapsed_time in values:
			txt = "elapsed(#val#ms)"
			dot = dot_value(value=elapsed_time, tip=txt)
			dots.append(dot)
		chart_line.values = dots
		chart_line.colour = color
		chart_line.text = name
		
		return(chart_line)
	
	##
	# render the chart 
	def render(self):
		
		for line in self.chart_lines:
			self.chart.add_element(line)
			
		self.chart.x_axis = self.x_axis
		self.chart.y_axis = self.y_axis
		self.chart.title = self.title
		
		return(self.chart.render())