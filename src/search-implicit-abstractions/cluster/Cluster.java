package cluster;

import weka.core.DistanceFunction;
import weka.core.EuclideanDistance;
import weka.core.Instances;
import weka.core.Instance;
import weka.core.converters.ArffLoader;
import weka.clusterers.*;
import weka.filters.Filter;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.util.*;

public class Cluster {
	
	public static void main(String[] args) {
		System.out.println("ARFF file: " + args[0]);
		int k = Integer.parseInt(args[1]);		
		System.out.println("k = " + k);
		System.out.println("output file: " + args[2]);
		
		ArffLoader loader = new ArffLoader();		
		
		try {
			File file = new File(args[0]);			
			
			loader.setFile(file);
			Instances inst = loader.getDataSet();
			System.out.println("Number of instances: " + inst.numInstances());
			System.out.println("Number of attributes: " + inst.numAttributes());
			
			UltraKMedoids cluster = new UltraKMedoids();
			cluster.setSelectedClusterCount(k);
			
			//SimpleKMeans cluster = new SimpleKMeans();
			//DistanceFunction dist = new EuclideanDistance();
			//cluster.setNumClusters(k);			
			//cluster.setDistanceFunction(dist);
			
			cluster.buildClusterer(inst);
			
			System.out.println("Number of clusters: " + cluster.numberOfClusters());
			//System.out.println(cluster);
			List<Instance> medoids = cluster.getMedoids();
								
			for (int i = 0; i < medoids.size(); i++) {
				Instance cent = medoids.get(i);				
				System.out.println(i + ": " + cent);				
			}
			
			
			FileWriter fw = new FileWriter(args[2]);
			BufferedWriter bw = new BufferedWriter(fw);
			
			bw.write("begin_centroids\n");
			bw.write(medoids.size() + "\n");
			for (int i = 0; i < medoids.size(); i++) {
				Instance cent = medoids.get(i);
				bw.write(cent.stringValue(0) + "\n");				
				/*
				bw.write("begin_state\n");
				for (int j = 0; j < cent.numAttributes(); j++) {
					bw.write((int) cent.value(j)  + "\n"); 
				}
				bw.write("end_state\n");
				*/
			}
			bw.write("end_centroids\n");
			bw.close();			
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

}
