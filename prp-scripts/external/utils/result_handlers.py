##########################
# Utilities for handling #
#  experimental results. #
##########################

class Result(object):
    """
      Class to represent the result of a single experimental run.
    """
    
    def __init__(self, id, single_args, parameter_settings):
        self.id = id
        self.trial = 1
        self.command = ''
        self.output_file = ''
        self.error_file = ''
        
        self.single_args = {}
        for setting in single_args:
            setting = setting.split("KRDELIMNARF")
            if len(setting) == 1:
                setting.append('')
            
            self.single_args[setting[0]] = setting[1]
        
        self.parameters = {}
        for key, val in [param.split() for param in parameter_settings]:
            self.parameters[key] = val
        
        self.runtime = -1.0
        self.timed_out = False
        self.mem_out = False
        self.return_code = -1
    
    @property
    def clean_run(self):
        return self.return_code == 0


class ResultSet(object):
    """
      Class to represent a collection of Result objects and filter them accordingly.
    """
    
    def __init__(self):
        self.results = {}
        
    def add_result(self, id, result):
        self.results[id] = result
    
    def filter(self, func):
        toReturn = ResultSet()
        
        newResults = filter(func, self.results.values())
        for result in newResults:
            toReturn.add_result(result.id, result)
        
        return toReturn
    
    def filter_parameter(self, param, setting):
        return self.filter(lambda result: result.parameters[param] == setting)
    
    def filter_argument(self, arg, setting):
        return self.filter(lambda result: result.single_args[arg] == setting)
    
    @property
    def size(self):
        return len(self.results)
    
    def __getitem__(self, index):
        return self.results[index]
    
    def get_ids(self):
        return self.results.keys()
