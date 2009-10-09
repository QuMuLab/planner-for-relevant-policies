from collections import defaultdict

import actions
import latex
import sys

TIMEOUT = 1800  # Problems with a larger search time don't count as solved.

CONFIGURATIONS = [
    "ou",  # LM-Cut with A*
#    "yY", # cyclic causal graph heuristic with preferred operators
#    "cC", # old causal graph heuristic with preferred operators
#    "aA", # additive heuristic with preferred operators
#    "fF", # FF heuristic with preferred operators
#    "y",  # cyclic causal graph heuristic
#    "c",  # old causal graph heuristic
#    "a",  # additive heuristic
#    "f",  # FF heuristic
    ]

PAIRS = [
    ("yY", "cC"),
    ("yY", "aA"),
    ("yY", "fF"),
    ]


def do_report(report, suite):
    report_func = globals().get("report_%s" % report)
    ReportClass = globals().get("Report%s" % report.title().replace("_", ""))
    if not report_func and not ReportClass:
        raise SystemExit("unknown report: %s" % report)
    results = collect_results(suite)
    add_virtual_results(results)
    if report_func:
        report_func(suite, results)
    else:
        ReportClass(suite, results).report()


def warn(msg):
    print >> sys.stderr, msg


def collect_results(suite):
    results = []
    for problem in suite:
        for config in CONFIGURATIONS:
            result = actions.parse_result(problem, config, cutoff_time=TIMEOUT)
            if not result.present:
                warn("not present: %s [%s]" % (problem, config))
                continue
            if result.solved and not result.complete:
                warn("strange: %s [%s]" % (problem, config))
            if result.complete and not result.solved:
                # warn("unsolvable?: %s [%s]" % (problem, config))
                ## TODO: This is commented out for now. In the future,
                ## should check against a whitelist of known unsolvable
                ## problems and warn on all others.
                pass
            assert problem, config not in results
            results.append(result)
    return results

def add_virtual_results(results):
    problems = set(result.problem for result in results)
    result_dict = dict(((result.problem, result.arguments), result)
                       for result in results)
    for config in CONFIGURATIONS:
        if config.startswith("V"):
            for problem in problems:
                subresults = [result_dict[problem, subconfig]
                              for subconfig in config[1:]]
                results.append(make_virtual_result(config, problem, subresults))


def make_virtual_result(config, problem, subresults):
    data = dict(problem=problem,
                arguments=config,
                solved=False,
                present=True,
                complete=False,
                status="NOT OK")
    count = len(subresults)
    for subres in subresults:
        if subres.solved and subres.status == "OK":
            time = subres.total_time * count
            if time <= data.get("total_time", TIMEOUT):
                data["solved"] = True
                data["complete"] = True
                data["status"] = "OK"
                data["total_time"] = time
                data["search_time"] = time ## Well...
                data["expanded"] = subres.expanded ## Well...
                data["generated"] = subres.generated ## Well...
                data["length"] = subres.length ## Well...
    return actions.Result(**data)
    

def tabulate(sequence, key):
    result = defaultdict(list)
    for element in sequence:
        result[key(element)].append(element)
    return result

def map_values(mapping, func):
    for key, value in mapping.iteritems():
        mapping[key] = func(value)


class Report(object):
    def __init__(self, suite, results, configs=None):
        self.configs = configs or CONFIGURATIONS
        config_set = set(self.configs)
        results = [r for r in results if r.arguments in config_set]
        self.suite = suite
        self.results = results

    def show_totals(self):
        return False

    def get_data(self):
        raise NotImplementedError

    def get_title(self):
        if self.title is not None:
            return self.title
        else:
            return self.__class__.__name__

    def get_row_info(self):
        return None

    def get_rows(self):
        return []  # Deduce rows automatically.

    def get_columns(self):
        return []  # Deduce columns automatically.

    def block_starters(self):
        return []

    def get_latex_table(self):
        return latex.Table(data=self.get_data(),
                           title=self.get_title(),
                           row_info=self.get_row_info(),
                           totals=self.show_totals(),
                           rows=self.get_rows(),
                           columns=self.get_columns(),
                           hline_before=self.block_starters())

    def report(self):
        table = self.get_latex_table()
        latex.Document([table]).dump()



