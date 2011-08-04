#! /usr/bin/env python
"""
Regular expressions and functions for parsing planning experiments
"""

from __future__ import with_statement, division

import logging
import re
import math
from collections import defaultdict

from resultfetcher import Fetcher, FetchOptionParser


def check(props):
    if props.get('translate_error') == 1:
        msg = 'Translator error without preprocessor error'
        assert props.get('preprocess_error') == 1, msg

    if props.get('cost') is not None:
        assert props.get('search_time') is not None


# Preprocessing functions -----------------------------------------------------


def parse_translator_timestamps(content, old_props):
    """Parse all translator output of the following forms:

        Computing fact groups: [0.000s CPU, 0.004s wall-clock]
        Writing output... [0.000s CPU, 0.001s wall-clock]
    """
    pattern = re.compile(r'^(.+)(\.\.\.|:) \[(.+)s CPU, .+s wall-clock\]$')
    new_props = {}
    for line in content.splitlines():
        if line.startswith('Done!'):
            break
        match = pattern.match(line)
        if match:
            section = match.group(1).lower().replace(' ', '_')
            new_props['translator_time_' + section] = float(match.group(3))
    return new_props


def get_derived_vars(content):
    """Count those variables that have an axiom_layer >= 0."""
    regex = re.compile(r'begin_variables\n\d+\n(.+)end_variables', re.M | re.S)
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


def get_facts(content):
    pattern = r'begin_variables\n\d+\n(.+)end_variables'
    vars_regex = re.compile(pattern, re.M | re.S)
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


def get_axioms(content):
    """
    If |axioms| > 0:  ...end_operator\nAXIOMS\nbegin_rule...
    If |axioms| == 0: ...end_operator\n0
    """
    regex = re.compile(r'end_operator\n(\d+)\nbegin_rule', re.M | re.S)
    match = regex.search(content)
    if not match:
        # make sure we have a valid file here
        regex = re.compile(r'end_operator\n(\d+)', re.M | re.S)
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
    regex = re.compile(r'begin_CG\n(.+)end_CG', re.M | re.S)
    match = regex.search(content)
    if not match:
        logging.error('Number of arcs could not be determined')
        return {}
    # cg looks like ['6', '1 16', '2 16', '3 8', '4 8', '5 8', '6 8', '4', ...]
    cg = match.group(1).splitlines()
    arcs = 0
    for line in cg:
        parts = line.split()
        parts = map(str.strip, parts)
        parts = filter(bool, parts)
        if len(parts) == 1:
            # We have a line containing the number of arcs for one node
            arcs += int(parts[0])
    return {'preprocessor_cg_arcs': arcs}


def get_problem_size(content):
    """
    Total problem size can be measured as the total number of tokens in the
    output.sas/output file.
    """
    return sum([len(line.split()) for line in content.splitlines()])


def translator_problem_size(content, old_props):
    return {'translator_problem_size': get_problem_size(content)}


def preprocessor_problem_size(content, old_props):
    return {'preprocessor_problem_size': get_problem_size(content)}


def translator_invariant_groups_total_size(content, old_props):
    """
    Total invariant group sizes after translating
    (sum over all numbers that follow a "group" line in the "all.groups" file)
    """
    groups = re.findall(r'group\n(\d+)', content, re.M | re.S)
    total = sum(map(int, groups))
    return {'translator_invariant_groups_total_size': total}


# Search functions ------------------------------------------------------------

def _get_states_pattern(attribute, name):
    return (attribute, re.compile(r'%s (\d+) state\(s\)\.' % name), int)


