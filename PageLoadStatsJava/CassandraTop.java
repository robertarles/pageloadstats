package com.citysearch.performance.PageLoadStatsPy.PageLoadStatsJava;

//
///**
// * @author robert
// * based on example from DD
// *
// */
//
//import java.io.IOException;
//import java.util.ArrayList;
//import java.util.HashMap;
//import java.util.Iterator;
//import java.util.List;
//import java.util.Map;
//
//import me.prettyprint.cassandra.connection.LeastActiveBalancingPolicy;
//import me.prettyprint.cassandra.model.AllOneConsistencyLevelPolicy;
//import me.prettyprint.cassandra.serializers.StringSerializer;
//import me.prettyprint.cassandra.service.CassandraHostConfigurator;
//import me.prettyprint.cassandra.service.ExhaustedPolicy;
//import me.prettyprint.cassandra.service.FailoverPolicy;
//import me.prettyprint.hector.api.Cluster;
//import me.prettyprint.hector.api.Keyspace;
//import me.prettyprint.hector.api.beans.HSuperColumn;
//import me.prettyprint.hector.api.beans.SuperRow;
//import me.prettyprint.hector.api.beans.SuperRows;
//import me.prettyprint.hector.api.beans.SuperSlice;
//import me.prettyprint.hector.api.factory.HFactory;
//import me.prettyprint.hector.api.query.MultigetSuperSliceQuery;
//import me.prettyprint.hector.api.query.QueryResult;
//
public class CassandraTop {
//
//    private static StringSerializer stringSerializer = StringSerializer.get();
//    private static CassandraHostConfigurator cassandraHostConfigurator;
//    private static Cluster cluster;
//
//    public static void main(String[] args) throws IOException {
//    	ArrayList<String> listingIds = new ArrayList<String>();
//    	String key = "losangeles+Restaurants";
////    	if(args.length < 1){
////    		System.out.println("\nDid you supply a key as a parameter ?  e.g.  losangeles+pizza");
////    		System.exit(1);
////    	}
////    	
////    	String key = args[0]; //"losangeles+Restaurants";
//    	listingIds = getTop(key);
//    	
//    	for (String listingId : listingIds){
//    		System.out.println("ID: " + listingId);
//    	}
//    	
//    }
//    
//    public static ArrayList<String> getTop(String key){
//    	ArrayList<String> listingIds = new ArrayList<String>();
//        Map<String,String> AccessMap = new HashMap<String,String>();
//        AccessMap.put("username", "");
//        AccessMap.put("password", "");
//
//        String hosts = "aws1prdcsc1.csprod.ctgrd.com:9160,aws1prdcsc2.csprod.ctgrd.com:9160,aws1prdcsc3.csprod.ctgrd.com:9160,aws1prdcsc4.csprod.ctgrd.com:9160";
//
//        cassandraHostConfigurator = new CassandraHostConfigurator(hosts);
//        cassandraHostConfigurator.setAutoDiscoverHosts(true);
//        cassandraHostConfigurator.setMaxActive(100);
//        cassandraHostConfigurator.setMaxWaitTimeWhenExhausted(6000);
//        cassandraHostConfigurator.setCassandraThriftSocketTimeout(7000);
//        cassandraHostConfigurator.setExhaustedPolicy(ExhaustedPolicy.WHEN_EXHAUSTED_FAIL);
//        cassandraHostConfigurator.setLoadBalancingPolicy(new LeastActiveBalancingPolicy());
//
//        cluster = HFactory.getOrCreateCluster("ListingCluster",
//                cassandraHostConfigurator);
//        Keyspace keyspace = HFactory.createKeyspace("upp", cluster, new AllOneConsistencyLevelPolicy(),
//                FailoverPolicy.ON_FAIL_TRY_ALL_AVAILABLE, AccessMap);
//
//        
//
//        MultigetSuperSliceQuery<String, String, String, String> columnQuery =  HFactory.createMultigetSuperSliceQuery(keyspace,
//                stringSerializer, stringSerializer, stringSerializer, stringSerializer);
//
//        columnQuery.setRange(null, null, false, 52);
//        columnQuery.setColumnFamily("topcat").setKeys(key);
//
//        QueryResult<SuperRows<String, String, String, String>> result = columnQuery.execute();
//        SuperRows<String, String, String, String> rows = result.get();
//
//        Iterator<SuperRow<String, String, String, String>> iter = rows.iterator();
//
//        while (iter.hasNext()) {
//            SuperSlice<String, String, String> slice = iter.next().getSuperSlice();
//            List<HSuperColumn<String, String, String>> columnList = slice.getSuperColumns();
//            for (HSuperColumn<String, String, String> scolumn : columnList) {
//                //System.out.println(scolumn.getName());
//                listingIds.add(scolumn.getName());
//            }
//        }
//
//        cluster.getConnectionManager().shutdown();
//        return listingIds;
//    }
} 