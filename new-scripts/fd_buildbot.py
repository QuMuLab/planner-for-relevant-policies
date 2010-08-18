from buildbot.steps.shell import ShellCommand
import os

class FastDownwardTestStep(ShellCommand):
    """This class is a Buildbot Build Step that runs a given set of configurations 
    of Fast Downward on a suite of problems (suite), and records the results in 
    build step properties
    """
    def __init__(self, name, configs, suite, **kwargs):
        """
        Initializes this build step 
        
        @type  name: string
        @param name: The name of this test step (used for directory)
        
        @type  configs: list of strings
        @param configs: The configurations to run (see downward-experiments.py)
        
        @type  suite: list of strings
        @param suite: The suite of problems to run on (see downward-experiments.py)
        """
        ShellCommand.__init__(self, **kwargs)
        self.name = name
        self.configs = configs
        self.suite = suite

        self.command = ["./run-fd-test",name, configs, suite]

        self.addFactoryArguments(name=name,
                                 configs=configs,
                                 suite=suite)
        
    def commandComplete(self, cmd):       
        properties = ['expanded', 'total_time', 'solved']
        base_dir = self.name + "-eval"        
        for config in os.listdir(base_dir):    
            for domain in os.listdir(os.path.join(base_dir, config)):
                for problem in os.listdir(os.path.join(base_dir, config, domain)):
                    file = os.path.join(base_dir, config, domain, problem, 'properties')
                    dict = {}                                
                    execfile(file, dict)
                    for prop in properties:
                        self.setProperty(prop + "-" + config + "-" + domain + "-" + problem, dict[prop])
                        #print prop + "-" + config + "-" + domain + "-" + problem, dict[prop]
                    os.remove(file)
                    os.rmdir(os.path.join(base_dir, config, domain, problem))                            
                os.rmdir(os.path.join(base_dir, config, domain))
            os.rmdir(os.path.join(base_dir, config))
        os.rmdir(os.path.join(base_dir))


    
    
    
    
        