# TODO: What about lines like "Initial state h value: 1147184/1703241."?
def get_iterative_results(content, old_props):
    """
    In iterative search some attributes like plan cost can have multiple
    values, i.e. one value for each iterative search. We save those values in
    lists.
    """
    values = defaultdict(list)
    patterns = [('cost', re.compile(r'Plan cost: (.+)'), int),
                _get_states_pattern('dead_ends', 'Dead ends:'),
                _get_states_pattern('evaluations', 'Evaluated'),
                _get_states_pattern('expansions', 'Expanded'),
                _get_states_pattern('generated', 'Generated'),
                ('initial_h_value',
                    re.compile(r'Initial state h value: (\d+)'), int),
                ('plan_length', re.compile(r'Plan length: (\d+)'), int),
                ('search_time',
                    re.compile(r'Actual search time: (.+)s \[t=.+s\]'), float)
               ]
    for line in content.splitlines():
        # At the end of iterative search some statistics are printed and we do
        # not want to parse those here.
        if line.startswith('Cumulative statistics'):
            break
        for name, pattern, cast in patterns:
            match = pattern.search(line)
            if not match:
                continue
            values[name].append(cast(match.group(1)))
            # We can break here, because each line contains only one value
            break

    # After iterative search completes there is another line starting with
    # "Actual search time" that just states the cumulative search time.
    # In order to let all lists have the same length, we omit that value here.
    if len(values['search_time']) > len(values['expansions']):
        values['search_time'].pop()

    # Check that some lists have the same length
    def same_length(group):
        return len(set(len(x) for x in group)) == 1

    group1 = ('cost', 'plan_length')
    group2 = ('dead_ends', 'expansions', 'evaluations', 'generated',
              'initial_h_value', 'search_time')
    assert same_length(values[x] for x in group1), values
    assert same_length(values[x] for x in group2), values

    new_props = {}
    for name, items in values.items():
        new_props[name + '_all'] = items

    if values['cost']:
        new_props['cost'] = values['cost'][-1]
    if values['plan_length']:
        new_props['plan_length'] = values['plan_length'][-1]
    return new_props


def get_cumulative_results(content, old_props):
    """
    Some cumulative results are printed at the end of the logfile. We revert
    the content to make a search for those values much faster. We would have to
    convert the content anyways, because there's no real telling if those
    values talk about a single or a cumulative result. If we start parsing at
    the bottom of the file we know that the values are the cumulative ones.
    """
    new_props = {}
    patterns = [_get_states_pattern('dead_ends', 'Dead ends:'),
                _get_states_pattern('evaluations', 'Evaluated'),
                _get_states_pattern('expansions', 'Expanded'),
                _get_states_pattern('generated', 'Generated'),
                ('search_time', re.compile(r'^Search time: (.+)s$'), float),
                ('total_time', re.compile(r'^Total time: (.+)s$'), float),
                ('memory', re.compile(r'Peak memory: (.+) KB'), int)
               ]
    reverse_content = list(reversed(content.splitlines()))
    for name, pattern, cast in patterns:
        for line in reverse_content:
            # There will be no cumulative values above this line
            if line == 'Cumulative statistics:':
                break
            match = pattern.search(line)
            if not match:
                continue
            new_props[name] = cast(match.group(1))
    return new_props


def set_search_time(content, old_props):
    """
    If iterative search has accumulated single search times, but the total
    search time was not written (due to a possible timeout for example), we
    set search_time to be the sum of the single search times.
    """
    new_props = {}
    if 'search_time' not in old_props:
        if 'search_time_all' in old_props:
            new_props['search_time'] = math.fsum(old_props['search_time_all'])
    return new_props


def completely_explored(content, old_props):
    return {'completely_explored':
            'Completely explored state space -- no solution!' in content}


def get_status(content, old_props):
    new_props = {}
    if 'plan_length' in old_props or 'cost' in old_props:
        new_props['status'] = 'ok'
    elif old_props.get('completely_explored', False):
        new_props['status'] = 'failure'
    elif 'does not support' in content:
        new_props['status'] = 'unsupported'
    else:
        new_props['status'] = 'unsolved'
    return new_props


def coverage(content, old_props):
    return {'coverage': int('plan_length' in old_props or 'cost' in old_props)}


