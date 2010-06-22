import os

import tools

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BENCHMARKS_DIR = os.path.join(ROOT_DIR, "benchmarks")
RESULTS_DIR = os.path.join(ROOT_DIR, "results")

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

class ResultFiles(object):
    def __init__(self, algorithm, args, problem):
        base, _ = os.path.splitext(os.path.basename(problem.problem))
        version = "version-" + args
        self.alg_dir = os.path.join(RESULTS_DIR, algorithm, version)
        self.domain_dir = os.path.join(RESULTS_DIR, algorithm, version, 
                                        problem.domain)
        self.base_name = os.path.join(RESULTS_DIR, algorithm, version, 
                                        problem.domain, base)
    def algorithm_directory(self):
        return self.alg_dir
    def domain_directory(self):
        return self.domain_dir
    def global_log(self):
        return self.base_name + ".log"
    def translate_log(self):
        return self.base_name + ".tlog"
    def preprocess_log(self):
        return self.base_name + ".plog"
    def search_log(self):
        return self.base_name + ".slog"
    def translate_out(self):
        return self.base_name + ".sas"
    def translate_group(self):
        return self.base_name + ".groups"
    def translate_group2(self):
        return self.base_name + ".groups2"
    def preprocess_out(self):
        return self.base_name + ".pre"
    def search_out(self):
        return self.base_name + ".out"
    def solution(self):
        return self.base_name + ".soln"


def generate_problems(description):
    if isinstance(description, Problem):
        yield description
    elif isinstance(description, Domain):
        for problem in description:
            yield problem
    elif description.isupper():
        suite_funcname = "suite_%s" % description.lower()
        suite_func = globals().get(suite_funcname)
        if not suite_func:
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


def suite_all():
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

def suite_icaps04_paper():
    # The domains considered in the ICAPS 2004 CG heuristic paper, i.e.,
    # all IPC 1-3 STRIPS domains.
    suite = [
        "blocks", "depot", "driverlog", "freecell", "grid", "gripper",
        "logistics00", "logistics98", "miconic", "movie", "mprime", "mystery",
        "zenotravel",
        ]

    # Only the first 20 Rovers and Satellite tasks are from IPC3.
    # The remaining ones were introduced later.
    for domain in ["rovers", "satellite"]:
        tasks = list(Domain(domain))
        suite += tasks[:20]

    suite = build_suite(suite)
    unsolvable = set(build_suite(suite_unsolvable()))
    return [p for p in suite if p not in unsolvable]

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

def suite_memory_glitches():
    # Problems for which "y" and "yY" ran into memory issues on
    # initialization.
    return ["logistics98:prob28.pddl",
            "satellite:p31-HC-pfile11.pddl",
            "satellite:p32-HC-pfile12.pddl",
            "satellite:p33-HC-pfile13.pddl",
            "satellite:p34-HC-pfile14.pddl",
            "satellite:p35-HC-pfile15.pddl",
            "satellite:p36-HC-pfile16.pddl",
            "airport:p29-airport4halfMUC-p8.pddl",
            "airport:p30-airport4halfMUC-p8.pddl",
            "airport:p31-airport4halfMUC-p9.pddl",
            "airport:p32-airport4halfMUC-p10.pddl",
            "airport:p33-airport4halfMUC-p10.pddl",
            "airport:p34-airport4halfMUC-p11.pddl",
            "airport:p35-airport4halfMUC-p12.pddl",
            "airport:p42-airport5MUC-p5.pddl",
            "airport:p43-airport5MUC-p5.pddl",
            "airport:p44-airport5MUC-p5.pddl",
            "airport:p45-airport5MUC-p6.pddl",
            "airport:p46-airport5MUC-p6.pddl",
            "airport:p47-airport5MUC-p8.pddl",
            "airport:p48-airport5MUC-p9.pddl",
            "airport:p49-airport5MUC-p10.pddl",
            "airport:p50-airport5MUC-p15.pddl"]

def suite_test():
    # Three smallish domains for quick tests.
    return ["grid", "gripper", "blocks"]


def suite_experiment1_unsolved_all():
    # All the tasks that *at least one* of the configurations cC, aA,
    # fF and yY did not solve in the first experiment of the ICAPS
    # 2008 paper.
    return [
        "depot:pfile12",
        "depot:pfile14",
        "depot:pfile15",
        "depot:pfile17",
        "depot:pfile18",
        "depot:pfile19",
        "depot:pfile20",
        "depot:pfile21",
        "depot:pfile22",
        "depot:pfile6",
        "depot:pfile9",
        "driverlog:pfile16",
        "driverlog:pfile20",
        "freecell:pfile18",
        "freecell:pfile19",
        "freecell:pfile20",
        "freecell:probfreecell-11-1.pddl",
        "freecell:probfreecell-11-3.pddl",
        "freecell:probfreecell-11-4.pddl",
        "freecell:probfreecell-11-5.pddl",
        "freecell:probfreecell-12-1.pddl",
        "freecell:probfreecell-12-4.pddl",
        "freecell:probfreecell-12-5.pddl",
        "freecell:probfreecell-13-5.pddl",
        "grid:prob04.pddl",
        "grid:prob05.pddl",
        "logistics98:prob15.pddl",
        "logistics98:prob20.pddl",
        "logistics98:prob22.pddl",
        "logistics98:prob25.pddl",
        "logistics98:prob26.pddl",
        "logistics98:prob28.pddl",
        "mprime:prob06.pddl",
        "mprime:prob10.pddl",
        "mprime:prob14.pddl",
        "mprime:prob18.pddl",
        "mprime:prob20.pddl",
        "mprime:prob22.pddl",
        "mprime:prob23.pddl",
        "mystery:prob06.pddl",
        "mystery:prob10.pddl",
        "mystery:prob13.pddl",
        "mystery:prob14.pddl",
        "satellite:p20-pfile20.pddl",
        ]


