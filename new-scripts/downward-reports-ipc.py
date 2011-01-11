#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from operator import itemgetter
import logging

from reports import Report, ReportArgParser, existing

SCORES = ['expansions', 'evaluations', 'search_time', 'total_time',
            'coverage',
            #'quality'
        ]

def get_date_and_time():
    return r"\today\ \thistime"

def escape(text):
    return text.replace('_', r'\_')


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
        parser.add_argument('--no-best', action='store_false',
                            dest='best_value_column',
                            help='Do not add a column with the best known score')
        parser.add_argument('--page-size', choices=['a2', 'a3', 'a4'],
                            default='a4',
                            help='Set the page size for the latex report')
        Report.__init__(self, parser)
        self.output_file = os.path.join(self.report_dir, self.name() + '.tex')
        self.focus_name = self.focus

        self.score = 'score_' + self.focus
        if self.focus == 'coverage':
            self.focus = 'plan_length'
            self.score = 'coverage'
        elif self.focus == 'quality':
            self.focus = 'plan_length'
            self.score = 'quality'

        logging.info('Using score attribute "%s"' % self.score)
        logging.info('Adding column with best value: %s' % self.best_value_column)
        # Get set of configs
        self.configs = sorted(self.data.group_dict('config').keys())
        self.total_scores = self._compute_total_scores()

    def name(self):
        name = os.path.basename(self.eval_dir)
        name += '-ipc-' + self.focus
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
                assert config_group, 'Config %s was not found in dict %s' % (
                        config, config_dict)
                scores = config_group[self.score]
                scores = filter(existing, scores)
                total_score = sum(scores)
                total_scores[config, domain] = total_score
        return total_scores

    def write(self):
        if self.dry:
            self.print_report()
            return

        with open(self.output_file, 'w') as file:
            sys.stdout = file
            self.print_report()
            sys.stdout = sys.__stdout__
        logging.info('Wrote file %s' % self.output_file)

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
        print r"\usepackage[%spaper,landscape,margin=%s]{geometry}" % \
                (self.page_size, margin)
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
        print r"\section*{%s %s --- %s}" % (
            escape(self.focus_name), escape(domain), get_date_and_time())
        print r"\tablehead{\hline"
        print r"\textbf{prob}"
        for config in self.configs:
            print r"& %s\textbf{%s}" % (self._tiny_if_squeeze(), escape(config))
        if self.best_value_column:
            print r"& %s\textbf{BEST}" % self._tiny_if_squeeze()
        print r"\\ \hline}"
        print r"\tabletail{\hline}"
        column_desc = "|l|%s|" % ("r" * len(self.configs))
        if self.best_value_column:
            column_desc += "r|"
        print r"\begin{supertabular}{%s}" % column_desc

        for problem, probgroup in sorted(runs.group_dict('problem').items()):
            print r"\textbf{%s}" % problem.replace('.pddl', '')
            scores = []
            # Compute best value if we are comparing quality
            if self.score == 'quality':
                # self.focus is "plan_length"
                lengths = probgroup.get(self.focus)
                lengths = filter(existing, lengths)
                best_length = max(lengths) if lengths else None
            config_dict = probgroup.group_dict('config')
            for config in self.configs:
                run = config_dict.get(config)
                assert len(run) == 1, run
                if self.score == 'quality':
                    length = run.get_single_value('plan_length')
                    quality = None
                    if length and best_length and not length == 0:
                        quality = float(best_length) / length
                    run['quality'] = quality
                    scores.append(quality)
                print r"& %s" % self._format_result(run)
            if self.best_value_column:
                if self.score == 'quality':
                    best = max(scores) if scores else None
                else:
                    values = probgroup.get(self.focus)
                    values = filter(existing, values)
                    best = min(values) if values else None
                print r"& %s" % ("---" if best is None else best)
            print r"\\"
        print r"\hline"
        print r"\textbf{total}"
        for config in self.configs:
            print r"& \textbf{%.2f}" % self.total_scores[config, domain]
        if self.best_value_column:
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
            escape(self.focus_name), escape(title), get_date_and_time())
        print r"\tablehead{\hline"
        print r"\textbf{domain}"
        for config in self.configs:
            print r"& %s\textbf{%s}" % (self._tiny_if_squeeze(), escape(config))
        print r"\\ \hline}"
        print r"\tabletail{\hline}"
        print r"\begin{supertabular}{|l|%s|}" % ("r" * len(self.configs))
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
        print r"\end{supertabular}"

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
    report.open()
