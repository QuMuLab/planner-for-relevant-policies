#! /usr/bin/env python
"""
A module that prepares experiments for preprocessing planning problems

When the resultfetcher is run the following directory structure is created:

SCRIPTS_DIR
    - preprocessed-tasks
        - TRANSLATOR_REV-PREPROCESSOR_REV
            - DOMAIN
                - PROBLEM
                    - output
"""
import os
import sys
import subprocess
import logging

import experiments
import downward_suites
import downward_configs

# e.g. issue69.py -> issue69-checkouts
SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '../'))
CHECKOUTS_DIRNAME = os.path.basename(sys.argv[0])[:-3] + '-checkouts'
CHECKOUTS_DIR = os.path.join(SCRIPTS_DIR, CHECKOUTS_DIRNAME)

DOWNWARD_DIR = os.path.join(SCRIPTS_DIR, '../downward')

PREPROCESSED_TASKS_DIR = os.path.join(SCRIPTS_DIR, 'preprocessed-tasks')

# The standard URLs
TRANSLATE_URL = 'svn+ssh://downward/trunk/downward/translate'
PREPROCESS_URL = 'svn+ssh://downward/trunk/downward/preprocess'
SEARCH_URL = 'svn+ssh://downward/trunk/downward/search'

            
            
class Checkout(object):
    def __init__(self, repo_url, rev, local_dir, name):
        self.repo = repo_url
        self.rev = str(rev)
        self.name = name
        
        if os.path.isabs(local_dir):
            self.dir = local_dir
        else:
            self.dir = os.path.join(CHECKOUTS_DIR, local_dir)
        
    def checkout(self):
        # We don't need to check out the working copy
        if not self.rev == 'WORK':
            # If there's already a checkout, don't checkout again
            working_path = self.dir
            if not os.path.exists(working_path):
                cmd = 'svn co %s@%s %s' % (self.repo, self.rev, working_path)
                print cmd
                ret = subprocess.call(cmd.split())
            assert os.path.exists(working_path), \
                    'Could not checkout to "%s"' % working_path
            
        # Needs compiling?
        executable = self.get_executable()
        if not executable or not os.path.exists(executable):
            os.chdir(self.dir)
            subprocess.call(['make'])
            os.chdir('../')
        #_svn_checkout(self.repo, self.rev, self.dir)
        
        
class TranslatorCheckout(Checkout):
    def __init__(self, repo_url=TRANSLATE_URL, rev='HEAD'):
        name = 'translate-' + str(rev)
        if rev == 'WORK':
            local_dir = os.path.join(DOWNWARD_DIR, 'translate')
        else:
            local_dir = name
            
        Checkout.__init__(self, repo_url, rev, local_dir, name)
        
    def get_executable(self):
        """ Returns the path to the python module or a binary """
        return os.path.join(self.dir, 'translate.py')
        
        
class PreprocessorCheckout(Checkout):
    def __init__(self, repo_url=PREPROCESS_URL, rev='HEAD'):
        name = 'preprocess-' + str(rev)
        if rev == 'WORK':
            local_dir = os.path.join(DOWNWARD_DIR, 'preprocess')
        else:
            local_dir = name
            
        Checkout.__init__(self, repo_url, rev, local_dir, name)
        
    def get_executable(self):
        """ Returns the path to the python module or a binary """
        return os.path.join(self.dir, 'preprocess')
        

class PlannerCheckout(Checkout):
    def __init__(self, repo_url=SEARCH_URL, rev='HEAD'):
        name = 'search-' + str(rev)
        if rev == 'WORK':
            local_dir = os.path.join(DOWNWARD_DIR, 'search')
        else:
            local_dir = name
            
        Checkout.__init__(self, repo_url, rev, local_dir, name)
        
    def get_executable(self):
        """ Returns the path to the python module or a binary """
        names = ['downward', 'release-search', 'search']
        for name in names:
            planner = os.path.join(self.dir, name)
            if os.path.exists(planner):
                return planner
        return None
        
        
def get_same_rev_combo(rev='HEAD'):
    """
    Helper function that returns checkouts of the same revision for all
    subsystems
    """
    translator = TranslatorCheckout(rev=rev)
    preprocessor = PreprocessorCheckout(rev=rev)
    planner = PlannerCheckout(rev=rev)
    return (translator, preprocessor, planner)
             
        

def _make_checkouts(combinations):
    cwd = os.getcwd()
    if not os.path.exists(CHECKOUTS_DIR):
        os.mkdir(CHECKOUTS_DIR)
    os.chdir(CHECKOUTS_DIR)
    
    for translator_co, preprocessor_co, planner_co in combinations:
        
        translator_co.checkout()
        preprocessor_co.checkout()
        planner_co.checkout()
                
    os.chdir(cwd)
    


def build_preprocess_exp(combinations):
    parser = experiments.ExpArgParser()
    
    parser.add_argument('-s', '--suite', default=[], nargs='+', 
                        required=True, help=downward_suites.HELP)
    
    exp = experiments.build_experiment(parser)
    
    # Set defaults for faster preprocessing
    #exp.suite = ['ALL']
    exp.runs_per_task = 10
    logging.info('GkiGrid experiments: runs per task set to %s' % exp.runs_per_task)
    import multiprocessing
    exp.processes = multiprocessing.cpu_count()
    logging.info('Local experiments: processes set to %s' % exp.processes)
    
    #_make_checkouts(combinations)
    #TODO: Use all combinations
    translator_co, preprocessor_co = combinations[0]
            
    problems = downward_suites.build_suite(exp.suite)
    
    translator = translator_co.get_executable()
    assert os.path.exists(translator), translator
    
    preprocessor = preprocessor_co.get_executable()
    assert os.path.exists(preprocessor)
    preprocessor_name = "PREPROCESSOR_%s" % preprocessor_co.rev
    exp.add_resource(preprocessor_name, preprocessor, preprocessor_co.name)
     
    for problem in problems:
        run = exp.add_run()
        run.require_resource(preprocessor_name)
        
        domain_file = problem.domain_file()
        problem_file = problem.problem_file()
        run.add_resource("DOMAIN", domain_file, "domain.pddl")
        run.add_resource("PROBLEM", problem_file, "problem.pddl")
        
        translator = os.path.abspath(translator)
        translate_cmd = '%s %s %s' % (translator, domain_file, 
                                        problem_file)
        
        preprocess_cmd = '$%s < %s' % (preprocessor_name, 'output.sas')
        
        run.set_command('%s; %s' % (translate_cmd, preprocess_cmd))
        
        run.declare_optional_output("*.groups")
        run.declare_optional_output("output.sas")
        run.declare_optional_output("output")
        
        ext_config = '-'.join([translator_co.rev, preprocessor_co.rev])
        
        run.set_property('translator', translator_co.rev)
        run.set_property('preprocessor', preprocessor_co.rev)
        
        run.set_property('config', ext_config)
        run.set_property('domain', problem.domain)
        run.set_property('problem', problem.problem)
        run.set_property('id', [ext_config, problem.domain, 
                                problem.problem])
            
    exp.build()
    

if __name__ == '__main__':
    # If the module is invoked as a script, preprocess the files with the 
    # translator and preprocessor of the working copy
    combinations = [
        (TranslatorCheckout(rev='WORK'), PreprocessorCheckout(rev='WORK')),
                   ]
               
    build_preprocess_exp(combinations)
