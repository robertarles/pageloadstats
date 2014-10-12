package com.citysearch.performance.PageLoadStatsPy.PageLoadStatsJava;

import java.sql.ResultSet;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpMethod;
import org.apache.commons.httpclient.methods.GetMethod;
import org.apache.commons.httpclient.params.HttpMethodParams;
import org.apache.commons.io.IOUtils;
import org.apache.commons.lang.StringEscapeUtils;

import com.mysql.jdbc.Connection;
import com.mysql.jdbc.Statement;

public class Target {	
	
	protected static final String SOLR_QTIME_LOCATOR = "<int name=\"QTime\">";
	protected static final String SOLR_NUMFOUND_LOCATOR = "numFound=\"";
	
	protected static Alert alert;
	protected static Database db;
	
	public Target(){
		alert = new Alert();
		db = new Database();
		
	}

	 /**
	  * Get a hashmap of information about the given target.
	  * @param url
	  * @param type
	  * @return
	  */
	 
	 public HashMap<String,String> getStats(String url, String type){
		 System.out.println("\n[INFO] Checking target: " + url);
		 String html = "";
		 HashMap<String,String> statsMap = new HashMap<String,String>();
		
		addRequestDateToMap(statsMap);
		 
		// used to record transaction start and stop times
		long startTimestamp;
		long endTimestamp;
		int connectionTimeout = 60000;
		
		 try{
			 HttpClient client = new HttpClient();
			 client.getParams().setParameter("http.socket.timeout", new Integer(connectionTimeout));
			 
			 setUseragent(type, client);
			 HttpMethod method = new GetMethod(url);
			 if(type.toLowerCase().equals("sentiment")) method.setRequestHeader("x-publisher","cs_reinvent");
			 
			 startTimestamp = System.currentTimeMillis();
			 // for solr queries, tack on the timestamp for troubleshooting
			 if(type.toLowerCase().equals("solr")){
				 url+="&csqatimestamp="+startTimestamp/1000L;
			 }

			 int responseCode = client.executeMethod(method);
			 endTimestamp = System.currentTimeMillis();
		
			 statsMap.put("http_status", Integer.toString(responseCode));
			 
			 if (responseCode != 200) {
			     System.out.println("[WARNING]   " + responseCode + " when attempting: " + url);
			     statsMap.put("page_load_time", null);
			     statsMap.put("error", Integer.toString(responseCode) );
			     if(statsMap.get("html")==null || statsMap.get("html").equals(""))
			    	 html = "http response was: "+ Integer.toString(responseCode);
			 }
			 html = StringEscapeUtils.unescapeHtml(IOUtils.toString(method.getResponseBodyAsStream(),"UTF-8"));
		 }catch(Exception e){
			 System.out.println("[FAILURE] Sending PageLoadStats ALERT connect failure message for target " + url);
			 String shortUrl = url.replaceAll("http://", "").substring(0,35);
			 //String shortUrl = url.substring(0, 10);
			 alert.send("6","ALERT PageLoadStats connect failure ("+shortUrl+")", "There may be a connection failure when contacting: " + url);
			 System.out.println(e.getMessage());
			 return null;
		 }

		String startTimeStamp = String.valueOf(startTimestamp/1000L);
		statsMap.put("timestamp", startTimeStamp);
		
		if( ! statsMap.containsKey("page_load_time")){
			long pageLoadTime = endTimestamp - startTimestamp;
			String pageLoadTimeString = String.valueOf(pageLoadTime);
			statsMap.put("page_load_time", pageLoadTimeString);
		}
		statsMap.put("url",url);
		statsMap.put("html", html);
		statsMap.putAll(getStatsFromHtml(html));
		// If there is an "elapsed time" in the header, use it overwriting any other collected data
		// for gifts.com, this header field is response-time
		responseTime = ""
		statsMap.put("elapsed", responseTime);
		 
		 System.out.println("[INFO] Target stats gathered.");
		 return statsMap;
	 }

