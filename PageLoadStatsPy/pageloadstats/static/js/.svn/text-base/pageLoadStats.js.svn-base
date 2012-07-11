		
	/**
	 * set the form defaults to reflect the values given in the url
	 */
	function updateFormChoices(){
				
		urlVars = getUrlVars();
		//console.log(urlVars);
		
		if(urlVars["limit"] != null){
			$("#select_recent").val(urlVars["limit"]).attr("selected",true);
		}			
		if(urlVars["url_filter"] != null){
			$("#select_recent_url").val( unescape(urlVars["url_filter"]) ).attr("selected",true);
			$("#select_range_url").val( unescape(urlVars["url_filter"]) ).attr("selected",true);
		}			
		if(urlVars["start_time"] != null){
			startTimeStamp = unescape(urlVars["start_time"]);
			startDate = new Date(startTimeStamp*1000);
			year = startDate.getFullYear();
			month = startDate.getMonth() +1;
			day = startDate.getDate();
			hour = startDate.getHours();
			if(hour<10) hour = "0" + hour;
			minute = startDate.getMinutes();
			if(minute<10) minute = "0" + minute;
			$("#start_date_picker").val( month+"/"+day+"/"+year+" "+hour+":"+minute ).attr("selected",true);
			//console.log(unescape(urlVars["start_time"]));
		}			
		if(urlVars["end_time"] != null){
			endTimeStamp = unescape(urlVars["end_time"]);
			endDate = new Date(endTimeStamp*1000);
			year = endDate.getFullYear();
			month = endDate.getMonth() +1;
			day = endDate.getDate();
			hour = endDate.getHours();
			if(hour<10) hour = "0" + hour;
			minute = endDate.getMinutes();
			if(minute<10) minute = "0" + minute;
			$("#end_date_picker").val( month+"/"+day+"/"+year+" "+hour+":"+minute ).attr("selected",true);
			//console.log(unescape(urlVars["end_time"]));
		}
		if(urlVars["target_search_term"] != null){
			$("#target_search_term").val( unescape(urlVars["target_search_term"]));
		}
	}
		
	/**
	 * Read a page's GET URL variables and return them as an associative array.
	 */ 
	function getUrlVars(){
		var vars = [], hash;
		var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
		for(var i = 0; i < hashes.length; i++)
		{
			hash = hashes[i].split('=');
			vars.push(hash[0]);
			vars[hash[0]] = hash[1];
		}
		return vars;
	}
	
	/**
	 * grab the form inputs and request a custom chart of recent data
	 */ 
	function displayRecentChart(){
		var timeSelect = 	window.document.getElementById('select_recent');
		var urlSelect = 	window.document.getElementById('select_recent_url');
		var limit = 		timeSelect.options[timeSelect.selectedIndex].value;
		var urlFilter = 	urlSelect.options[urlSelect.selectedIndex].value;
		
		urlFilter = encodeURIComponent(urlFilter);
				
		var url = location.href;
		var url_parts = url.split("?");
		var main_url = url_parts[0];	
		
		//console.log(main_url+"?url_filter="+urlFilter+"&limit="+limit);
		window.open(main_url+"?url_filter="+urlFilter+"&limit="+limit,"_top");
	}		
	
	/**
	 * grab the form inputs and request a custom chart of data from requested date range
	 */ 
	function displayRangeChart(){
		var startTimeString = 	window.document.getElementById('start_date_picker').value;
		var endTimeString = 	window.document.getElementById('end_date_picker').value;
		var urlSelect = 	window.document.getElementById('select_range_url');
		var urlFilter = 	urlSelect.options[urlSelect.selectedIndex].value;
		
		var startStamp = getTimestamp(startTimeString)/1000;
		var endStamp = getTimestamp(endTimeString)/1000;
		//alert(startStamp+ " NOW= "  + Date.now());
		
		var url = location.href;
		var url_parts = url.split("?");
		var main_url = url_parts[0];	
		
		console.log(main_url+"?url_filter="+urlFilter+"&start_time="+startStamp+"&end_time="+endStamp);
		window.open(main_url+"?url_filter="+urlFilter+"&start_time="+startStamp+"&end_time="+endStamp,"_top");
	}	
	
	/**
	 * grab the form inputs and request a custom chart of data from requested date range
	 */ 
	function displayMultiChart(){
		var startTimeString = 	window.document.getElementById('start_date_picker').value;
		var endTimeString = 	window.document.getElementById('end_date_picker').value;
		var searchTerm = 	window.document.getElementById('target_search_term').value;
		
		var startStamp = getTimestamp(startTimeString)/1000;
		var endStamp = getTimestamp(endTimeString)/1000;
		//alert(startStamp+ " NOW= "  + Date.now());
		
		var url = location.href;
		var url_parts = url.split("?");
		var main_url = url_parts[0];	
		
		console.log(main_url+"?target_search_term="+searchTerm+"&start_time="+startStamp+"&end_time="+endStamp);
		window.open(main_url+"?target_search_term="+searchTerm+"&start_time="+startStamp+"&end_time="+endStamp,"_top");
	}
	
	function getTimestamp(timeString){
		
		var timestamp = Date.parse(timeString);
		//var date = new Date();
		
		//var timezoneOffsetMS = date.getTimezoneOffset() * 60 * 1000; // convert the offset from minutes to milliseconds
		
		//timestamp = timestamp - timezoneOffsetMS;
		
		return timestamp;
	}
	
	function dotClickHandler(){
		$("#messageArea").text("dotClickHandler called");
	}
		