def check_memory(content, old_props):
    """
    Set "memory" to the max value if it was exceeded and "-1 KB" was reported
    """
    new_props = {}
    memory = old_props.get('memory')
    memory_limit = old_props.get('memory_limit')
    if memory == -1 and memory_limit:
        new_props['memory'] = memory_limit
    return new_props


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

    return {'score_expansions': log_score(old_props.get('expansions'),
                    min_bound=100, max_bound=1000000, min_score=0.0),
            'score_evaluations': log_score(old_props.get('evaluations'),
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


def validate(content, old_props):
    """
    Check the returncode of the validate command
    """
    assert 'coverage' in old_props
    return {"plan_invalid": int(old_props.get('coverage') == 1 and
                                old_props.get('validate_returncode') == '1')}

# -----------------------------------------------------------------------------


def add_preprocess_parsing(eval):
    """Add some preprocess specific parsing"""

    # TODO: Set required to True
    #eval.add_pattern('translate_error', r'translate_error = (\d)',
    #                 file='preprocess-properties', type=int, required=False)
    #eval.add_pattern('preprocess_error', r'preprocess_error = (\d)',
    #                 file='preprocess-properties', type=int, required=False)

    # Number of invariant groups (second line in the "all.groups" file)
    # The file starts with "begin_groups\n7\ngroup"
    #eval.add_pattern('translator_invariant_groups', r'begin_groups\n(\d+)\n',
    #                    file='all.groups', type=int, flags='MS')
    eval.add_pattern('translator_invariant_groups',
                     r'begin_groups\n(\d+)\ngroup', file='all.groups',
                     type=int, flags='MS')

    # Preprocessor output:
    # 19 variables of 19 necessary
    # 2384 of 2384 operators necessary.
    # 0 of 0 axiom rules necessary
    eval.add_multipattern([(1, 'preprocessor_vars', int),
                          (2, 'translator_vars', int)],
                          r'(\d+) variables of (\d+) necessary')
    eval.add_multipattern([(1, 'preprocessor_ops', int),
                           (2, 'translator_ops', int)],
                           r'(\d+) of (\d+) operators necessary')
    eval.add_multipattern([(1, 'preprocessor_axioms', int),
                           (2, 'translator_axioms', int)],
                           r'(\d+) of (\d+) axiom rules necessary')

    """
    the numbers from the following lines of translator output:
        170 relevant atoms
        141 auxiliary atoms
        311 final queue length
        364 total queue pushes
        13 uncovered facts
        0 implied effects removed
        0 effect conditions simplified
        0 implied preconditions added
        0 operators removed
        38 propositions removed
    """
    translator_values = [
        'relevant atoms', 'auxiliary atoms', 'final queue length',
        'total queue pushes', 'uncovered facts', 'implied effects removed',
        'effect conditions simplified', 'implied preconditions added',
        'operators removed', 'propositions removed']
    for value_name in translator_values:
        attribute = 'translator_' + value_name.lower().replace(' ', '_')
        eval.add_pattern(attribute, r'(.+) %s' % value_name, type=int)


def add_preprocess_functions(eval):
    eval.add_function(parse_translator_timestamps)
    return

    eval.add_function(translator_facts, file='output.sas')
    eval.add_function(preprocessor_facts, file='output')

    eval.add_function(translator_derived_vars, file='output.sas')
    eval.add_function(preprocessor_derived_vars, file='output')

    #eval.add_function(cg_arcs, file='output')

    #eval.add_function(translator_problem_size, file='output.sas')
    #eval.add_function(preprocessor_problem_size, file='output')

    # Total invariant group sizes after translating
    # (sum over all numbers following a "group" line in the "all.groups" file)
    eval.add_function(translator_invariant_groups_total_size,
                      file='all.groups')


def add_search_functions(eval):
    #eval.add_function(completely_explored)
    eval.add_function(get_iterative_results)
    eval.add_function(get_cumulative_results)
    eval.add_function(set_search_time)
    eval.add_function(coverage)
    eval.add_function(get_status)
    eval.add_function(scores)
    eval.add_function(check_memory)
    eval.add_function(validate)


def build_fetcher(parser=FetchOptionParser()):
    parser.add_argument('--no-preprocess', action='store_true',
        help='Do not parse preprocessing results')
    parser.add_argument('--no-search', action='store_true',
        help='Do not parse search results')

    eval = Fetcher(parser)

    # Do not parse preprocess files if it has been disabled on the commandline
    if not eval.no_preprocess:
        if eval.exp_props.get('compact', False):
            # For compact experiments the preprocess files do not reside in the
            # run's directory so we can't parse them
            logging.info('You are parsing a compact experiment, so preprocess '
                         'files will not be parsed')
        else:
            add_preprocess_parsing(eval)
            add_preprocess_functions(eval)
    if not eval.no_search:
        add_search_functions(eval)

    eval.add_function(check_min_values)
    eval.set_check(check)

    return eval


if __name__ == '__main__':
    fetcher = build_fetcher()
    fetcher.fetch()
