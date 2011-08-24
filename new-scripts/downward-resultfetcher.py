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
import tools


def check(props):
    if props.get('translate_error') == 1:
        msg = 'Translator error without preprocessor error'
        assert props.get('preprocess_error') == 1, msg

    if props.get('cost') is not None:
        assert props.get('search_time') is not None


# Preprocessing functions -----------------------------------------------------


def parse_translator_timestamps(content, props):
    """Parse all translator output of the following forms:

        Computing fact groups: [0.000s CPU, 0.004s wall-clock]
        Writing output... [0.000s CPU, 0.001s wall-clock]
    """
    pattern = re.compile(r'^(.+)(\.\.\.|:) \[(.+)s CPU, .+s wall-clock\]$')
    for line in content.splitlines():
        if line.startswith('Done!'):
            break
        match = pattern.match(line)
        if match:
            section = match.group(1).lower().replace(' ', '_')
            props['translator_time_' + section] = float(match.group(3))


def _get_var_descriptions(content):
    """Returns a list of (var_name, domain_size, axiom_layer) tuples."""
    regex = re.compile(r'begin_variables\n\d+\n(.+)end_variables', re.M | re.S)
    match = regex.search(content)
    if not match:
        return []
    # var_descriptions looks like ['var0 7 -1', 'var1 4 -1', 'var2 4 -1']
    var_descriptions = [var.split() for var in match.group(1).splitlines()]
    return [(name, int(size), int(layer))
            for name, size, layer in var_descriptions]


def _get_derived_vars(content):
    """Count those variables that have an axiom_layer >= 0."""
    var_descriptions = _get_var_descriptions(content)
    if not var_descriptions:
        logging.error('Number of derived vars could not be found')
        return None
    return len([name for name, size, layer in var_descriptions if layer >= 0])


def translator_derived_vars(content, props):
    props.setdefault('translator_derived_vars', _get_derived_vars(content))


def preprocessor_derived_vars(content, props):
    props.setdefault('preprocessor_derived_vars', _get_derived_vars(content))


def _get_facts(content):
    var_descriptions = _get_var_descriptions(content)
    if not var_descriptions:
        logging.error('Number of facts could not be found')
        return None
    return sum(size for name, size, layer in var_descriptions)


def translator_facts(content, props):
    props.setdefault('translator_facts', _get_facts(content))


def preprocessor_facts(content, props):
    props.setdefault('preprocessor_facts', _get_facts(content))


def get_problem_size(content):
    """
    Total problem size can be measured as the total number of tokens in the
    output.sas/output file.
    """
    return len(content.split())


def translator_problem_size(content, props):
    props['translator_problem_size'] = get_problem_size(content)


def preprocessor_problem_size(content, props):
    props['preprocessor_problem_size'] = get_problem_size(content)


def translator_mutex_groups_total_size(content, props):
    """
    Total mutex group sizes after translating
    (sum over all numbers that follow a "group" line in the "all.groups" file)
    """
    groups = re.findall(r'group\n(\d+)', content, re.M | re.S)
    props['translator_mutex_groups_total_size'] = sum(map(int, groups))


# Search functions ------------------------------------------------------------

def _get_states_pattern(attribute, name):
    return (attribute, re.compile(r'%s (\d+) state\(s\)\.' % name), int)


ITERATIVE_PATTERNS = [
    ('cost', re.compile(r'Plan cost: (.+)'), int),
    _get_states_pattern('dead_ends', 'Dead ends:'),
    _get_states_pattern('evaluations', 'Evaluated'),
    _get_states_pattern('expansions', 'Expanded'),
    _get_states_pattern('generated', 'Generated'),
    # We exclude lines like "Initial state h value: 1147184/1703241." that stem
    # from multi-heuristic search.
    ('initial_h_value', re.compile(r'Initial state h value: (\d+)\.'), int),
    ('plan_length', re.compile(r'Plan length: (\d+)'), int),
    # We cannot include " \[t=.+s\]" in the regex, because older versions don't
    # have this information in the log.
    ('search_time', re.compile(r'Actual search time: (.+?)s'), float)
    ]

CUMULATIVE_PATTERNS = [
    # This time we parse the cumulative values
    _get_states_pattern('dead_ends', 'Dead ends:'),
    _get_states_pattern('evaluations', 'Evaluated'),
    _get_states_pattern('expansions', 'Expanded'),
    _get_states_pattern('generated', 'Generated'),
    ('search_time', re.compile(r'^Search time: (.+)s$'), float),
    ('total_time', re.compile(r'^Total time: (.+)s$'), float),
    ('memory', re.compile(r'Peak memory: (.+) KB'), int),
    # For iterated searches we discard any h values. Here we will not find
    # anything before the "cumulative" line and stop the search. For single
    # searches we will find the h value if it isn't a multi-heuristic search.
    ('initial_h_value', re.compile(r'Initial state h value: (\d+)\.'), int),
    ]


def get_iterative_results(content, props):
    """
    In iterative search some attributes like plan cost can have multiple
    values, i.e. one value for each iterative search. We save those values in
    lists.
    """
    values = defaultdict(list)

    for line in content.splitlines():
        # At the end of iterative search some statistics are printed and we do
        # not want to parse those here.
        if line == 'Cumulative statistics:':
            break
        for name, pattern, cast in ITERATIVE_PATTERNS:
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
    group2 = ('expansions', 'evaluations', 'generated', 'search_time')
    assert same_length(values[x] for x in group1), values
    assert same_length(values[x] for x in group2), values

    for name, items in values.items():
        props[name + '_all'] = items

    for attr in ['cost', 'plan_length']:
        if values[attr]:
            props[attr] = min(values[attr])


