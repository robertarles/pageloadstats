package com.citysearch.performance.PageLoadStatsPy.PageLoadStatsJava;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Date;
import java.util.HashMap;

import com.citysearch.performance.utils.SimpleSendmail;
import com.mysql.jdbc.Connection;
import com.mysql.jdbc.Statement;

public class Alert {
	
	Database db;
	
	// a list of variables that should be assigned in the properties file
	protected static String smtpServer;
	protected static String smtpUser;
	protected static String smtpPassword;
	protected static String plsWebHost;
	protected static String alertSubjectText = "ALERT PageLoadStats ";
	
	
	protected static double SolrAlertShrinkLimit = -0.1;	// default for Solr shrinkage percent, overridden by setting from sql settings tbl
	protected static double solrAlertGrowthLimit = +0.1;	// default for Solr growth percent, overridden by setting from sql settings tbl
	protected static final int SOLR_AVG_WINDOW = 5;	// how much history to use for average when calculating index percent change
	
	public Alert(){
		db = new Database();
	}
	/**
	  * Given a target id and a hashmap of its current data, send an alert if needed.
	  * @param targetId 
	  * @param statsMap
	  * @return
	  */
	 protected boolean checkForAlertConditions(String targetId, HashMap<String,String> statsMap, int avg){
		 
		 if( ! statsMap.containsKey("page_load_time")){ return false;} // failed to get a map of target data
		 String pageLoadTime = statsMap.get("page_load_time");
		 String limitHigh = "99999999";
		 // query to get active alerts applied to this target
		 String query = 
				 "SELECT * FROM target_alert ta join alert a on a.id = ta.alert_id join target t on t.id = ta.target_id  WHERE a.active = 1 AND ta.active=1 AND ta.target_id = " 
						 + Integer.valueOf(targetId);
		 Connection con = db.openDb();
		 ResultSet rs = null;
		 
		 if(con==null){
			 return false;
		 }
		 // go through the list of alerts that might apply, check against statsMap,  and alert as configured
		 try{
			 Statement stmt = (Statement)con.createStatement();
			 rs = stmt.executeQuery(query);
			 while (rs.next()) {
				 String targetType = "";
				 String resultCount = "";
				 try{
					 targetType = rs.getString("type");
					 resultCount = statsMap.get("result_count");
				 }catch(Exception e){
					 e.printStackTrace();
				 }
				 limitHigh= rs.getString("limit_high");	 // test for failure
				 String targetUrl = rs.getString("url");
				 String alertDefId = rs.getString("alert_id");
				 String targetTags = rs.getString("tags");
				 // if both the average load time and current load time are above alert level, send an email
				 if( (avg > Integer.valueOf(limitHigh)) && (Integer.valueOf(pageLoadTime) > Integer.valueOf(limitHigh)) ){
					 String alertText = "Failure for target (id " + targetId + ") "+targetUrl+ "<br/>";
					 alertText += "time limit = " + limitHigh + "ms<br/>";
					 alertText += "load time = " + pageLoadTime + "ms<br/>";
					 alertText += "avg load time is now "+avg+"ms<br/>";
					 alertText += "<a href='"+plsWebHost + "?url_filter="+targetId+"&limit=48'>**see the latest stats**</a></br>";
					 alertText += "<h3>dump of collected info:</h3>";
					 for(String key: statsMap.keySet()){
						 alertText += key + ": \t"+ statsMap.get(key) + "<br/>";
					 }
					 String alertSubjectTextAppended = alertSubjectText + " (id "+ targetId + ") tags("+targetTags+")";
					 boolean messageSent = send(alertDefId, alertSubjectTextAppended, alertText);
					 if(messageSent == false){
						 // text alert AND log an error here!
						 System.out.println("[FAILURE] Solr performance alert triggered, but email failed to send.");
					 }
				 }
				 // is this a solr server test?
				 if(targetType==null) targetType="";
				 if(resultCount != null && targetType.toLowerCase().equals("solr")){
					 if(Integer.valueOf(resultCount)==0){}
					 // get an average of recent result counts to check current result count against.
					 String sqlQuery = "select result_count from stat where target_id = "+targetId+" and result_count > 0 order by timestamp desc limit "+ SOLR_AVG_WINDOW;
					 Connection rccon = db.openDb();
					 Statement rcstmt = (Statement)rccon.createStatement();
					 ResultSet rcrs;
					 rcrs = rcstmt.executeQuery(sqlQuery);
					 int resultCountSum = 0;
					 int resultCountAvg = 0;
					 int resultCountRows = 0;
					 while (rcrs.next()) {
						 resultCountSum += Integer.valueOf(rcrs.getString("result_count"));
						 resultCountRows++;
					 }
					 resultCountAvg = resultCountSum / resultCountRows;
					 // send an alert if the result count has varied more than the rules allow for
					 double chg = Double.valueOf(resultCount) - resultCountAvg;
					 double percentChange = chg/resultCountAvg;
					 if( percentChange > Alert.solrAlertGrowthLimit || percentChange < Alert.SolrAlertShrinkLimit ){
						 String alertText = "Failure for SOLR target (id " + targetId + ") "+targetUrl+ "<br/><br/>";
						 alertText += "percent change range is set at " + (Alert.SolrAlertShrinkLimit*100) + "% to " + (Alert.solrAlertGrowthLimit*100) + "%<br/>";
						 alertText += "recent average is " + resultCountAvg + " results returned<br/>";
						 alertText += "this test returned " + resultCount + " results<br/>";
						 String changeSign = " DOWN ";
						 if(Float.valueOf(resultCount) > Float.valueOf(resultCountAvg) ){
							 changeSign = " UP ";
						 }
						 alertText += "this result is " + changeSign + (percentChange*100) + "% of the recent average<br/>";
						 alertText += "<a href='"+plsWebHost + "/chart/"+targetId+"'>**see the latest stats**</a></br>";
						 alertText += "<h3>dump of collected info:</h3>";
						 for(String key: statsMap.keySet()){
							 alertText += key + ": \t"+ statsMap.get(key) + "<br/>";
						 }
						 String alertSubjectTextAppended = alertSubjectText + " SOLR RESULTS CHANGED (id "+ targetId + ")";
						 boolean messageSent = send(alertDefId, alertSubjectTextAppended, alertText);
						 if(messageSent == false){
							 // text alert AND log an error here!
							 System.out.println("[FAILURE] Solr results changed, alert triggered, but email failed to send.");
						 }
					 }
				 }
			 }
		}catch(Exception e){
			// whatever.  move on.
			e.printStackTrace();
		}
		 

		 // save if failed
		 
		 
		 
		 try {
			 con.close();
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		 
		 return true;
	 }
	 /**
	  * handles the actual alerting process (email or whatever else might be config'd)
	  * @param reportFromAddress
	  * @param alertSubjectTextAppended
	  * @param alertText
	  * @return
	  */
	 protected boolean send(String alertDefId, String alertSubjectTextAppended, String alertText){
		 String sqlQuery = "select * from alert_recipients ar join alert_alert_recipients aar on aar.alert_recipient_id = ar.id where ar.active = 1 and aar.alert_id = " +alertDefId;
		 Connection con = db.openDb();
		 ResultSet rs = null;	 
		 String recipientList="";
		 boolean sendStatus=true;
		 if(con==null){
			 return false;
		 }
		 // create a recipient list of those emails associated to the current alert_def
		 try{
			 BufferedWriter logfile = new BufferedWriter(new FileWriter(PageLoadStats.LOGFILE, true));
			 Statement stmt = (Statement)con.createStatement();
			 rs = stmt.executeQuery(sqlQuery);
			 while(rs.next()){
				 recipientList += rs.getString("email_address") + ";";
			 }

			sendStatus = SimpleSendmail.send(alertSubjectTextAppended, alertText, recipientList);
			logfile.write("[ALERT] "+ alertSubjectTextAppended+" : " +alertText+"\n");
			if(sendStatus == true ){
				System.out.println("[INFO] ALERT SENT.  mail successfully sent: "+sendStatus + "  '"+ alertSubjectTextAppended + "'" );
			}else{
				logfile.write("[FAIL] failed to send alert at "+ new Date().toString() + 
						" \n[FAIL] failed to send alert: " + alertSubjectTextAppended + 
						"\n[FAIL] failed to send alert" + alertText + "\n");
			}
			logfile.close();
		 }catch(Exception e){
			 e.printStackTrace();
		 }finally{
		 }
		return sendStatus;
	 }
	 
	 public void sendUnexpectedHttpResponseAlert(String url,HashMap<String, String> statsMap, String defaultAlertId) {
			String alertSubjectTextAppended = "";
			String alertText = "";
			
			if(statsMap.equals(null)){
				alertSubjectTextAppended = Alert.alertSubjectText + " (could not connect)";
				alertText = "Target: " + url + ": could not connect.";
			}else{
				alertSubjectTextAppended = Alert.alertSubjectText + " (status " + statsMap.get("error") + ")";
				alertText = "Target: " + url + " returned status: " + statsMap.get("error");
			}
			
			boolean messageSent = send(defaultAlertId, alertSubjectTextAppended, alertText);
			if(messageSent == false){
				// text alert AND log an error here!
				System.out.println("[FAILURE] Error. Alert triggered, but email failed to send.");
			}
		}


}
