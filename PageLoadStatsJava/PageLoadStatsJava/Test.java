package com.citysearch.performance.PageLoadStatsPy.PageLoadStatsJava;

import java.util.HashMap;


public class Test implements Runnable {

	private String url = "";
	private String targetId = "";
	private String type = "";
	
	public Test(String url, String targetId, String type){
		this.url = url;
		this.targetId = targetId;
		this.type = type;
	}
	 /**
	  * Gather data on the given target url, send alerts as needed.
	  * @param url
	  * @param targetId
	  * @param type
	  * @return
	  */
	 public HashMap<String,String> startTest(){
		 Target target = new Target();
		 Alert alert = new Alert();
		 Database db = new Database();
		 HashMap<String,String> settings = db.loadAppSettings();
		 HashMap<String,String> statsMap = target.getStats(url, type);
		 if(statsMap == null || ! statsMap.containsKey("html")){
			 return null;
		 }
		 boolean isTargetContentValid = target.verifyDocContent(targetId,statsMap.get("html"));
		 statsMap.remove("html"); // don't  save this into the db
		 if( ! isTargetContentValid){
			 statsMap.put("error", "page failed content check");
		 }
		 
		 // check first for an unexpected HTTP response
		 if(statsMap.containsKey("error") || statsMap.equals(null)){
			 alert.sendUnexpectedHttpResponseAlert(url, statsMap,  db.getDefaultAlertId());
			 statsMap.remove("error"); // error is not a valid field in the DB, this is covered by http_status
		 }else{
			 int smaWindowSize = Integer.valueOf( settings.get("smaWindowSize") );
			 alert.checkForAlertConditions(targetId, statsMap, target.getMovingAvgOf(targetId,smaWindowSize) );
		 }
		 
		 String insertStats = db.createInsertStatement(targetId, statsMap);
		 
		 db.updateDb(insertStats);


		//Test.printUrlStats(statsMap);
			
		 return statsMap;
	 }
	 
	 private static void printUrlStats(HashMap<String, String> statsMap) {
			 for(String key : statsMap.keySet()){ 
				 if( ! key.equals("html")){
					 System.out.printf("[INFO]%s %s %s\n", key,  statsMap.get(key), statsMap.get("url"));	 
			 	 }
			 }
		}
	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub

	}

	public void run() {
		startTest();
	}

}
