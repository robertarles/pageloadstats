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
	
	HashMap<String,String> settings = new HashMap<String,String>();
	
	public PageLoadStats() {
	}
	
	public static void main(String[] args){
		PageLoadStats pls = new PageLoadStats();
		String url = null;
		ArrayList<HashMap<String,String>> targetDataList = new ArrayList<HashMap<String,String>>();

		pls.loadPropertiesFromFile();
		targetDataList = getTargetList(args, pls);
		for(HashMap<String,String>targetData : targetDataList) {
			if(targetData.get("type")==null) 
				targetData.put("type","");
			Test test = new Test(targetData.get("url"), targetData.get("targetId"), targetData.get("type"));
			Thread testThread = new  Thread( new Test( targetData.get("url"), targetData.get("targetId"), targetData.get("type")) );
			testThread.start();  // TODO implement as thread launch
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
		Database db = new Database();
		targets = db.getTargets();
		 if(targets==null){
			HashMap<String,String> target = new HashMap<String,String>();
			target.put("url", "http://losangeles.citysearch.com");
			targets.add(target);
		 }
		return targets;
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


}