class ReportDetails(Report):
    title = "Instance"
    keys = ["init_h", "length", "expanded", "generated", "search_time"]

    def get_rows(self):
        for result in self.results:
            yield str(result.problem)

    def get_columns(self):
        for key in self.keys:
            yield key.replace("_", " ")
    
    def get_data(self):
        assert len(self.configs) == 1
        data = {}
        for result in self.results:
            row = str(result.problem)
            for key in self.keys:
                column = key.replace("_", " ")
                data[row, column] = getattr(result, key, None)
        return data

    def block_starters(self):
        prev_domain = None
        for result in self.results:
            if result.problem.domain != prev_domain:
                yield str(result.problem)
                prev_domain = result.problem.domain


class DomainVsConfigReport(Report):
    def get_data(self):
        def domain_and_config(result):
            return result.problem.domain, result.arguments
        data = tabulate(self.results, key=domain_and_config)
        map_values(data, self.cell_entry)
        return data

    def get_row_info(self):
        counts = tabulate(self.suite, key=lambda problem: problem.domain)
        map_values(counts, len)
        counts["total"] = sum(counts.itervalues())
        return counts

    def cell_entry(self, results):
        raise NotImplementedError


class DomainVsConfigCountReport(DomainVsConfigReport):
    def cell_entry(self, results):
        return sum(1 for r in results if self.is_counted(r))

    def show_totals(self):
        return True

    def is_counted(self, result):
        raise NotImplementedError


class ReportSolved(DomainVsConfigCountReport):
    def get_title(self):
        return "Solved problems"
    
    def is_counted(self, result):
        return result.solved


class ReportUnsolved(DomainVsConfigCountReport):
    def get_title(self):
        return "Unsolved problems"

    def is_counted(self, result):
        return not result.solved


class ReportLongTime(DomainVsConfigCountReport):
    def get_title(self):
        return "Solved in >= 10 mins"

    def is_counted(self, result):
        # NOTE: This does not count problems that are solved after
        #       the timeout, because these don't count as "solved".
        return result.solved and result.total_time >= 600


def compare_config_pair(suite, results, config1, config2, comparator):
    def aggregate(entries):
        sums = [0, 0, 0]
        good, neutral, bad = 0, 0, 0
        for problem, res1, res2 in entries:
            outcome = comparator(res1, res2)
            if outcome is not None:
                sums[outcome + 1] += 1
        return "%d - %d - %d" % tuple(sums)
    data = comparative_results(suite, results, config1, config2)
    table_data = tabulate(data, key=lambda x: x[0].domain)
    map_values(table_data, func=aggregate)
    return table_data

def compare_config_pairs(suite, results, pairs, comparator, title):
    table_data = defaultdict(lambda: "missing")
    for config1, config2 in pairs:
        pairing = r"%s vs.\ %s" % (config1, config2)
        pair_data = compare_config_pair(suite, results, config1, config2,
                                        comparator)
        for domain, comparison in pair_data.iteritems():
            table_data[domain, pairing] = comparison
    table = latex.Table(title=title, data=table_data)
    latex.Document([table]).dump()

def report_compare_expansions(suite, results):
    def comparator(r1, r2):
        if r1.solved and r2.solved:
            return cmp(r1.expanded, r2.expanded)
        else:
            return None
    compare_config_pairs(suite, results, PAIRS, comparator,
                         "Comparison: expansions")

def report_compare_plan_length(suite, results):
    def comparator(r1, r2):
        if r1.solved and r2.solved:
            return cmp(r1.length, r2.length)
        else:
            return None
    compare_config_pairs(suite, results, PAIRS, comparator,
                         "Comparison: plan length")

def report_compare_search_time(suite, results):
    def comparator(r1, r2):
        if r1.solved and r2.solved:
            return cmp(round(r1.search_time), round(r2.search_time))
        else:
            return None
    compare_config_pairs(suite, results, PAIRS, comparator,
                         "Comparison: search time")

def comparative_results(suite, results, config1, config2):
    def problem_and_config(result):
        return result.problem, result.arguments
    by_problem_and_config = tabulate(results, problem_and_config)
    data = []
    for problem in suite:
        import sys
        result1, = by_problem_and_config[problem, config1]
        result2, = by_problem_and_config[problem, config2]
        data.append((problem, result1, result2))
    return data