def suite_experiment1_unsolved_hcea():
    # All the tasks that yY did not solve in the first experiment of
    # the ICAPS 2008 paper.
    return [
        "depot:pfile12",
        "depot:pfile17",
        "depot:pfile18",
        "depot:pfile19",
        "depot:pfile20",
        "depot:pfile22",
        "depot:pfile6",
        "depot:pfile9",
        "driverlog:pfile16",
        "driverlog:pfile20",
        "freecell:pfile19",
        "freecell:pfile20",
        "freecell:probfreecell-11-1.pddl",
        "freecell:probfreecell-11-5.pddl",
        "freecell:probfreecell-12-5.pddl",
        "freecell:probfreecell-13-5.pddl",
        "grid:prob05.pddl",
        ]


def suite_minitest():
    return ["gripper:prob01.pddl", "zenotravel:pfile1"]


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
            

def suite_lmcut_solvable():
    suite = build_suite(suite_lmcut_domains())
    unsolvable = set(build_suite(suite_unsolvable()))
    return [p for p in suite if p not in unsolvable]


def suite_lmcut_test():
    for domain in suite_lmcut_domains():
        yield iter(Domain(domain)).next()


def lmcut_pairs():
    tasks = []
    for domain_name in suite_lmcut_domains():
        tasks.extend(list(enumerate(Domain(domain_name))))
    tasks.sort()
    return tasks


def suite_lmcut_odd():
    for num, task in lmcut_pairs():
        if num % 2 == 0:
            yield task


def suite_lmcut_even():
    for num, task in lmcut_pairs():
        if num % 2 == 1:
            yield task


def suite_lmcut_turtur():
    # DOMAINS = ["miconic", "logistics00", "psr-small", "airport"]
    # DOMAINS = ["pipesworld-notankage", "pipesworld-tankage"]
    DOMAINS = ["pathways", "tpp"]
    for num, task in lmcut_pairs():
        if num >= 20 and task.domain in DOMAINS:
            yield task
    

def suite_lmcut_habakuk():
    # DOMAINS = ["blocks", "mystery", "mprime", "logistics98"]
    # DOMAINS = ["depot", "driverlog", "freecell"]
    DOMAINS = ["rovers", "zenotravel"]
    for num, task in lmcut_pairs():
        if num >= 20 and task.domain in DOMAINS:
            yield task


