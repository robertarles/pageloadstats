package com.citysearch.performance.PageLoadStatsPy.PageLoadStatsJava;

import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;

import com.mysql.jdbc.Connection;
import com.mysql.jdbc.Statement;

public class Database {
	
	protected static String dbServer;
	protected static String dbPort;
	protected static String dbName;
	protected static String dbUsername;
	protected static String dbPassword;
	
	 protected Connection openDb(){
		 String dbUrl = "jdbc:mysql://"+dbServer + ":" + dbPort + "/" + dbName;

		 try {

			 Class.forName("com.mysql.jdbc.Driver");
			 Connection con = (Connection) DriverManager.getConnection (dbUrl, dbUsername, dbPassword);

			 return con;
			 
		 }catch(Exception e){
			 System.out.println(e.getMessage());
			 return null;
		 }
	 }
 
	 protected boolean updateDb(String query){
		 Connection con = openDb();
		 ResultSet rs;
		 
		 if(con==null){
			 return false;
		 }
		 
		 try{
			 Statement stmt = (Statement)con.createStatement();
			 int sqlReturn = stmt.executeUpdate(query);
			 con.close();
		 }catch(SQLException e){
			 e.printStackTrace();
		 }
		 
		 return true;
	 }
	 
	 protected ResultSet queryDb(String query){
		 Connection con = openDb();
		 ResultSet rs = null;
		 ArrayList<String> targets = new ArrayList<String>();
		 
		 if(con==null){
			 return null;
		 }
		 
		 try{
			 Statement stmt = (Statement)con.createStatement();
			 rs = stmt.executeQuery(query);
			 while (rs.next()) {
				 String dbtime = rs.getString(1);
				 System.out.println("[INFO] queryDb() dbtime "+ dbtime);
				 targets.add(dbtime);
			}
	
			con.close();
		 }catch(SQLException e){
			 e.printStackTrace();
		 }
		 
		 return rs;
	 } 
	 public String createInsertStatement(String targetId, HashMap<String, String> statsMap) {
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

	public String getDefaultAlertId() {
		String defaultAlertId = "";
		try{
			 
			 Connection con;
			 ResultSet rs = null;
			 con = openDb();
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
	 /**
	  * Get a list of active targets, each list item is a hashmap of target info
	  * @return targets, list of hashmaps. ArrayList<<HashMap<String,String> 
	  */
	 public ArrayList<HashMap<String,String>> getTargets(){
		 ArrayList<HashMap<String,String>> targets = new ArrayList<HashMap<String,String>>();
		 Database db = new Database();
		 

		 String query = "SELECT id,url,type FROM target WHERE active=1;";
		 Connection con = db.openDb();
		 ResultSet rs = null;
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
		 System.out.println("[INFO] getTargetMap() retrieved " + dbUrl+ ", " + dbTargetId);
		return target;
	} 
	
 	public HashMap<String,String>  loadAppSettings(){
 		// read settings from db table (settings)
 		HashMap<String,String> settings = new HashMap<String,String>();
		 String query = "SELECT * from settings;";
		 Connection con = openDb();
		 ResultSet rs = null;
		 if(con==null){
			 return null;
		 }
		 // go through the list of settings
		 try{
			 Statement stmt = (Statement)con.createStatement();
			 rs = stmt.executeQuery(query);
			 while (rs.next()) {
				 if(rs.getString("sma_window_size") != null && rs.getString("sma_window_size").length() > 0){
					 settings.put( "smaWindowSize", rs.getString("sma_window_size") );
				 }
			 }
			 
		 }catch(Exception e){
			 //
			e.printStackTrace();
		 }
		 return settings;
 	}
}
