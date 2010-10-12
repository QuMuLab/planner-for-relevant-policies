#! /usr/bin/env python
"""
A module that has methods for checking out different revisions of the three
components of fast-downward (translate, preprocess, search) and performing
experiments with them.
"""
import os
import sys
import subprocess

import experiments
import downward_suites
import downward_configs

# e.g. issue69.py -> issue69-checkouts
SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '../'))
CHECKOUTS_DIRNAME = os.path.basename(sys.argv[0])[:-3] + '-checkouts'
CHECKOUTS_DIR = os.path.join(SCRIPTS_DIR, CHECKOUTS_DIRNAME)

DOWNWARD_DIR = os.path.join(SCRIPTS_DIR, '../downward')

# The standard URLs
TRANSLATE_URL = 'svn+ssh://downward/trunk/downward/translate'
PREPROCESS_URL = 'svn+ssh://downward/trunk/downward/preprocess'
SEARCH_URL = 'svn+ssh://downward/trunk/downward/search'

         

def _svn_checkout(repo_path, revision, working_path):
    if not os.path.exists(working_path):
        cmd = 'svn co %s@%s %s' % (repo_path, revision, working_path)
        print cmd
        ret = subprocess.call(cmd.split())
    assert os.path.exists(working_path), \
            'Could not checkout to "%s"' % working_path
            
            
            
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
        if not self.rev == 'WORK':
            _svn_checkout(self.repo, self.rev, self.dir)
        
        
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
        
        # Needs compiling
        preprocessor = os.path.join(preprocessor_co.dir, 'preprocess')
        if  not os.path.exists(preprocessor):
            os.chdir(preprocessor_co.dir)
            subprocess.call(['make'])
            os.chdir('../')
        
        planner_co.checkout()
        
        # Needs compiling
        planner = planner_co.get_executable()
        if planner is None:
            os.chdir(planner_co.dir)
            subprocess.call(['make'])
            os.chdir('../')
                
    os.chdir(cwd)
    


def build_comparison_exp(combinations):    
    exp = experiments.build_experiment(parser=downward_configs.get_dw_parser())
    
    _make_checkouts(combinations)
            
    problems = downward_suites.build_suite(exp.suite)
    
    for translator_co, preprocessor_co, planner_co in combinations:
        
        translator = translator_co.get_executable()
        assert os.path.exists(translator), translator
        
        preprocessor = preprocessor_co.get_executable()
        assert os.path.exists(preprocessor)
        preprocessor_name = "PREPROCESSOR_%s" % preprocessor_co.rev
        exp.add_resource(preprocessor_name, preprocessor, preprocessor_co.name)
        
        planner = planner_co.get_executable()
        assert os.path.exists(planner)
        planner_name = "PLANNER_%s" % planner_co.rev
        exp.add_resource(planner_name, planner, planner_co.name)
        
        new_syntax = planner_co.rev in ['HEAD', 'WORK'] or \
                        int(planner_co.rev) >= 4425
                        
        if new_syntax:
            # configs is a list of (nickname,config) pairs
            configs = downward_configs.get_configs(exp.configs)
        else:
            # Use the old config names
            # We use the config names also as nicknames
            configs = zip(exp.configs, exp.configs)
         
        for config_name, config in configs:
            for problem in problems:
                run = exp.add_run()
                run.require_resource(preprocessor_name)
                run.require_resource(planner_name)
                
                domain_file = problem.domain_file()
                problem_file = problem.problem_file()
                run.add_resource("DOMAIN", domain_file, "domain.pddl")
                run.add_resource("PROBLEM", problem_file, "problem.pddl")
                
                translator = os.path.abspath(translator)
                translate_cmd = '%s %s %s' % (translator, domain_file, 
                                                problem_file)
                
                preprocess_cmd = '$%s < %s' % (preprocessor_name, 'output.sas')
                
                run.set_preprocess('%s; %s' % (translate_cmd, preprocess_cmd))
                
                run.set_command("$%s %s < output" % (planner_name, config))
                
                run.declare_optional_output("*.groups")
                run.declare_optional_output("output")
                run.declare_optional_output("output.sas")
                run.declare_optional_output("sas_plan")
                
                ext_config = '-'.join([translator_co.rev, preprocessor_co.rev, 
                                        planner_co.rev, config_name])
                
                run.set_property('translator', translator_co.rev)
                run.set_property('preprocessor', preprocessor_co.rev)
                run.set_property('planner', planner_co.rev)
                
                run.set_property('commandline_config', config)
                
                run.set_property('config', ext_config)
                run.set_property('domain', problem.domain)
                run.set_property('problem', problem.problem)
                run.set_property('id', [ext_config, problem.domain, 
                                        problem.problem])
            
    exp.build()
    

if __name__ == '__main__':
    # If the module is invoked as a script, compare the working copy with
    # the last checked-in version
    combinations = [
        get_same_rev_combo('HEAD'),
        get_same_rev_combo('WORK'),
                   ]
               
    build_comparison_exp(combinations)
