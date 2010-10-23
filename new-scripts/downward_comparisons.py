#! /usr/bin/env python
"""
A module that has methods for checking out different revisions of the three
components of fast-downward (translate, preprocess, search) and performing
experiments with them.
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
CHECKOUTS_DIRNAME = os.path.basename(sys.argv[0])[:-3] + \
                                    '-checkouts'.replace('-experiments-', '')
CHECKOUTS_DIR = os.path.join(SCRIPTS_DIR, CHECKOUTS_DIRNAME)

DOWNWARD_DIR = os.path.join(SCRIPTS_DIR, '../downward')

            
            
class Checkout(object):    
    def __init__(self, part, repo, rev, checkout_dir, name):
        # Directory name of the planner part (translate, preprocess, search)
        self.part = part
        self.repo = repo
        self.rev = str(rev)
        self.name = name
        
        if not os.path.isabs(checkout_dir):
            checkout_dir = os.path.join(CHECKOUTS_DIR, checkout_dir)
        self.checkout_dir = checkout_dir
        
    def checkout(self):
        # We don't need to check out the working copy
        if not self.rev == 'WORK':
            # If there's already a checkout, don't checkout again
            path = self.checkout_dir
            if os.path.exists(path):
                logging.info('Checkout "%s" already exists' % path)
            else:
                cmd = self.get_checkout_cmd()
                print cmd
                ret = subprocess.call(cmd.split())
            assert os.path.exists(path), \
                    'Could not checkout to "%s"' % path
                    
    def get_checkout_cmd(self):
        raise Exception('Not implemented')
            
    def compile(self):
        """
        """
        # Needs compiling?
        executable = self.get_executable()
        if executable is None or not os.path.exists(executable):
            os.chdir(self.exe_dir)
            subprocess.call(['make'])
            os.chdir(SCRIPTS_DIR)
        
    def get_executable(self):
        """ Returns the path to the python module or a binary """
        names = ['translate.py', 'preprocess', 
                'downward', 'release-search', 'search']
        for name in names:
            planner = os.path.join(self.exe_dir, name)
            if os.path.exists(planner):
                return planner
        return None
        


# ---------- Mercurial ---------------------------------------------------------

class HgCheckout(Checkout):
    DEFAULT_URL = 'ssh://downward'
    DEFAULT_REV = 'tip'
    
    def __init__(self, part, repo, rev):
        #TODO: Find proper absolute revision
        #rev = revname
        revname = str(rev).upper()
        name = part + '-' + revname
        
        if revname == 'WORK':
            checkout_dir = os.path.join(SCRIPTS_DIR, '../')
        else:
            checkout_dir = rev
            
        Checkout.__init__(self, part, repo, rev, checkout_dir, name)
        
    def get_checkout_cmd(self):
        return 'hg clone -r %s %s %s' % (self.rev, self.repo, self.checkout_dir)
        
    @property
    def exe_dir(self):
        assert os.path.exists(self.checkout_dir)
        exe_dir = os.path.join(self.checkout_dir, 'downward', self.part)
        # "downward" dir has been renamed to "src"
        if not os.path.exists(exe_dir):
            self.exe_dir = os.path.join(self.checkout_dir, 'src', self.part)
        return exe_dir
            
            
class TranslatorHgCheckout(HgCheckout):
    def __init__(self, repo=HgCheckout.DEFAULT_URL, rev=HgCheckout.DEFAULT_REV):
        HgCheckout.__init__(self, 'translate', repo, rev)
            
class PreprocessorHgCheckout(HgCheckout):
    def __init__(self, repo=HgCheckout.DEFAULT_URL, rev=HgCheckout.DEFAULT_REV):
        HgCheckout.__init__(self, 'preprocess', repo, rev)
        
class PlannerHgCheckout(HgCheckout):
    def __init__(self, repo=HgCheckout.DEFAULT_URL, rev=HgCheckout.DEFAULT_REV):
        HgCheckout.__init__(self, 'search', repo, rev)
        
        
        
# ---------- Subversion --------------------------------------------------------
        
class SvnCheckout(Checkout):
    DEFAULT_URL = 'svn+ssh://downward-svn/trunk/downward'
    DEFAULT_REV = 'HEAD'
    
    def __init__(self, part, repo, rev=DEFAULT_REV):
        name = part + '-' + str(rev)
        if rev == 'WORK':
            checkout_dir = os.path.join(DOWNWARD_DIR, part)
        else:
            checkout_dir = name
            
        Checkout.__init__(self, part, repo, rev, checkout_dir, name)
        
    def get_checkout_cmd(self):
        return 'svn co %s@%s %s' % (self.repo, self.rev, self.checkout_dir)
        
    @property
    def exe_dir(self):
        # checkout_dir is exe_dir for SVN
        assert os.path.exists(self.checkout_dir)
        return self.checkout_dir
        
        
class TranslatorSvnCheckout(SvnCheckout):
    DEFAULT_URL = 'svn+ssh://downward-svn/trunk/downward/translate'
    
    def __init__(self, repo=DEFAULT_URL, rev=SvnCheckout.DEFAULT_REV):
        SvnCheckout.__init__(self, 'translate', repo, rev)
        
        
class PreprocessorSvnCheckout(SvnCheckout):
    DEFAULT_URL = 'svn+ssh://downward-svn/trunk/downward/preprocess'
    
    def __init__(self, repo=DEFAULT_URL, rev=SvnCheckout.DEFAULT_REV):
        SvnCheckout.__init__(self, 'preprocess', repo, rev)
        

class PlannerSvnCheckout(SvnCheckout):
    DEFAULT_URL = 'svn+ssh://downward-svn/trunk/downward/search'
    
    def __init__(self, repo=DEFAULT_URL, rev=SvnCheckout.DEFAULT_REV):
        SvnCheckout.__init__(self, 'search', repo, rev)
             
# ------------------------------------------------------------------------------



def make_checkouts(combinations):
    """
    Checks out and compiles the code
    """
    cwd = os.getcwd()
    if not os.path.exists(CHECKOUTS_DIR):
        os.mkdir(CHECKOUTS_DIR)
    os.chdir(CHECKOUTS_DIR)
    
    for combo in combinations:
        for part in combo:
            part.checkout()
            part.compile()
        
    os.chdir(cwd)
    


def build_comparison_exp(combinations):
    exp = experiments.build_experiment(parser=downward_configs.get_dw_parser())
    
    make_checkouts(combinations)
            
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
    

def test():
    combinations = [
        (TranslatorHgCheckout(), PreprocessorHgCheckout(rev='tip'), PlannerHgCheckout(rev='WORK')),
        (TranslatorSvnCheckout(), PreprocessorSvnCheckout(rev='HEAD'), PlannerSvnCheckout(rev='WORK')),
        (TranslatorSvnCheckout(4321), PreprocessorHgCheckout(rev='tip'), PlannerSvnCheckout(rev='HEAD')),
                   ]
    
    build_comparison_exp(combinations)

    

if __name__ == '__main__':
    test()
