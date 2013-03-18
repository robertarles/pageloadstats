package com.citysearch.performance.PageLoadStatsPy.PageLoadStatsJava;

import com.citysearch.performance.PageLoadStatsPy.PageLoadStatsJava.Target;
import com.mysql.jdbc.Connection;
import com.mysql.jdbc.Statement;

import java.io.IOException;
import java.io.InputStream;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Properties;

public class PageLoadStats {

    protected static String reportFromAddress =    	"PageLoadStats@citysearch.com";
	protected static String reportToAddress =      	"robert.arles@citygridmedia.com";
	protected static String reportSubjectText =    	"PageLoadStats report";
	

	protected static int smaWindowSize = 96;  // default for the simple moving avg calc, overridden by setting from sql settings tbl


	protected static final String LOGFILE = "pls.log";
	
	protected Properties properties = new Properties();
	private static final String PROPERTIES_FILE = "app.properties";


	
	// a place to store error messages during testing
	protected static ArrayList<String> errorList = new ArrayList<String>();
	
	// a place to store urls for follow up
	protected static ArrayList<HashMap<String,String>> failedChecks = new ArrayList<HashMap<String,String>>();
	
	private Database db;
	private Target target;
	private Alert alert;

	public PageLoadStats() {
		db = new Database();
		target = new Target();
		alert = new Alert();
	}
	
	public static void main(String[] args){
		PageLoadStats pls = new PageLoadStats();
		String url = null;
		ArrayList<HashMap<String,String>> targets = new ArrayList<HashMap<String,String>>();

		pls.loadPropertiesFromFile();
		pls.loadAppSettingsFromDB();
		targets = getTargetList(args, pls);
		for(HashMap<String,String>target : targets) {
			if(target.get("type")==null) 
				target.put("type","");	
			 pls.checkUrl(target.get("url"), target.get("targetId"), target.get("type"));
		}
	}

	private static ArrayList<HashMap<String, String>> getTargetList(String[] args, PageLoadStats pls) {
		ArrayList<HashMap<String, String>> targets = new ArrayList<HashMap<String,String>>();
		//  if no url is provided at the command line, pull a set of target to check from the DB
		 if( args.length > 0l &&  ( args[0].contains("http://") || args[1].contains("https://") ) ){
			HashMap<String,String> target = new HashMap<String,String>();
			target.put("url", args[0]);
			targets.add(target);
		 }else{
			 targets = getTargetsFromDb(pls);
		 }
		return targets;
	}

	private static ArrayList<HashMap<String, String>> getTargetsFromDb(PageLoadStats pls) {
		ArrayList<HashMap<String, String>> targets;
		targets = pls.getTargets();
		 // fallback default...
		 if(targets==null){
			HashMap<String,String> target = new HashMap<String,String>();
			target.put("url", "http://losangeles.citysearch.com");
			targets.add(target);
		 }
		return targets;
	}
 
 /**
  * Shortcut for checkUrl(String url, String targetId, String type)
  * @param url
  * @return
  */
 private boolean checkUrl(String url){
	 return checkUrl(url,"0", "");
 }
 
