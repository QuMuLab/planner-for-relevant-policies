import os.path

from paths import BENCHMARKS_DIR, RESULTS_DIR

class Repository(object):
    def __init__(self):
        domains = os.listdir(BENCHMARKS_DIR)
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
        problems.sort()
        self.problems = [Problem(domain, problem) for problem in problems]
    def __str__(self):
        return self.domain
    def __iter__(self):
        return iter(self.problems)

class Problem(object):
    def __init__(self, domain, problem):
        self.domain = domain
        self.problem = problem
    def __str__(self):
        return "%s-%s" % (self.domain, self.problem)
    def problem_file(self):
        return os.path.join(BENCHMARKS_DIR, self.domain, self.problem)
    def domain_file(self):
        result = os.path.join(BENCHMARKS_DIR, self.domain, "domain.pddl")
        if os.path.exists(result):
            return result
        return os.path.join(BENCHMARKS_DIR, self.domain,
                            self.problem[:4] + "domain.pddl")

class ResultFiles(object):
    def __init__(self, algorithm, problem):
        base, _ = os.path.splitext(os.path.basename(problem.problem))
        self.base_name = os.path.join(RESULTS_DIR, algorithm, problem.domain, base)
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
    def preprocess_out(self):
        return self.base_name + ".pre"
    def search_out(self):
        return self.base_name + ".out"
    def solution(self):
        return self.base_name + ".soln"
