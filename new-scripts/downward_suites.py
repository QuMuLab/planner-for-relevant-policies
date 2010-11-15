import os
import re

import tools

HELP = """\
tasks, domains and suites can be specified in the following ways: gripper, gripper:prob01.pddl, \
TEST, mysuitefile.py:myTEST, TEST_FIRST5, mysuitefile.py:myTEST_FIRST5
The python modules have to live in the scripts dir.
"""

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCHMARKS_DIR = os.path.join(ROOT_DIR, "benchmarks")


class Repository(object):
    def __init__(self):
        domains = [d for d in os.listdir(BENCHMARKS_DIR)
                   if not d.startswith(".")]
        domains.sort()
        self.domains = [Domain(domain) for domain in domains]
    def __iter__(self):
        return iter(self.domains)
        

class Domain(object):
    def __init__(self, domain):
        self.domain = domain
        self.directory = os.path.join(BENCHMARKS_DIR, domain)
        problems = os.listdir(self.directory)
        problems = [p for p in problems if "domain" not in p
                    and not p.startswith(".")]
        tools.natural_sort(problems)
        self.problems = [Problem(domain, problem) for problem in problems]
    def __str__(self):
        return self.domain
    def __repr__(self):
        return "<Domain %s>" % self.domain
    def __hash__(self):
        return hash(self.domain)
    def __cmp__(self, other):
        return cmp(self.domain, other.domain)
    def __iter__(self):
        return iter(self.problems)
        

class Problem(object):
    def __init__(self, domain, problem):
        self.domain = domain
        self.problem = problem
    def __str__(self):
        return "%s:%s" % (self.domain, self.problem)
    def __repr__(self):
        return "<Problem %s:%s>" % (self.domain, self.problem)
    def __hash__(self):
        return hash((self.domain, self.problem))
    def __cmp__(self, other):
        return cmp((self.domain, self.problem), (other.domain, other.problem))
    def problem_file(self):
        return os.path.join(BENCHMARKS_DIR, self.domain, self.problem)
    def domain_file(self):
        domain_basenames = ["domain.pddl",
                            self.problem[:4] + "domain.pddl",
                            self.problem[:3] + "-domain.pddl",
                            "domain_" + self.problem]
        domain_dir = os.path.join(BENCHMARKS_DIR, self.domain)
        return tools.find_file(domain_basenames, domain_dir)


def generate_problems(description):
    """
    Descriptions have the form:
    
    gripper:prob01.pddl
    gripper
    TEST
    mysuitefile.py:mytest
    mysuitefile.py:MYTEST
    
    TEST_FIRST5
    mysuitefile.py:MYTEST_FIRST5
    """
    if description.upper().endswith('FIRST'):
        # Allow writing SUITE_NAME_FIRST
        # This will work for all suites that only list domains and will
        # return the first problem of each domain
        description += '1'
        
    number_expr = re.compile(r'.*FIRST([-]?\d+)', re.IGNORECASE)
    number_result = number_expr.search(description)
    
    
    if '.py:' in description:
        filename, rest = description.split(':', 1)
        description = rest
    else:
        filename = __file__
    
    module = tools.import_python_file(filename)
    module_dict = module.__dict__
        
    if number_result:
        # Allow writing SUITE_NAME_FIRSTn
        # This will work for all suites that only list domains and will
        # return the first n problems of each domain
        number = int(number_result.group(1))
        assert number >= 1, number
        suite_name, first_text = description.rsplit('_', 1)
        suite_func = module_dict.get(suite_name, None)
        if suite_func is None:
            suite_func = module_dict.get("suite_%s" % suite_name.lower(), None)
        if not suite_func:
            raise SystemExit("unknown suite: %s" % suite_funcname)
        for domain_name in suite_func():
            domain = Domain(domain_name)
            for problem in domain.problems[:number]:
                yield problem
    elif isinstance(description, Problem):
        yield description
    elif isinstance(description, Domain):
        for problem in description:
            yield problem
    elif description.isupper() or description in module_dict:
        suite_func = module_dict.get(description, None)
        if suite_func is None:
            suite_func = module_dict.get("suite_%s" % description.lower(), None)
        if suite_func is None:
            raise SystemExit("unknown suite: %s" % description)
        for element in suite_func():
            for problem in generate_problems(element):
                yield problem
    elif ":" in description:
        domain_name, problem_name = description.split(":", 1)
        yield Problem(domain_name, problem_name)
    else:
        for problem in Domain(description):
            yield problem


def build_suite(descriptions):
    result = []
    for description in descriptions:
        result.extend(generate_problems(description))
    return result


