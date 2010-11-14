#! /usr/bin/env python
"""
Regular expressions and functions for parsing planning experiments
"""

from __future__ import with_statement, division

import sys
import os
import logging
import re
import math

from resultfetcher import Fetcher, FetchOptionParser

def check(props):
    if props.get('translator_error') == 1:
        assert props.get('preprocessor_error') == 1, \
                                'Translator error without preprocessor error'

def add_preprocess_parsing(eval):
    
    def translator_error(content, old_props):
        error = not 'Done! [' in content
        return {'translator_error': int(error)}
        
    def preprocessor_error(content, old_props):
        error = not 'Writing output...\ndone' in content
        return {'preprocessor_error': int(error)}
        
    eval.add_function(translator_error)
    eval.add_function(preprocessor_error)


def build_fetcher(parser=FetchOptionParser()):
    eval = Fetcher(parser)
    #eval.add_key_value_pattern('run_start_time')
    eval.add_pattern('initial_h_value', r'Initial state h value: (\d+)', type=int, required=False)
    eval.add_pattern('plan_length', r'Plan length: (\d+)', type=int, required=False)
    eval.add_pattern('expanded', r'Expanded (\d+)', type=int, required=False)
    eval.add_pattern('generated', r'Generated (\d+) state', type=int, required=False)
    eval.add_pattern('search_time', r'Search time: (.+)s', type=float, required=False, flags='I')
    eval.add_pattern('total_time', r'Total time: (.+)s', type=float, required=False)
    eval.add_pattern('memory', r'Peak memory: (.+) KB', type=int, required=False)
    eval.add_pattern('cost', r'Plan cost: (.+)', type=int, required=False)
    
    
    #eval.add_pattern('translator_vars', r'begin_variables\n(\d+)', file='output.sas', type=int, flags='M')
    #eval.add_pattern('translator_ops', r'end_goal\n(\d+)', file='output.sas', type=int, flags='M')
    
    #eval.add_pattern('preprocessor_vars', r'begin_variables\n(\d+)', file='output', type=int, flags='M')
    #eval.add_pattern('preprocessor_ops', r'end_goal\n(\d+)', file='output', type=int, flags='M')
    
    
    # Experimental
    # Preprocessor output:
    # 19 variables of 19 necessary
    # 2384 of 2384 operators necessary.
    # 0 of 0 axiom rules necessary
    
    #eval.add_pattern('rules_exp', r'Generated (\d+) rules', type=int)
    
    eval.add_multipattern([(1, 'preprocessor_vars', int), (2, 'translator_vars', int)], 
                            r'(\d+) variables of (\d+) necessary')
    eval.add_multipattern([(1, 'preprocessor_ops', int), (2, 'translator_ops', int)], 
                            r'(\d+) of (\d+) operators necessary')
    eval.add_multipattern([(1, 'preprocessor_axioms', int), (2, 'translator_axioms', int)],
                            r'(\d+) of (\d+) axiom rules necessary')
    
    
    def completely_explored(content, old_props):
        new_props = {}
        if 'Completely explored state space -- no solution!' in content:
            new_props['completely_explored'] = True
        return new_props
    
    def get_status(content, old_props):
        new_props = {}
        if 'does not support' in content:
            new_props['status'] = 'unsupported'
        elif 'plan_length' in old_props:
            new_props['status'] = 'ok'
        elif 'completely_explored' in old_props:
            new_props['status'] = 'failure'
        else:
            new_props['status'] = 'not_ok'
        return new_props
        
    def solved(content, old_props):
        new_props = {}
        if 'plan_length' in old_props:
            new_props['solved'] = 1
        else:
            new_props['solved'] = 0
        return new_props
        
        
    def get_facts(content):
        vars_regex = re.compile(r'begin_variables\n\d+\n(.+)end_variables', re.M|re.S)
        match = vars_regex.search(content)
        if not match:
            logging.error('Number of facts could not be found')
            return {}
        """
        var_descriptions looks like
        ['var0 7 -1', 'var1 4 -1', 'var2 4 -1', 'var3 3 -1']
        """
        var_descriptions = match.group(1).splitlines()
        total_domain_size = 0
        for var in var_descriptions:
            var_name, domain_size, axiom_layer = var.split()
            total_domain_size += int(domain_size)
        return total_domain_size
        
    def translator_facts(content, old_props):
        return {'translator_facts': get_facts(content)}
        
    def preprocessor_facts(content, old_props):
        return {'preprocessor_facts': get_facts(content)}
        
        
    def get_derived_vars(content):
        """
        Count those variables that have an axiom_layer >= 0
        """
        regex = re.compile(r'begin_variables\n\d+\n(.+)end_variables', re.M|re.S)
        match = regex.search(content)
        if not match:
            logging.error('Number of derived vars could not be found')
            return {}
        """
        var_descriptions looks like
        ['var0 7 -1', 'var1 4 -1', 'var2 4 -1', 'var3 3 -1']
        """
        var_descriptions = match.group(1).splitlines()
        derived_vars = 0
        for var in var_descriptions:
            var_name, domain_size, axiom_layer = var.split()
            if int(axiom_layer) >= 0:
                derived_vars += 1
        return derived_vars
        
    def translator_derived_vars(content, old_props):
        return {'translator_derived_vars': get_derived_vars(content)}
        
    def preprocessor_derived_vars(content, old_props):
        return {'preprocessor_derived_vars': get_derived_vars(content)}
        
        
    def get_axioms(content):
        """
        If |axioms| > 0:  ...end_operator\nAXIOMS\nbegin_rule...
        If |axioms| == 0: ...end_operator\n0
        """
        regex = re.compile(r'end_operator\n(\d+)\nbegin_rule', re.M|re.S)
        match = regex.search(content)
        if not match:
            # make sure we have a valid file here
            regex = re.compile(r'end_operator\n(\d+)', re.M|re.S)
            match = regex.search(content)
            
            if match is None:
                # Some mystery problems don't have any operators
                assert 'begin_rule' not in content, content
                return 0
            else:
                assert match.group(1) == '0'
        axioms = int(match.group(1))
        return axioms
        
    def translator_axioms(content, old_props):
        return {'translator_axioms': get_axioms(content)}
        
    def preprocessor_axioms(content, old_props):
        return {'preprocessor_axioms': get_axioms(content)}
        
        
    def cg_arcs(content, old_props):
        """
        Sums up the number of outgoing arcs for each vertex
        """
        regex = re.compile(r'begin_CG\n(.+)end_CG', re.M|re.S)
        match = regex.search(content)
        if not match:
            logging.error('Number of arcs could not be determined')
            return {}
        """
        cg looks like
        ['6', '1 16', '2 16', '3 8', '4 8', '5 8', '6 8', '4', ...]
        """
        cg = match.group(1).splitlines()
        arcs = 0
        for line in cg:
            parts = line.split()
            parts = map(lambda part: part.strip(), parts)
            parts = filter(lambda part: len(part) > 0, parts)
            if len(parts) == 1:
                # We have a line containing the number of arcs for one node
                arcs += int(parts[0])
        return {'cg_arcs': arcs}


    def scores(content, old_props):
        """
        Some reported results are measured via scores from the
        range 0-1, where best possible performance in a task is
        counted as 1, while failure to solve a task and worst 
        performance are counted as 0
        """
        def log_score(value, min_bound, max_bound, min_score):
            if value is None:
                return 0
            if value < min_bound:
                value = min_bound
            if value > max_bound:
                value = max_bound
            raw_score = math.log(value) - math.log(max_bound)
            best_raw_score = math.log(min_bound) - math.log(max_bound)
            score = min_score + (1 - min_score) * (raw_score / best_raw_score)
            return round(score, 4)
        
        return {'score_expansions': log_score(old_props.get('expanded'), 
                        min_bound=100, max_bound=1000000, min_score=0.0),
                'score_total_time': log_score(old_props.get('total_time'), 
                        min_bound=1.0, max_bound=1800.0, min_score=0.0),
                'score_search_time': log_score(old_props.get('search_time'), 
                        min_bound=1.0, max_bound=1800.0, min_score=0.0),
                }
                
    def check_min_values(content, old_props):
        """
        Ensure that times are at least 0.1s if they are present in log
        """
        new_props = {}
        for time in ['search_time', 'total_time']:
            sec = old_props.get(time, None)
            if sec is not None:
                sec = max(sec, 0.1)
                new_props[time] = sec
        return new_props
                    
        
    #eval.add_function(completely_explored)
    #eval.add_function(get_status)
    eval.add_function(solved)
    
#    eval.add_function(translator_facts, file='output.sas')
#    eval.add_function(preprocessor_facts, file='output')
    
    #eval.add_function(translator_axioms, file='output.sas')
    #eval.add_function(preprocessor_axioms, file='output')
    
#    eval.add_function(translator_derived_vars, file='output.sas')
#    eval.add_function(preprocessor_derived_vars, file='output')
    
#    eval.add_function(cg_arcs, file='output')
    
    eval.add_function(scores)
    
    eval.add_function(check_min_values)
    
    add_preprocess_parsing(eval)
    
    eval.set_check(check)
    
    return eval


if __name__ == '__main__':
    fetcher = build_fetcher()
    fetcher.fetch()
