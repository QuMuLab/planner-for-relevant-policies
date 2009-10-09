import os.path

from paths import BENCHMARKS_DIR, RESULTS_DIR
import tools

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