def suite_ipc_one_to_five():
    # All IPC1-5 domains, including the trivial Movie.
    return [
        "airport", "assembly", "blocks", "depot", "driverlog",
        "freecell", "grid", "gripper", "logistics00", "logistics98",
        "miconic", "miconic-fulladl", "miconic-simpleadl", "movie", "mprime",
        "mystery", "openstacks", "optical-telegraphs", "pathways",
        "philosophers", "pipesworld-notankage", "pipesworld-tankage",
        "psr-large", "psr-middle", "psr-small", "rovers", "satellite",
        "schedule", "storage", "tpp", "trucks", "zenotravel",
        ]

def suite_interesting():
    # A domain is boring if all planners solve all tasks in < 1 sec.
    # We include logistics00 even though it has that property because
    # we merge its results with logistics98 (which doesn't).
    boring = set(["gripper", "miconic", "miconic-simpleadl", "movie"])
    return [domain for domain in suite_all() if domain not in boring]

def suite_first_tasks():
    suite = []
    for domain in suite_all():
        tasks = list(Domain(domain))
        suite.append(tasks[0])
    suite = build_suite(suite)
    unsolvable = set(build_suite(suite_unsolvable()))
    return [p for p in suite if p not in unsolvable]

def suite_unsolvable():
    # TODO: Add other unsolvable problems (Miconic-FullADL).
    return ["mystery:prob%02d.pddl" % index
            for index in [4, 5, 7, 8, 12, 16, 18, 21, 22, 23, 24]]

def suite_test():
    # Three smallish domains for quick tests.
    return ["grid", "gripper", "blocks"]

def suite_minitest():
    return ["gripper:prob01.pddl", "gripper:prob02.pddl", 
            "gripper:prob03.pddl", "zenotravel:pfile1",
            "zenotravel:pfile2", "zenotravel:pfile3", ]
            
def suite_tinytest():
    return ["gripper:prob01.pddl", "trucks-strips:p01.pddl",
            "trucks:p01.pddl", "psr-middle:p01-s17-n2-l2-f30.pddl"]
            
def suite_everything():
    return suite_all() + ['openstacks-strips', 'pathways-noneg', 'trucks-strips']


def suite_lmcut_domains():
    return ["airport",
            "blocks",
            "depot",
            "driverlog",
            "freecell",
            "grid",
            "gripper",
            "logistics00",
            "logistics98",
            "miconic",
            "mprime",
            "mystery",
            "openstacks-strips",
            "pathways-noneg",
            "pipesworld-notankage",
            "pipesworld-tankage",
            "psr-small",
            "rovers",
            "satellite",
            "tpp",
            "trucks-strips",
            "zenotravel",
            ]
            

def suite_strips():
    # like suite_lmcut_domains, but without openstacks-strips (which has
    # many translator timeouts).
    return ["airport",
            "blocks",
            "depot",
            "driverlog",
            "freecell",
            "grid",
            "gripper",
            "logistics00",
            "logistics98",
            "miconic",
            "mprime",
            "mystery",
            "pathways-noneg",
            "pipesworld-notankage",
            "pipesworld-tankage",
            "psr-small",
            "rovers",
            "satellite",
            "tpp",
            "trucks-strips",
            "zenotravel",
            ]
            
def suite_all():
    domains = suite_ipc_one_to_five() + suite_lmcut_domains()
    domains += ['seq-sat', 'seq-opt']
    return list(sorted(set(domains)))
            

def suite_five_per_domain():
    for domain in Repository():
        problems = list(domain)
        for item in select_evenly_spread(problems, 5):
            yield item


def select_evenly_spread(seq, num_items):
   """Return num_items many items of seq, spread evenly.
   If seq is shorter than num_items, include all items.
   Otherwise, include first and last items and spread evenly in between.
   (If num_items is 1, only include first item.)

   Example:
   >>> select_evenly_spread("abcdef", 3)
   ['a', 'd', 'f']
   """
   if len(seq) <= num_items:
      return seq
   if num_items == 1:
      return [seq[0]]
   step_size = (len(seq) - 1) / float(num_items - 1)
   float_indices = [i * step_size for i in range(num_items)]
   return [seq[int(round(index))] for index in float_indices]
   
   
if __name__ == '__main__':
    print build_suite([
        'gripper', 
        'gripper:prob01.pddl',
        # Four times the same suite:
        'downward_suites.py:TEST',
        'downward_suites.py:suite_test',
        'TEST',
        'suite_test',
        # Four times the same suite:
        'downward_suites.py:TEST_FIRST',
        'downward_suites.py:suite_test_first',
        'TEST_FIRST',
        'suite_test_first',
        # Four times the same suite:
        'downward_suites.py:TEST_FIRST2',
        'downward_suites.py:suite_test_first2',
        'TEST_FIRST2',
        'suite_test_first2',
        ])
