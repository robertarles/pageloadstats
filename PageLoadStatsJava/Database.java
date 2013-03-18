package com.citysearch.performance.PageLoadStatsPy.PageLoadStatsJava;

import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;

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
				 System.out.println("[INFO] "+ dbtime);
				 targets.add(dbtime);
			}
	
			con.close();
		 }catch(SQLException e){
			 e.printStackTrace();
		 }
		 
		 return rs;
	 } 

}
