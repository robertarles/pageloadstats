class Pls_Chart(object):
	
	def __init__(self, url):
		self.url = url
		
	def print_args(self):
		print self.url
	
		
	def init_param_vars(self):
		param_string = self.url.split("?")[1]
		param_array = param_string.split("&")
		for param in param_array:
			key,value = param.split("=")
			print( "%s : %s" % (key,value) )