def suite_lmcut_reference():
    # Tasks solved by the first (buggy and hence not guaranteed to be
    # optimal) implementation.
    return [
        "airport:p01-airport1-p1.pddl",  # 0 sec
        "airport:p02-airport1-p1.pddl",  # 0 sec
        "airport:p03-airport1-p2.pddl",  # 0 sec
        "airport:p04-airport2-p1.pddl",  # 0 sec
        "airport:p05-airport2-p1.pddl",  # 0 sec
        "airport:p06-airport2-p2.pddl",  # 0 sec
        "airport:p07-airport2-p2.pddl",  # 0 sec
        "airport:p10-airport3-p1.pddl",  # 0 sec
        "airport:p11-airport3-p1.pddl",  # 0 sec
        "airport:p12-airport3-p2.pddl",  # 0 sec
        "airport:p13-airport3-p2.pddl",  # 0 sec
        "airport:p14-airport3-p3.pddl",  # 0 sec
        "airport:p15-airport3-p3.pddl",  # 0 sec
        "blocks:probBLOCKS-4-0.pddl",  # 0 sec
        "blocks:probBLOCKS-4-1.pddl",  # 0 sec
        "blocks:probBLOCKS-4-2.pddl",  # 0 sec
        "blocks:probBLOCKS-5-0.pddl",  # 0 sec
        "blocks:probBLOCKS-5-1.pddl",  # 0 sec
        "blocks:probBLOCKS-5-2.pddl",  # 0 sec
        "blocks:probBLOCKS-6-0.pddl",  # 0 sec
        "blocks:probBLOCKS-6-1.pddl",  # 0 sec
        "blocks:probBLOCKS-6-2.pddl",  # 0 sec
        "blocks:probBLOCKS-7-0.pddl",  # 0 sec
        "blocks:probBLOCKS-7-1.pddl",  # 0 sec
        "blocks:probBLOCKS-7-2.pddl",  # 0 sec
        "blocks:probBLOCKS-8-0.pddl",  # 0 sec
        "blocks:probBLOCKS-8-1.pddl",  # 0 sec
        "blocks:probBLOCKS-8-2.pddl",  # 0 sec
        "blocks:probBLOCKS-9-1.pddl",  # 0 sec
        "blocks:probBLOCKS-9-2.pddl",  # 0 sec
        "depot:pfile1",  # 0 sec
        "depot:pfile2",  # 0 sec
        "driverlog:pfile1",  # 0 sec
        "driverlog:pfile10",  # 0 sec
        "driverlog:pfile11",  # 0 sec
        "driverlog:pfile3",  # 0 sec
        "driverlog:pfile5",  # 0 sec
        "driverlog:pfile6",  # 0 sec
        "driverlog:pfile7",  # 0 sec
        "freecell:pfile1",  # 0 sec
        "grid:prob01.pddl",  # 0 sec
        "gripper:prob01.pddl",  # 0 sec
        "gripper:prob02.pddl",  # 0 sec
        "logistics00:probLOGISTICS-4-0.pddl",  # 0 sec
        "logistics00:probLOGISTICS-4-1.pddl",  # 0 sec
        "logistics00:probLOGISTICS-4-2.pddl",  # 0 sec
        "logistics00:probLOGISTICS-5-0.pddl",  # 0 sec
        "logistics00:probLOGISTICS-5-1.pddl",  # 0 sec
        "logistics00:probLOGISTICS-5-2.pddl",  # 0 sec
        "logistics00:probLOGISTICS-6-1.pddl",  # 0 sec
        "logistics00:probLOGISTICS-6-2.pddl",  # 0 sec
        "logistics00:probLOGISTICS-6-9.pddl",  # 0 sec
        "logistics98:prob05.pddl",  # 0 sec
        "logistics98:prob31.pddl",  # 0 sec
        "logistics98:prob32.pddl",  # 0 sec
        "miconic:s10-0.pddl",  # 0 sec
        "miconic:s10-1.pddl",  # 0 sec
        "miconic:s10-2.pddl",  # 0 sec
        "miconic:s10-3.pddl",  # 0 sec
        "miconic:s10-4.pddl",  # 0 sec
        "miconic:s1-0.pddl",  # 0 sec
        "miconic:s11-0.pddl",  # 0 sec
        "miconic:s11-1.pddl",  # 0 sec
        "miconic:s11-2.pddl",  # 0 sec
        "miconic:s11-4.pddl",  # 0 sec
        "miconic:s1-1.pddl",  # 0 sec
        "miconic:s12-0.pddl",  # 0 sec
        "miconic:s12-1.pddl",  # 0 sec
        "miconic:s12-2.pddl",  # 0 sec
        "miconic:s12-3.pddl",  # 0 sec
        "miconic:s12-4.pddl",  # 0 sec
        "miconic:s1-2.pddl",  # 0 sec
        "miconic:s13-0.pddl",  # 0 sec
        "miconic:s13-2.pddl",  # 0 sec
        "miconic:s13-3.pddl",  # 0 sec
        "miconic:s13-4.pddl",  # 0 sec
        "miconic:s1-3.pddl",  # 0 sec
        "miconic:s1-4.pddl",  # 0 sec
        "miconic:s2-0.pddl",  # 0 sec
        "miconic:s2-1.pddl",  # 0 sec
        "miconic:s2-2.pddl",  # 0 sec
        "miconic:s2-3.pddl",  # 0 sec
        "miconic:s2-4.pddl",  # 0 sec
        "miconic:s3-0.pddl",  # 0 sec
        "miconic:s3-1.pddl",  # 0 sec
        "miconic:s3-2.pddl",  # 0 sec
        "miconic:s3-3.pddl",  # 0 sec
        "miconic:s3-4.pddl",  # 0 sec
        "miconic:s4-0.pddl",  # 0 sec
        "miconic:s4-1.pddl",  # 0 sec
        "miconic:s4-2.pddl",  # 0 sec
        "miconic:s4-3.pddl",  # 0 sec
        "miconic:s4-4.pddl",  # 0 sec
        "miconic:s5-0.pddl",  # 0 sec
        "miconic:s5-1.pddl",  # 0 sec
        "miconic:s5-2.pddl",  # 0 sec
        "miconic:s5-3.pddl",  # 0 sec
        "miconic:s5-4.pddl",  # 0 sec
        "miconic:s6-0.pddl",  # 0 sec
        "miconic:s6-1.pddl",  # 0 sec
        "miconic:s6-2.pddl",  # 0 sec
        "miconic:s6-3.pddl",  # 0 sec
        "miconic:s6-4.pddl",  # 0 sec
        "miconic:s7-0.pddl",  # 0 sec
        "miconic:s7-1.pddl",  # 0 sec
        "miconic:s7-2.pddl",  # 0 sec
        "miconic:s7-3.pddl",  # 0 sec
        "miconic:s7-4.pddl",  # 0 sec
        "miconic:s8-0.pddl",  # 0 sec
        "miconic:s8-2.pddl",  # 0 sec
        "miconic:s8-3.pddl",  # 0 sec
        "miconic:s8-4.pddl",  # 0 sec
        "miconic:s9-0.pddl",  # 0 sec
        "miconic:s9-1.pddl",  # 0 sec
        "miconic:s9-2.pddl",  # 0 sec
        "miconic:s9-3.pddl",  # 0 sec
        "mprime:prob01.pddl",  # 0 sec
        "mprime:prob03.pddl",  # 0 sec
        "mprime:prob07.pddl",  # 0 sec
        "mprime:prob11.pddl",  # 0 sec
        "mprime:prob12.pddl",  # 0 sec
        "mprime:prob25.pddl",  # 0 sec
        "mprime:prob28.pddl",  # 0 sec
        "mprime:prob29.pddl",  # 0 sec
        "mprime:prob31.pddl",  # 0 sec
        "mprime:prob34.pddl",  # 0 sec
        "mprime:prob35.pddl",  # 0 sec
        "mystery:prob01.pddl",  # 0 sec
        "mystery:prob03.pddl",  # 0 sec
        "mystery:prob09.pddl",  # 0 sec
        "mystery:prob11.pddl",  # 0 sec
        "mystery:prob25.pddl",  # 0 sec
        "mystery:prob26.pddl",  # 0 sec
        "mystery:prob27.pddl",  # 0 sec
        "mystery:prob28.pddl",  # 0 sec
        "mystery:prob29.pddl",  # 0 sec
        "pathways:p01.pddl",  # 0 sec
        "pathways:p02.pddl",  # 0 sec
        "pathways:p03.pddl",  # 0 sec
        "pathways:p04.pddl",  # 0 sec
        "pipesworld-notankage:p01-net1-b6-g2.pddl",  # 0 sec
        "pipesworld-notankage:p02-net1-b6-g4.pddl",  # 0 sec
        "pipesworld-notankage:p03-net1-b8-g3.pddl",  # 0 sec
        "pipesworld-notankage:p04-net1-b8-g5.pddl",  # 0 sec
        "pipesworld-notankage:p05-net1-b10-g4.pddl",  # 0 sec
        "pipesworld-notankage:p06-net1-b10-g6.pddl",  # 0 sec
        "pipesworld-notankage:p07-net1-b12-g5.pddl",  # 0 sec
        "pipesworld-notankage:p08-net1-b12-g7.pddl",  # 0 sec
        "pipesworld-tankage:p01-net1-b6-g2-t50.pddl",  # 0 sec
        "pipesworld-tankage:p02-net1-b6-g4-t50.pddl",  # 0 sec
        "pipesworld-tankage:p05-net1-b10-g4-t50.pddl",  # 0 sec
        "psr-small:p01-s2-n1-l2-f50.pddl",  # 0 sec
        "psr-small:p02-s5-n1-l3-f30.pddl",  # 0 sec
        "psr-small:p03-s7-n1-l3-f70.pddl",  # 0 sec
        "psr-small:p04-s8-n1-l4-f10.pddl",  # 0 sec
        "psr-small:p05-s9-n1-l4-f30.pddl",  # 0 sec
        "psr-small:p06-s10-n1-l4-f50.pddl",  # 0 sec
        "psr-small:p07-s11-n1-l4-f70.pddl",  # 0 sec
        "psr-small:p08-s12-n1-l5-f10.pddl",  # 0 sec
        "psr-small:p09-s13-n1-l5-f30.pddl",  # 0 sec
        "psr-small:p10-s17-n2-l2-f30.pddl",  # 0 sec
        "psr-small:p11-s18-n2-l2-f50.pddl",  # 0 sec
        "psr-small:p12-s21-n2-l3-f30.pddl",  # 0 sec
        "psr-small:p13-s22-n2-l3-f50.pddl",  # 0 sec
        "psr-small:p14-s23-n2-l3-f70.pddl",  # 0 sec
        "psr-small:p15-s24-n2-l4-f10.pddl",  # 0 sec
        "psr-small:p16-s29-n2-l5-f30.pddl",  # 0 sec
        "psr-small:p17-s30-n2-l5-f50.pddl",  # 0 sec
        "psr-small:p18-s31-n2-l5-f70.pddl",  # 0 sec
        "psr-small:p20-s34-n3-l2-f50.pddl",  # 0 sec
        "psr-small:p21-s35-n3-l2-f70.pddl",  # 0 sec
        "psr-small:p23-s38-n3-l3-f50.pddl",  # 0 sec
        "psr-small:p24-s39-n3-l3-f70.pddl",  # 0 sec
        "psr-small:p26-s41-n3-l4-f30.pddl",  # 0 sec
        "psr-small:p27-s42-n3-l4-f50.pddl",  # 0 sec
        "psr-small:p28-s43-n3-l4-f70.pddl",  # 0 sec
        "psr-small:p30-s46-n3-l5-f50.pddl",  # 0 sec
        "psr-small:p32-s50-n4-l2-f50.pddl",  # 0 sec
        "psr-small:p33-s51-n4-l2-f70.pddl",  # 0 sec
        "psr-small:p34-s55-n4-l3-f70.pddl",  # 0 sec
        "psr-small:p37-s67-n6-l2-f70.pddl",  # 0 sec
        "psr-small:p38-s78-n3-l3-f50.pddl",  # 0 sec
        "psr-small:p39-s79-n3-l3-f70.pddl",  # 0 sec
        "psr-small:p41-s81-n3-l4-f30.pddl",  # 0 sec
        "psr-small:p42-s82-n3-l4-f50.pddl",  # 0 sec
        "psr-small:p43-s83-n3-l4-f70.pddl",  # 0 sec
        "psr-small:p44-s89-n4-l2-f30.pddl",  # 0 sec
        "psr-small:p45-s94-n4-l3-f50.pddl",  # 0 sec
        "psr-small:p47-s98-n5-l2-f50.pddl",  # 0 sec
        "psr-small:p50-s107-n6-l2-f70.pddl",  # 0 sec
        "rovers:p01.pddl",  # 0 sec
        "rovers:p02.pddl",  # 0 sec
        "rovers:p03.pddl",  # 0 sec
        "rovers:p04.pddl",  # 0 sec
        "tpp:p01.pddl",  # 0 sec
        "tpp:p02.pddl",  # 0 sec
        "tpp:p03.pddl",  # 0 sec
        "tpp:p04.pddl",  # 0 sec
        "tpp:p05.pddl",  # 0 sec
        "zenotravel:pfile1",  # 0 sec
        "zenotravel:pfile2",  # 0 sec
        "zenotravel:pfile3",  # 0 sec
        "zenotravel:pfile4",  # 0 sec
        "zenotravel:pfile5",  # 0 sec
        "zenotravel:pfile6",  # 0 sec
        "zenotravel:pfile8",  # 0 sec
        "driverlog:pfile4",  # 1 sec
        "freecell:probfreecell-2-1.pddl",  # 1 sec
        "freecell:probfreecell-2-2.pddl",  # 1 sec
        "logistics00:probLOGISTICS-6-0.pddl",  # 1 sec
        "miconic:s14-0.pddl",  # 1 sec
        "miconic:s14-1.pddl",  # 1 sec
        "miconic:s14-2.pddl",  # 1 sec
        "miconic:s14-3.pddl",  # 1 sec
        "miconic:s14-4.pddl",  # 1 sec
        "miconic:s15-0.pddl",  # 1 sec
        "miconic:s15-1.pddl",  # 1 sec
        "miconic:s15-2.pddl",  # 1 sec
        "miconic:s15-3.pddl",  # 1 sec
        "miconic:s15-4.pddl",  # 1 sec
        "miconic:s16-0.pddl",  # 1 sec
        "miconic:s16-1.pddl",  # 1 sec
        "miconic:s16-2.pddl",  # 1 sec
        "miconic:s16-4.pddl",  # 1 sec
        "miconic:s8-1.pddl",  # 1 sec
        "pipesworld-tankage:p06-net1-b10-g6-t50.pddl",  # 1 sec
        "psr-small:p19-s33-n3-l2-f30.pddl",  # 1 sec
        "zenotravel:pfile7",  # 1 sec
        "driverlog:pfile2",  # 2 sec
        "freecell:probfreecell-2-3.pddl",  # 2 sec
        "freecell:probfreecell-2-4.pddl",  # 2 sec
        "gripper:prob03.pddl",  # 2 sec
        "miconic:s17-3.pddl",  # 2 sec
        "mprime:prob09.pddl",  # 2 sec
        "mystery:prob17.pddl",  # 2 sec
        "pipesworld-tankage:p03-net1-b8-g3-t80.pddl",  # 2 sec
        "airport:p08-airport2-p3.pddl",  # 3 sec
        "airport:p16-airport3-p4.pddl",  # 3 sec
        "logistics00:probLOGISTICS-9-1.pddl",  # 3 sec
        "miconic:s16-3.pddl",  # 3 sec
        "miconic:s17-0.pddl",  # 3 sec
        "miconic:s17-1.pddl",  # 3 sec
        "miconic:s17-2.pddl",  # 3 sec
        "miconic:s18-0.pddl",  # 3 sec
        "miconic:s18-2.pddl",  # 3 sec
        "miconic:s18-3.pddl",  # 3 sec
        "miconic:s18-4.pddl",  # 3 sec
        "miconic:s9-4.pddl",  # 3 sec
        "mystery:prob02.pddl",  # 3 sec
        "pipesworld-notankage:p09-net1-b14-g6.pddl",  # 3 sec
        "airport:p21-airport4halfMUC-p2.pddl",  # 4 sec
        "miconic:s18-1.pddl",  # 4 sec
        "miconic:s19-1.pddl",  # 4 sec
        "miconic:s19-4.pddl",  # 4 sec
        "mprime:prob04.pddl",  # 4 sec
        "mprime:prob32.pddl",  # 4 sec
        "freecell:probfreecell-2-5.pddl",  # 5 sec
        "miconic:s19-0.pddl",  # 5 sec
        "miconic:s20-1.pddl",  # 5 sec
        "miconic:s19-3.pddl",  # 6 sec
        "miconic:s20-4.pddl",  # 6 sec
        "miconic:s21-2.pddl",  # 6 sec
        "mprime:prob27.pddl",  # 6 sec
        "pipesworld-notankage:p21-net3-b12-g2.pddl",  # 6 sec
        "psr-small:p35-s57-n5-l2-f30.pddl",  # 6 sec
        "airport:p36-airport5MUC-p2.pddl",  # 7 sec
        "miconic:s20-3.pddl",  # 7 sec
        "miconic:s21-1.pddl",  # 7 sec
        "miconic:s21-3.pddl",  # 7 sec
        "miconic:s21-4.pddl",  # 7 sec
        "miconic:s21-0.pddl",  # 8 sec
        "miconic:s22-3.pddl",  # 8 sec
        "miconic:s22-4.pddl",  # 8 sec
        "mystery:prob15.pddl",  # 8 sec
        "psr-small:p31-s49-n4-l2-f30.pddl",  # 8 sec
        "zenotravel:pfile11",  # 8 sec
        "mystery:prob20.pddl",  # 9 sec
        "pipesworld-notankage:p13-net2-b12-g3.pddl",  # 9 sec
        "airport:p19-airport3-p6.pddl",  # 10 sec
        "miconic:s22-0.pddl",  # 10 sec
        "miconic:s23-4.pddl",  # 10 sec
        "psr-small:p46-s97-n5-l2-f30.pddl",  # 10 sec
        "logistics00:probLOGISTICS-8-0.pddl",  # 11 sec
        "miconic:s22-1.pddl",  # 12 sec
        "miconic:s24-3.pddl",  # 12 sec
        "mprime:prob26.pddl",  # 12 sec
        "pipesworld-tankage:p04-net1-b8-g5-t80.pddl",  # 12 sec
        "miconic:s22-2.pddl",  # 13 sec
        "miconic:s23-0.pddl",  # 13 sec
        "miconic:s23-2.pddl",  # 13 sec
        "miconic:s24-0.pddl",  # 13 sec
        "depot:pfile13",  # 14 sec
        "depot:pfile3",  # 14 sec
        "miconic:s20-2.pddl",  # 14 sec
        "miconic:s24-2.pddl",  # 15 sec
        "depot:pfile7",  # 16 sec
        "gripper:prob04.pddl",  # 16 sec
        "miconic:s25-3.pddl",  # 16 sec
        "rovers:p07.pddl",  # 16 sec
        "driverlog:pfile9",  # 17 sec
        "miconic:s24-1.pddl",  # 17 sec
        "miconic:s24-4.pddl",  # 17 sec
        "airport:p22-airport4halfMUC-p3.pddl",  # 18 sec
        "blocks:probBLOCKS-12-1.pddl",  # 19 sec
        "miconic:s25-1.pddl",  # 19 sec
        "miconic:s25-4.pddl",  # 19 sec
        "mystery:prob19.pddl",  # 19 sec
        "miconic:s25-0.pddl",  # 20 sec
        "miconic:s26-4.pddl",  # 20 sec
        "blocks:probBLOCKS-9-0.pddl",  # 21 sec
        "miconic:s26-0.pddl",  # 21 sec
        "psr-small:p29-s45-n3-l5-f30.pddl",  # 21 sec
        "mystery:prob30.pddl",  # 22 sec
        "mprime:prob17.pddl",  # 23 sec
        "logistics00:probLOGISTICS-7-0.pddl",  # 24 sec
        "miconic:s26-3.pddl",  # 24 sec
        "miconic:s26-2.pddl",  # 25 sec
        "miconic:s27-1.pddl",  # 25 sec
        "psr-small:p22-s37-n3-l3-f30.pddl",  # 25 sec
        "miconic:s28-0.pddl",  # 27 sec
        "rovers:p12.pddl",  # 27 sec
        "miconic:s27-3.pddl",  # 28 sec
        "mprime:prob02.pddl",  # 28 sec
        "rovers:p05.pddl",  # 28 sec
        "psr-small:p25-s40-n3-l4-f10.pddl",  # 30 sec
        "miconic:s27-4.pddl",  # 31 sec
        "miconic:s28-4.pddl",  # 32 sec
        "miconic:s28-2.pddl",  # 33 sec
        "miconic:s27-2.pddl",  # 34 sec
        "miconic:s28-3.pddl",  # 35 sec
        "zenotravel:pfile10",  # 36 sec
        "tpp:p06.pddl",  # 37 sec
        "freecell:pfile2",  # 38 sec
        "airport:p23-airport4halfMUC-p4.pddl",  # 40 sec
        "miconic:s29-0.pddl",  # 42 sec
        "miconic:s30-2.pddl",  # 42 sec
        "miconic:s30-4.pddl",  # 42 sec
        "miconic:s29-4.pddl",  # 43 sec
        "miconic:s30-1.pddl",  # 46 sec
        "pipesworld-tankage:p07-net1-b12-g5-t80.pddl",  # 46 sec
        "miconic:s30-0.pddl",  # 47 sec
        "miconic:s29-2.pddl",  # 48 sec
        "airport:p24-airport4halfMUC-p4.pddl",  # 51 sec
        "pipesworld-notankage:p11-net2-b10-g2.pddl",  # 54 sec
        "miconic:s29-3.pddl",  # 55 sec
        "airport:p09-airport2-p4.pddl",  # 57 sec
        "miconic:s29-1.pddl",  # 58 sec
        "blocks:probBLOCKS-10-1.pddl",  # 60 sec
        "logistics00:probLOGISTICS-9-0.pddl",  # 62 sec
        "freecell:pfile3",  # 69 sec
        "zenotravel:pfile9",  # 75 sec
        "logistics98:prob35.pddl",  # 76 sec
        "depot:pfile10",  # 93 sec
        "logistics98:prob01.pddl",  # 94 sec
        "airport:p20-airport3-p7.pddl",  # 107 sec
        "miconic:s11-3.pddl",  # 107 sec
        "airport:p17-airport3-p5.pddl",  # 108 sec
        "grid:prob02.pddl",  # 112 sec
        "psr-small:p40-s80-n3-l4-f10.pddl",  # 118 sec
        "blocks:probBLOCKS-11-2.pddl",  # 125 sec
        "gripper:prob05.pddl",  # 134 sec
        "mprime:prob08.pddl",  # 146 sec
        "psr-small:p36-s65-n6-l2-f30.pddl",  # 147 sec
        "blocks:probBLOCKS-11-0.pddl",  # 154 sec
        "mprime:prob15.pddl",  # 154 sec
        "airport:p25-airport4halfMUC-p5.pddl",  # 159 sec
        "logistics00:probLOGISTICS-8-1.pddl",  # 169 sec
        "blocks:probBLOCKS-11-1.pddl",  # 171 sec
        "blocks:probBLOCKS-10-2.pddl",  # 176 sec
        "blocks:probBLOCKS-12-0.pddl",  # 183 sec
        "mprime:prob16.pddl",  # 204 sec
        "pipesworld-notankage:p23-net3-b14-g3.pddl",  # 204 sec
        "driverlog:pfile13",  # 211 sec
        "freecell:probfreecell-3-4.pddl",  # 214 sec
        "pathways:p05.pddl",  # 240 sec
        "pipesworld-notankage:p12-net2-b10-g4.pddl",  # 243 sec
        "airport:p26-airport4halfMUC-p6.pddl",  # 248 sec
        "driverlog:pfile14",  # 250 sec
        "pipesworld-tankage:p21-net3-b12-g2-t60.pddl",  # 305 sec
        "driverlog:pfile8",  # 317 sec
        "miconic:s13-1.pddl",  # 321 sec
        "zenotravel:pfile12",  # 346 sec
        "mprime:prob05.pddl",  # 353 sec
        "pipesworld-notankage:p15-net2-b14-g4.pddl",  # 370 sec
        "logistics00:probLOGISTICS-7-1.pddl",  # 388 sec
        "freecell:pfile4",  # 397 sec
        "airport:p27-airport4halfMUC-p6.pddl",  # 408 sec
        "mprime:prob19.pddl",  # 437 sec
        "blocks:probBLOCKS-10-0.pddl",  # 449 sec
        "depot:pfile4",  # 461 sec
        "freecell:pfile5",  # 515 sec
        "pipesworld-notankage:p10-net1-b14-g8.pddl",  # 524 sec
        "blocks:probBLOCKS-14-0.pddl",  # 537 sec
        "logistics98:prob33.pddl",  # 679 sec
        "airport:p28-airport4halfMUC-p7.pddl",  # 787 sec
        "gripper:prob06.pddl",  # 809 sec
        "airport:p18-airport3-p6.pddl",  # 936 sec
        "pipesworld-tankage:p11-net2-b10-g2-t30.pddl",  # 959 sec
        "blocks:probBLOCKS-14-1.pddl",  # 1050 sec
        "pipesworld-notankage:p41-net5-b22-g2.pddl",  # 1095 sec
        "logistics00:probLOGISTICS-10-1.pddl",  # 1128 sec
        "mystery:prob10.pddl",  # 1141 sec
        "logistics00:probLOGISTICS-12-0.pddl",  # 1179 sec
        "airport:p29-airport4halfMUC-p8.pddl",  # 1202 sec
        "pipesworld-tankage:p08-net1-b12-g7-t80.pddl",  # 1212 sec
        "logistics00:probLOGISTICS-10-0.pddl",  # 1326 sec
        "freecell:probfreecell-3-2.pddl",  # 1357 sec
        "mystery:prob06.pddl",  # 1493 sec
        "logistics00:probLOGISTICS-11-0.pddl",  # 1670 sec
        "airport:p30-airport4halfMUC-p8.pddl",  # 1761 sec
        ]