 /**
  * Gather data on the given target url, send alerts as needed.
  * @param url
  * @param targetId
  * @param type
  * @return
  */
 private boolean checkUrl(String url, String targetId, String type){
	 HashMap<String,String> statsMap = target.getStats(url, type);
	 String defaultAlertId = getDefaultAlertId();
	 
	 boolean isTargetContentValid = false;
	 if(statsMap == null || ! statsMap.containsKey("html")){
		 return false;
	 }

	 isTargetContentValid = target.verifyDocContent(targetId,statsMap.get("html"));
	 
	 statsMap.remove("html"); // we don't want to try to save this into the db
	 // TODO: DEBUG this message should be handled in checkfinds()
	 if( ! isTargetContentValid){
		 statsMap.put("error", "page failed content check");
	 }
	 
	 // check first for an unexpected HTTP response
	 if(statsMap.containsKey("error") || statsMap.equals(null)){
		 sendUnexpectedHttpResponseAlert(url, statsMap, defaultAlertId);
		 statsMap.remove("error"); // error is not a valid field in the DB, this is covered by http_status
	 }else{
		 alert.checkForAlertConditions(targetId, statsMap, target.getMovingAvgOf(targetId,smaWindowSize));
	 }
	 
	 String insertStats = createInsertStatement(targetId, statsMap);
	 
	 db.updateDb(insertStats);
	 
	 printUrlStats(statsMap);

	 return true;
 }

private String getDefaultAlertId() {
	String defaultAlertId = "";
	try{
		 
		 Connection con;
		 ResultSet rs = null;
		 con = db.openDb();
		 String query = "Select * from alert where name = 'default' limit 1";
		 Statement stmt = (Statement)con.createStatement();
		 rs = stmt.executeQuery(query);
		 while (rs.next()) {
			 defaultAlertId = rs.getString("id");
		}

		con.close();
	}catch (Exception e) {
		e.printStackTrace();
	}
	return defaultAlertId;
}

private void printUrlStats(HashMap<String, String> statsMap) {
	System.out.println();
	 for(String key : statsMap.keySet()){ 
		 if( ! key.equals("html")){
			 System.out.printf("[INFO] %-25s %s\n", key,  statsMap.get(key));	 
	 	 }
	 }
}


private void sendUnexpectedHttpResponseAlert(String url,HashMap<String, String> statsMap, String defaultAlertId) {
	String alertSubjectTextAppended = "";
	String alertText = "";
	
	if(statsMap.equals(null)){
		alertSubjectTextAppended = Alert.alertSubjectText + " (could not connect)";
		alertText = "Target: " + url + ": could not connect.";
	}else{
		alertSubjectTextAppended = Alert.alertSubjectText + " (status " + statsMap.get("error") + ")";
		alertText = "Target: " + url + " returned status: " + statsMap.get("error");
	}
	
	boolean messageSent = alert.send(defaultAlertId, alertSubjectTextAppended, alertText);
	if(messageSent == false){
		// text alert AND log an error here!
		System.out.println("[FAILURE] Error. Alert triggered, but email failed to send.");
	}
}
 

private String createInsertStatement(String targetId, HashMap<String, String> statsMap) {
	String insert = "insert into stat ";
	String fields = " (target_id,";
	 String values = " values ('"+targetId+"',";
	 // build the values and fields part of the sql update query
	 
	 for(String key: statsMap.keySet()){
		 String value = "";
		 if(statsMap.get(key)==null){
			 value = "null";
		 }else{
			 value = "'"+statsMap.get(key)+"'";
		 }
		 fields = fields + "" + key + ",";
		 values = values + value + ",";
	 }
	 fields = fields.substring(0, fields.length()-1) + ") " ; // remove the last comma
	 values = values.substring(0, values.length()-1) + "); "; // remove the last comma
	
	 insert = insert + fields + values;
	return insert;
}
 

  
 /**
  * Get a list of active targets, each list item is a hashmap of target info
  * @return targets, list of hashmaps. ArrayList<<HashMap<String,String> 
  */
 private ArrayList<HashMap<String,String>> getTargets(){
	 String query = "SELECT id,url,type FROM target WHERE active=1;";
	 Connection con = db.openDb();
	 ResultSet rs = null;
	 ArrayList<HashMap<String,String>> targets = new ArrayList<HashMap<String,String>>();
	 
	 if(con==null){
		 return null;
	 }
	 
	 try{
		 Statement stmt = (Statement)con.createStatement();
		 rs = stmt.executeQuery(query);
		 while (rs.next()) {
			 targets.add(getTargetMap(rs));
		}

		 con.close();
	 }catch(SQLException e){
		 e.printStackTrace();
	 }
	 
	 return targets;
 }

private HashMap<String, String> getTargetMap(ResultSet rs) throws SQLException {
	String dbTargetId = rs.getString(1);
	 String  dbUrl= rs.getString(2);
	 String  type= rs.getString(3);
	 HashMap<String,String> target = new HashMap<String,String>();
	 target.put("targetId",dbTargetId);
	 target.put("url", dbUrl);
	 target.put("type", type);
	 System.out.println("[INFO] " + dbUrl+ ", " + dbTargetId);
	return target;
} 
 
 	private boolean loadPropertiesFromFile(){
		// Read properties file.
		 InputStream in = getClass().getResourceAsStream(PROPERTIES_FILE);
		 try {
			properties.load(in);
			 in.close();
		} catch (IOException e) {
			e.printStackTrace();
			return false;
		}
	
		Database.dbServer = properties.getProperty("db.server");
		Database.dbPort = properties.getProperty("db.port");
		Database.dbName = properties.getProperty("db.name");
		Database.dbUsername = properties.getProperty("db.username");
		Database.dbPassword = properties.getProperty("db.password");
		
	
		Alert.smtpServer = properties.getProperty("smtp.server");
		Alert.smtpUser = properties.getProperty("smtp.user");
		Alert.smtpPassword = properties.getProperty("smtp.password");
		
		Alert.plsWebHost = properties.getProperty("plsWeb.host");
		
		 return true;
 	}

 	private boolean loadAppSettingsFromDB(){
 		// read settings from db table (settings)
		 String query = "SELECT * from settings;";
		 Connection con = db.openDb();
		 ResultSet rs = null;
		 if(con==null){
			 return false;
		 }
		 // go through the list of settings
		 try{
			 Statement stmt = (Statement)con.createStatement();
			 rs = stmt.executeQuery(query);
			 while (rs.next()) {
				 if(rs.getString("sma_window_size") != null && rs.getString("sma_window_size").length() > 0){
					 smaWindowSize = Integer.valueOf(rs.getString("sma_window_size"));
				 }
				 if(rs.getString("alert_solr_shrink_limit") != null && rs.getString("alert_solr_shrink_limit").length() > 0){
					 Alert.SolrAlertShrinkLimit = Double.valueOf(rs.getString("alert_solr_shrink_limit"));
				 }
				 if(rs.getString("alert_solr_growth_limit") != null && rs.getString("alert_solr_growth_limit").length() > 0){
					 Alert.solrAlertGrowthLimit = Double.valueOf(rs.getString("alert_solr_growth_limit"));
				 }
			 }
			 
		 }catch(Exception e){
			 //
			e.printStackTrace();
		 }
		 System.out.println("[INFO] SMA: " + smaWindowSize);
		 return true;
 	}
}
