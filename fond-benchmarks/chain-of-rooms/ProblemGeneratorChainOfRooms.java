import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintStream;

/**
 * this is a problem generator, that created instances of the
 * chainOfRooms problem. those instances are not randomly, but
 * uniquely defined by the parameter n (number of rooms)
 * 
 * domain description: there is a chain of rooms, each two neighboring
 * rooms connected through one door: room-1 door-1 , ... room-n,
 * door-n, room-n+1 The goal is to get from room 1 to room n+1, using
 * the doors, which can be locked or unlocked.  Initially, all rooms
 * are dark, preventing the agent from seeing the doors. thus, before
 * using them he has to turn on the light (the light can only be
 * turned on when it was off before). turning on the light leads in
 * seeing the door of the room, which can be nondeterministically open
 * or closed.  if it's open, one can pass the door through the next
 * room. otherwise the door has to be unlocked before. unlocking a
 * door is even possible if it is already unlocked.  for this domain,
 * there exits a conformant plan, but also a nonconformant one.
 * 
 * @author Pascal Bercher
 */
public class ProblemGeneratorChainOfRooms {

    /* instance variables */
    
    /**
     * ls = line separator
     */
    private static String ls = "\n";
   
    /* methods */
    
    /**
     * the main method,
     * creates the problem instances.
     * @param args
     * @throws IOException 
     */
    public static void main(String[] args) throws IOException {

	/*
	 * change the values here !!
	 */
	int smallestProblemToCreate = 10;
	int largestProblemToCreate = 100;
	int step = 10;	//for example: step = 5 -> 5, 10, 15,...
	
	System.out.println("starting to create the problem instances");
	
	for(int i=smallestProblemToCreate ; i<=largestProblemToCreate ; i+=step){
	    createProblemFile(i);
	}
		
	System.out.println("finished creating the problem instances");
    }
    
    /**
     * creates the problem file
     * @param numberOfRooms equals n+1 (see domain description)
     * @throws IOException
     */
    private static void createProblemFile(int numberOfRooms) throws IOException{
	String problem=
	    "(define (problem chainOfRooms)"+ls+
            "  (:domain chainOfRooms)"+ls+
            "  (:objects ";
	for(int i=1 ; i<=numberOfRooms ; i++)
	    problem+="r"+i+" ";
    	problem+=
	    "- room)"+ls+
            "  (:init (agent_position r1)"+ls+
            "         (visited r1)"+ls;
	for(int i=1 ; i<numberOfRooms ; i++)
	    problem+="         (light_off r"+i+")"+ls;
	for(int i=1 ; i<numberOfRooms ; i++)
	    problem+="         (adjacent r"+i+" r"+(i+1)+")"+ls;		
	problem+=
	    "  )"+ls+
	    "  (:goal (and (visited r1)"+ls;
	for(int i=2 ; i<=numberOfRooms ; i++)
	    problem+="              (visited r"+i+")"+ls;
	problem+=
	    "         )"+ls+
	    "  )"+ls+
	    ")";

	File problemFile = new File(System.getProperty("user.dir")+"/"+"p"+numberOfRooms+".pddl");
	problemFile.createNewFile();
	PrintStream output = new PrintStream(problemFile);
	
	output.println(problem);
	output.close();
    }
}