def expansions_compare(suite, results, config1, config2):
    data = comparative_results(suite, results, config1, config2)
    for problem, res1, res2 in data:
        if res1.solved and res2.solved:
            print problem, res1.expanded, res2.expanded

def domain_pairing_summary(suite, results, config1, config2, aggregator):
    def normalize(domain):
        return {"logistics98": "logistics",
                "logistics00": "logistics"}.get(domain, domain)

    data = comparative_results(suite, results, config1, config2)
    data = [(p.domain, r1, r2)
            for p, r1, r2 in data
            if r1.solved and r2.solved]
    data = tabulate(data, lambda (domain, r1, r2): normalize(domain))
    map_values(data, aggregator)
    return data

def domain_pairing_summaries(suite, results, pairings, aggregator, title):
    table_data = defaultdict(lambda: "missing")
    for config1, config2 in PAIRS:
        pairing = r"%s vs.\ %s" % (config1, config2)
        pair_data = domain_pairing_summary(
            suite, results, config1, config2, aggregator)
        for domain, entry in pair_data.iteritems():
            table_data[domain, pairing] = str(entry)
    table = latex.Table(title=title, data=table_data)
    latex.Document([table]).dump()
                             
def report_total_expansion_improvements(suite, results):
    def aggregator(entries):
        sum1 = sum(entry[1].expanded for entry in entries)
        sum2 = sum(entry[2].expanded for entry in entries)
        return "%.2f" % (float(sum2) / sum1)
    domain_pairing_summaries(suite, results, PAIRS, aggregator,
                             "Total expansion improvements")

def report_median_expansion_improvements(suite, results):
    def aggregator(entries):
        fractions = [float(r2.expanded) / r1.expanded
                     for _, r1, r2 in entries]
        fractions.sort()
        middle1 = (len(fractions) - 1) // 2
        middle2 = len(fractions) // 2
        # This is a "geometric" median, since this makes more sense.
        median = (fractions[middle1] * fractions[middle2]) ** 0.5
        return "%.3f" % median
    domain_pairing_summaries(suite, results, PAIRS, aggregator,
                             "Expansion improvement medians")

def report_mean_expansion_improvements(suite, results):
    def aggregator(entries):
        fractions = [float(r2.expanded) / r1.expanded
                     for _, r1, r2 in entries]
        product = 1
        for frac in fractions:
            product *= frac
        geom_mean = product ** (1.0 / len(fractions))
        return "%.3f" % geom_mean
    domain_pairing_summaries(suite, results, PAIRS, aggregator,
                             "Expansion improvement means")

def report_percent_expansion_improvements(suite, results):
    def aggregator(entries):
        count = 0.0
        for _, r1, r2 in entries:
            if r1.expanded < r2.expanded:
                count += 1.0
            elif r1.expanded == r2.expanded:
                count += 0.5
        return r"%.0f\%%" % (100.0 * count / len(entries))
    domain_pairing_summaries(suite, results, PAIRS, aggregator,
                             "Expansion improvement percentages")


def report_solved_vs_time(suite, results):
    EPSILON = 0.01
    by_config = tabulate(results, lambda r: r.arguments)
    for config, results in by_config.iteritems():
        outfile = open("solved-vs-time-%s.data" % config, "w")
        times = sorted(r.search_time for r in results if r.solved)
        last_time = 0.0
        for index, time in enumerate(times):
            if time > last_time:
                # Until epsilon before "time", fewer problems were solved.
                print >> outfile, index, time - EPSILON
                last_time = time
            print >> outfile, index + 1, time
        if len(times) != len(results):
            # If any problem was unsolved, plot up to max_time.
            print >> outfile, len(times), TIMEOUT
        outfile.close()


def report_expansions_cC_yY(suite, results):
    return expansions_compare(suite, results, "cC", "yY")

def report_expansions_aA_yY(suite, results):
    return expansions_compare(suite, results, "aA", "yY")

def report_expansions_fF_yY(suite, results):
    return expansions_compare(suite, results, "fF", "yY")

def get_status(result):
    if result.status == "OK":
        return "OK  %6ds" % result.search_time
    else:
        return result.status

def report_list_unsolved(suite, results):
    for r in results:
        if not r.solved:
            print "%10s [%2s] %s" % (get_status(r), r.arguments, r.problem)

def report_status(suite, results):
    for r in results:
        print "%10s [%2s] %s" % (get_status(r), r.arguments, r.problem)