	private void addRequestDateToMap(HashMap<String, String> statsMap) {
		DateFormat dateFormat = new SimpleDateFormat("yyyy/MM/dd HH:mm:ss");
		Date date = new Date();
		String requestDate = dateFormat.format(date);
		statsMap.put("request_date", requestDate);
	}

	private void setUseragent(String type, HttpClient client) {
		String mobileUserAgent= "Mozilla/5.0 (iPhone U CPU iPhone OS 4_3_3 like Mac OS X en-us) AppleWebKit/533.17.9 (KHTML,like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5";
		 
		//for mobile targets, set the useragent
		 if(type.toLowerCase().equals("mobile")){
			System.out.println();
			client.getParams().setParameter(HttpMethodParams.USER_AGENT, mobileUserAgent);
			System.out.println("[INFO] For this URL, Setting user-agent to " + mobileUserAgent);
		 }
	}	
	 
	 public HashMap<String,String> getStatsFromHtml(String html){
		// find the CS specific Data on the page
		 HashMap<String,String> pageStatsMap = new HashMap<String,String>();
		 String[] htmlLines = html.split("\n");
		 for (String line : htmlLines){
			pageStatsMap.putAll(getDocStatsMap(line));
		 }
		 return pageStatsMap;
	 }

	private HashMap<String, String> getDocStatsMap(String line) {
		HashMap<String, String> pageStatsMap = new HashMap<String,String>();
		if( line.contains("Elapsed: ")){
			if(line.contains("Cache Elapsed:")){
				// ignore this stat for now.
			}else{
				 // remove spaces then grab the number after the colon
				 // assumes a string like "Elapsed:      1234"
				 String val = line.replaceAll(" ", "").split(":")[1];
				 pageStatsMap.put("elapsed", val);
			}
		 }		 
		 if( line.contains("Elapsed2: ")){
			 // remove spaces then grab the number after the colon
			 // assumes a string like "Elapsed2:      1234-->" a comment close is inline
			 String val = line.replaceAll(" ", "").replaceAll("-->","").split(":")[1];
			 pageStatsMap.put("elapsed2", val);
		 }
		 if(line.contains("Tag: ")){
			 String val = line.replaceAll(" ", "").split(":")[1];
			 pageStatsMap.put("tag", val);
		 }
		 if(line.contains("Server: ")){
			 String val = line.replaceAll(" ", "").split(":")[1];
			 pageStatsMap.put("server", val);
		 }
		 if(line.contains("Request ID: ")){
			 String val = line.replaceAll(" ", "").split(":")[1];
			 pageStatsMap.put("request_id", val);
		 }
		 //
		 // citysearch solr specific data collection
		 //
		 if(line.contains(SOLR_QTIME_LOCATOR)){
			 // qTime node (query time)
			 String qTime = "";
			 String regex = "(?<="+SOLR_QTIME_LOCATOR+")[0-9]+";
			 Matcher m = Pattern.compile(regex).matcher(line);
			 while(m.find()){
				 qTime = m.group();
			 }
			 pageStatsMap.put("query_time", qTime);
		 }
		 if(line.contains(SOLR_NUMFOUND_LOCATOR)){
			 // solr results found
			 String regex = "(?<="+SOLR_NUMFOUND_LOCATOR+")[0-9]+";
			 Matcher m = Pattern.compile(regex).matcher(line);
			 String numFound = "";
			 while(m.find()){
				 numFound = m.group();
			 }
			 pageStatsMap.put("result_count", numFound);
		 }
		 return pageStatsMap;
	}