def suite_mas_paper_domains():
    # The domains used in the ICAPS 2007 paper on merge-and-shrink.
    return ["logistics00", "pipesworld-notankage", "pipesworld-tankage",
            "psr-small", "satellite", "tpp"]

def suite_mas_paper_solved():
    # Subset of suite_mas_paper_domains() that only contains the
    # problems that were reported in the paper and solved by the
    # merge-and-shrink abstraction approach. (This excludes TPP-08,
    # which was solved by MIPS but not merge-and-shrink, and it also
    # excludes many small Logistics and PSR problems that were not
    # reported for space reasons.)
    
    return [
        "logistics00:probLOGISTICS-4-0.pddl",
        "logistics00:probLOGISTICS-4-1.pddl",
        "logistics00:probLOGISTICS-5-0.pddl",
        "logistics00:probLOGISTICS-5-1.pddl",
        "logistics00:probLOGISTICS-6-0.pddl",
        "logistics00:probLOGISTICS-6-1.pddl",
        "logistics00:probLOGISTICS-7-0.pddl",
        "logistics00:probLOGISTICS-7-1.pddl",
        "logistics00:probLOGISTICS-8-0.pddl",
        "logistics00:probLOGISTICS-8-1.pddl",
        "logistics00:probLOGISTICS-9-0.pddl",
        "logistics00:probLOGISTICS-9-1.pddl",
        "logistics00:probLOGISTICS-10-0.pddl",
        "logistics00:probLOGISTICS-10-1.pddl",
        "logistics00:probLOGISTICS-11-0.pddl",
        "logistics00:probLOGISTICS-11-1.pddl",
        "logistics00:probLOGISTICS-12-0.pddl",
        "logistics00:probLOGISTICS-12-1.pddl",
        "pipesworld-notankage:p01-net1-b6-g2.pddl",
        "pipesworld-notankage:p02-net1-b6-g4.pddl",
        "pipesworld-notankage:p03-net1-b8-g3.pddl",
        "pipesworld-notankage:p04-net1-b8-g5.pddl",
        "pipesworld-notankage:p05-net1-b10-g4.pddl",
        "pipesworld-notankage:p06-net1-b10-g6.pddl",
        "pipesworld-notankage:p07-net1-b12-g5.pddl",
        "pipesworld-notankage:p08-net1-b12-g7.pddl",
        "pipesworld-notankage:p09-net1-b14-g6.pddl",
        "pipesworld-notankage:p10-net1-b14-g8.pddl",
        "pipesworld-notankage:p11-net2-b10-g2.pddl",
        "pipesworld-notankage:p12-net2-b10-g4.pddl",
        "pipesworld-notankage:p13-net2-b12-g3.pddl",
        "pipesworld-notankage:p14-net2-b12-g5.pddl",
        "pipesworld-notankage:p15-net2-b14-g4.pddl",
        "pipesworld-notankage:p17-net2-b16-g5.pddl",
        "pipesworld-notankage:p21-net3-b12-g2.pddl",
        "pipesworld-notankage:p23-net3-b14-g3.pddl",
        "pipesworld-notankage:p24-net3-b14-g5.pddl",
        "pipesworld-tankage:p01-net1-b6-g2-t50.pddl",
        "pipesworld-tankage:p02-net1-b6-g4-t50.pddl",
        "pipesworld-tankage:p03-net1-b8-g3-t80.pddl",
        "pipesworld-tankage:p04-net1-b8-g5-t80.pddl",
        "pipesworld-tankage:p05-net1-b10-g4-t50.pddl",
        "pipesworld-tankage:p06-net1-b10-g6-t50.pddl",
        "pipesworld-tankage:p07-net1-b12-g5-t80.pddl",
        "pipesworld-tankage:p08-net1-b12-g7-t80.pddl",
        "pipesworld-tankage:p11-net2-b10-g2-t30.pddl",
        "pipesworld-tankage:p13-net2-b12-g3-t70.pddl",
        "pipesworld-tankage:p15-net2-b14-g4-t30.pddl",
        "pipesworld-tankage:p21-net3-b12-g2-t60.pddl",
        "pipesworld-tankage:p31-net4-b14-g3-t20.pddl",
        "psr-small:p29-s45-n3-l5-f30.pddl",
        "psr-small:p36-s65-n6-l2-f30.pddl",
        "psr-small:p40-s80-n3-l4-f10.pddl",
        "psr-small:p48-s101-n5-l3-f30.pddl",
        "psr-small:p49-s105-n6-l2-f30.pddl",
        "satellite:p01-pfile1.pddl",
        "satellite:p02-pfile2.pddl",
        "satellite:p03-pfile3.pddl",
        "satellite:p04-pfile4.pddl",
        "satellite:p05-pfile5.pddl",
        "satellite:p06-pfile6.pddl",
        "tpp:p01.pddl",
        "tpp:p02.pddl",
        "tpp:p03.pddl",
        "tpp:p04.pddl",
        "tpp:p05.pddl",
        "tpp:p06.pddl",
        "tpp:p07.pddl",
        ]

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