def get_cumulative_results(content, props):
    """
    Some cumulative results are printed at the end of the logfile. We revert
    the content to make a search for those values much faster. We would have to
    convert the content anyways, because there's no real telling if those
    values talk about a single or a cumulative result. If we start parsing at
    the bottom of the file we know that the values are the cumulative ones.
    """
    reverse_content = list(reversed(content.splitlines()))
    for name, pattern, cast in CUMULATIVE_PATTERNS:
        for line in reverse_content:
            # There will be no cumulative values above this line
            if line == 'Cumulative statistics:':
                break
            match = pattern.search(line)
            if not match:
                continue
            props[name] = cast(match.group(1))


def set_search_time(content, props):
    """
    If iterative search has accumulated single search times, but the total
    search time was not written (due to a possible timeout for example), we
    set search_time to be the sum of the single search times.
    """
    if 'search_time' not in props:
        if 'search_time_all' in props:
            props['search_time'] = math.fsum(props['search_time_all'])


def completely_explored(content, props):
    props['completely_explored'] = ('Completely explored state space -- '
                                    'no solution!' in content)


def get_status(content, props):
    if 'plan_length' in props or 'cost' in props:
        props['status'] = 'ok'
    elif props.get('completely_explored', False):
        props['status'] = 'failure'
    elif 'does not support' in content:
        props['status'] = 'unsupported'
    else:
        props['status'] = 'unsolved'


def coverage(content, props):
    props['coverage'] = int('plan_length' in props or 'cost' in props)


def check_memory(content, props):
    """
    Set "memory" to the max value if it was exceeded and "-1 KB" was reported
    """
    memory = props.get('memory')
    memory_limit = props.get('memory_limit')
    if memory == -1 and memory_limit:
        props['memory'] = memory_limit


def scores(content, props):
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

    props.update({'score_expansions': log_score(props.get('expansions'),
                    min_bound=100, max_bound=1000000, min_score=0.0),
            'score_evaluations': log_score(props.get('evaluations'),
                    min_bound=100, max_bound=1000000, min_score=0.0),
            'score_total_time': log_score(props.get('total_time'),
                    min_bound=1.0, max_bound=1800.0, min_score=0.0),
            'score_search_time': log_score(props.get('search_time'),
                    min_bound=1.0, max_bound=1800.0, min_score=0.0),
           })


def check_min_values(content, props):
    """
    Ensure that times are at least 0.1s if they are present in log
    """
    for time in ['search_time', 'total_time']:
        sec = props.get(time, None)
        if sec is not None:
            sec = max(sec, 0.1)
            props[time] = sec

# -----------------------------------------------------------------------------


def add_preprocess_parsing(eval):
    """Add some preprocess specific parsing"""

    # TODO: Set required to True
    #eval.add_pattern('translate_error', r'translate_error = (\d)',
    #                 file='preprocess-properties', type=int, required=False)
    #eval.add_pattern('preprocess_error', r'preprocess_error = (\d)',
    #                 file='preprocess-properties', type=int, required=False)

    # Number of mutex groups (second line in the "all.groups" file)
    # The file starts with "begin_groups\n7\ngroup"
    eval.add_pattern('translator_mutex_groups',
                     r'begin_groups\n(\d+)\ngroup', file='all.groups',
                     type=int, flags='MS')

    # Parse the preprocessor output. We keep this code for older revisions:
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

    # Parse the numbers from the following lines of translator output:
    #    170 relevant atoms
    #    141 auxiliary atoms
    #    311 final queue length
    #    364 total queue pushes
    #    13 uncovered facts
    #    0 implied effects removed
    #    0 effect conditions simplified
    #    0 implied preconditions added
    #    0 operators removed
    #    38 propositions removed
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

    eval.add_function(translator_facts, file='output.sas')
    eval.add_function(preprocessor_facts, file='output')

    eval.add_function(translator_derived_vars, file='output.sas')
    eval.add_function(preprocessor_derived_vars, file='output')

    eval.add_function(translator_problem_size, file='output.sas')
    eval.add_function(preprocessor_problem_size, file='output')

    # Total mutex group sizes after translating
    # (sum over all numbers following a "group" line in the "all.groups" file)
    eval.add_function(translator_mutex_groups_total_size, file='all.groups')


def add_search_parsing(eval):
    eval.add_pattern('landmarks', r'Discovered (\d+?) landmarks', type=int,
                     required=False)
    eval.add_pattern('landmarks_generation_time',
                     r'Landmarks generation time: (.+)s', type=float,
                     required=False)


def add_search_functions(eval):
    #eval.add_function(completely_explored)
    eval.add_function(get_iterative_results)
    eval.add_function(get_cumulative_results)
    eval.add_function(set_search_time)
    eval.add_function(coverage)
    eval.add_function(get_status)
    eval.add_function(scores)
    eval.add_function(check_memory)


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
        add_search_parsing(eval)
        add_search_functions(eval)

    eval.add_function(check_min_values)
    eval.set_check(check)

    return eval


if __name__ == '__main__':
    fetcher = build_fetcher()
    with tools.timing('Parse files'):
        fetcher.fetch()
