#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from operator import itemgetter
import logging

from reports import Report, ReportArgParser, existing

SCORES = ['expansions', 'evaluations', 'search_time', 'total_time']

class Options(object):
    def __init__(self):
        self.ref_value_column = False # Not implemented
        self.best_value_column = False # Not implemented
options = Options()


def get_date_and_time():
    return r"\today\ \thistime"


class IpcReport(Report):
    """
    """
    def __init__(self, parser=ReportArgParser()):
        parser.set_defaults(output_format='tex')
        parser.add_argument('focus', choices=SCORES,# metavar='FOCUS',
                    help='the analyzed attribute (e.g. "expanded"). '
                        'The "attributes" parameter is ignored')
        parser.add_argument('--normalize', action='store_true',
                            help='Add a summary table with normalized values')
        parser.add_argument('--squeeze', action='store_true',
                            help='Use small fonts to fit in more data')
        Report.__init__(self, parser)
        self.score = 'score_' + self.focus
        logging.info('Using score attribute "%s"' % self.score)
        # Get set of configs
        self.configs = sorted(self.data.group_dict('config').keys())
        self.total_scores = self._compute_total_scores()

    def name(self):
        name = ''
        eval_dir = os.path.basename(self.eval_dir)
        name += eval_dir.replace('-', '')
        name = name.replace('eval', '')
        name += '-' + self.focus
        return name

    def _tiny_if_squeeze(self):
        if self.squeeze:
            return r"\tiny"
        else:
            return ""

    def _compute_total_scores(self):
        total_scores = {}
        domain_dict = self.data.group_dict('domain')
        for domain, runs in domain_dict.items():
            config_dict = runs.group_dict('config')
            for config in self.configs:
                config_group = config_dict.get(config)
                scores = config_group[self.score]
                scores = filter(existing, scores)
                total_score = sum(scores)
                total_scores[config, domain] = total_score
        return total_scores

    def write(self):
        if self.dry:
            self.print_report()
            return

        self.output_file = os.path.join(self.report_dir, self.name() + '.tex')

        with open(self.output_file, 'w') as file:
            sys.stdout = file
            self.print_report()
            sys.stdout = sys.__stdout__

    def print_report(self):
        self.print_header()
        # Group by domain
        self.data.sort('domain', 'problem', 'config')
        domain_dict = self.data.group_dict('domain')
        for index, (domain, group) in enumerate(domain_dict.items()):
            if index:
                self.print_between_domains()
            self.print_domain(domain, group)
        self.print_summary()
        self.print_footer()

    def print_header(self):
        print r"\documentclass{article}"
        if self.squeeze:
            margin = "0.5cm"
        else:
            margin = "2.5cm"
        print r"\usepackage[a4paper,landscape,margin=%s]{geometry}" % margin
        print r"\usepackage{supertabular}"
        print r"\usepackage{scrtime}"
        print r"\begin{document}"
        if self.squeeze:
            print r"\scriptsize"
            print r"\setlength{\tabcolsep}{1pt}"
        print r"\centering"

    def _format_item(self, item):
        if item is None:
            return ""
        elif isinstance(item, float):
            return "%.2f" % item
        else:
            return str(item)

    def _format_result(self, run):
        status = run.get_single_value('status')
        if status == "ok":
            return r"{\tiny %s} \textbf{%s}" % (
                self._format_item(run.get_single_value(self.focus)),
                self._format_item(run.get_single_value(self.score)))
        else:
            SHORTHANDS = {"unsolved": "uns.", None: "---"}
            return SHORTHANDS.get(status, status)

    def print_domain(self, domain, runs):
        # Get set of problems
        problems = ['']

        print r"\section*{%s %s --- %s}" % (
            self.focus, domain, get_date_and_time())
        print r"\tablehead{\hline"
        print r"\textbf{prob}"
        for config in self.configs:
            print r"& %s\textbf{%s}" % (self._tiny_if_squeeze(), config)
        if options.ref_value_column:
            print r"& %s\textbf{REF}" % self._tiny_if_squeeze()
        if options.best_value_column:
            print r"& %s\textbf{BEST}" % self._tiny_if_squeeze()
        print r"\\ \hline}"
        print r"\tabletail{\hline}"
        column_desc = "|l|%s|" % ("r" * len(self.configs))
        if options.ref_value_column:
            column_desc += "r|"
        if options.best_value_column:
            column_desc += "r|"
        print r"\begin{supertabular}{%s}" % column_desc

        for problem, probgroup in sorted(runs.group_dict('problem').items()):
            print r"\textbf{%s}" % problem
            config_dict = probgroup.group_dict('config')
            for config in self.configs:
                run = config_dict.get(config)
                assert len(run) == 1, run
                print r"& %s" % self._format_result(run)
            if options.ref_value_column:
                ref_quality = results.reference_quality(instance)
                print r"& %s" % ("---" if ref_quality is None else ref_quality)
            if options.best_value_column:
                best_known_quality = results.best_known_quality(instance)
                print r"& %s" % ("---" if best_known_quality is None else best_known_quality)
            print r"\\"
        print r"\hline"
        print r"\textbf{total}"
        for config in self.configs:
            print r"& \textbf{%.2f}" % self.total_scores[config, domain]
        if options.ref_value_column:
            print r"&"
        if options.best_value_column:
            print r"&"
        print r"\\"
        print r"\end{supertabular}"

    def print_between_domains(self):
        print r"\clearpage"

    def print_summary(self):
        self._print_summary(False, "overall")
        if self.normalize:
            self._print_summary(True, "normalized overall")

    def _print_summary(self, normalize, title):
        print r"\clearpage"
        from collections import defaultdict
        overall = defaultdict(float)

        print r"\section*{%s %s --- %s}" % (
            self.focus, title, get_date_and_time())
        print r"\begin{tabular}{|l|%s|}" % ("r" * len(self.configs))
        print r"\hline"
        print r"\textbf{domain}"
        for config in self.configs:
            print r"& %s\textbf{%s}" % (self._tiny_if_squeeze(), config)
        print r"\\ \hline"
        domain_dict = self.data.group_dict('domain')
        for domain, group in sorted(domain_dict.items()):
            print r"\textbf{%s}" % domain
            for config in self.configs:
                score = self.total_scores[config, domain]
                if normalize:
                    num_instances = len(group.group_dict('problem'))
                    score = float(score) * 100 / num_instances
                overall[config] += score
                entry = "%.2f" % score
                print r"& %s" % entry
            print r"\\"
        print r"\hline"
        print r"\textbf{overall}"
        for config in self.configs:
            overall_score = overall[config]
            if normalize:
                num_domains = len(domain_dict)
                overall_score = float(overall_score) / num_domains
            print r"& \textbf{%.2f}" % overall_score
        print r"\\ \hline"
        print r"\end{tabular}"

    def print_footer(self):
        print r"\end{document}"


if __name__ == "__main__":
    report_type = 'ipc'
    logging.info('Report type: %s' % report_type)

    if report_type == 'ipc':
        report = IpcReport()

    # Copy the report type
    report.report_type = report_type

    report.write()