	 /**
	  * Does this target have regex's associated to it?  
	  * This function check to see if the target target has associated regex's  used to check the page for expected content.
	  * @param siteId
	  * @return
	  */
	 public boolean hasContentCheckAssociated(String siteId){
	
		 String sqlQuery = "select count(*) from find where site_id = " + siteId + " and active = 1";
		 Connection con = db.openDb();
		 
		 ResultSet rs = null;	 
		 try {
			Statement stmt = (Statement)con.createStatement();
			rs = stmt.executeQuery(sqlQuery);
			int rows = rs.getInt(0);
			if (rows > 0) {
				return true;
			}
		 }catch(Exception e){
			 e.printStackTrace();
		 } 
		 
		 return false;
	 }
	 /**
	  * Return any regex's associated to the target  
	  * This function returns regex's used to check the page for expected content.
	  * @param siteId
	  * @return
	  */
	 public ArrayList<HashMap<String,String>> getContentVerificationValues(String siteId){
		 ArrayList<HashMap<String,String>> findMaps = new ArrayList<HashMap<String,String>>();
		 String sqlQuery = "select * from find where target_id = " + siteId + " and active = 1";
		 Connection con = db.openDb();
		 
		 ResultSet rs = null;	 
		 try {
			Statement stmt = (Statement)con.createStatement();
			rs = stmt.executeQuery(sqlQuery);
			while(rs.next()){
				HashMap<String,String> findMap = new HashMap<String,String>();
				findMap.put("regex", rs.getString("regex"));
				findMap.put("present", rs.getString("present"));
				findMap.put("count", rs.getString("count"));
				findMap.put("operator", rs.getString("operator"));
				findMaps.add(findMap);
			}
		 }catch(Exception e){
			 e.printStackTrace();
			 return null;
		 } 
		 
		 return findMaps;
	 }
	 
	 
	 /**
	  * Using associated regex's (in the 'finds' table) check this page content.
	  * @param targetId
	  * @param sourceHtml
	  * @return
	  */ 
	 public boolean verifyDocContent(String targetId, String sourceHtml){
		 ArrayList<HashMap<String,String>> findMaps = getContentVerificationValues(targetId);
		 try{
			 for(HashMap<String,String> findMap: findMaps){
				 String regex = findMap.get("regex");
				 int targetCount = Integer.valueOf(findMap.get("count"));
				 int present = Integer.valueOf(findMap.get("present"));
				 String operator = findMap.get("operator");
				 int findCount = 0; // how many hits for this regex? 
				 
				 Matcher m = Pattern.compile(regex).matcher(sourceHtml);		 
				 while(m.find()){
					 //System.out.println("\n*************\nFOUND: " + m.group() +"\n****************\n");
					 findCount++;
				 }
				 
				 // if present was set to 0, the regex should fail
				 if(present == 0 && findCount > 0){
					 return false;
				 }
				 if(operator.equals(">")){
					 if( ! (findCount > targetCount)){
						 return false;
					 }
				 }else if (operator.equals("=")){
					 if(! (findCount == targetCount)){
						 return false;
					 }
				 }else if (operator.equals("<")){
					 if( ! (findCount < targetCount)){
						 return false;
					 }
				 }
			 }
		 }catch(Exception e){
			 System.out.println("[FAILURE] checkFinds() caught an exception");
			 return(false);
		 }
		 return true;
	 }
	 
	 
	 /**
	  * return the average page load time for targetId using the last avgOf results
	  * @param targetId
	  * @param windowSize
	  * @return the average
	  */
	 protected int getMovingAvgOf(String targetId, int windowSize){
		 int avg = 0;
		 int pageLoadTime = 0;
		 int resultsFound = 0, pageLoadSum = 0;
		 
		 String sqlQuery = "select page_load_time from stat where target_id = "+ targetId +
				 			" order by timestamp desc limit " + Integer.toString(windowSize);
		 Connection con = db.openDb();
		 ResultSet rs = null;	 
		 if(con==null){
			 return avg;
		 }
		 // go through the list of alerts that might apply, check against statsMap,  and alert as configured
		 try{
			 Statement stmt = (Statement)con.createStatement();
			 rs = stmt.executeQuery(sqlQuery);
			 while (rs.next()) {
				 resultsFound ++;
				 pageLoadTime = Integer.valueOf(rs.getString("page_load_time"));	 // test for failure
				 pageLoadSum += pageLoadTime;
			 }
			 // were there enough results to accomodate the request (e.g. only 2 when an average of 4 was requested)
			 if (resultsFound < windowSize) return 0;
			 avg = pageLoadSum / windowSize;
			 
		}catch(Exception e){
			// whatever.  move on.
		}
		 return avg;
	 }
	 


}
