from collections import defaultdict


def escape(text):
    return str(text).replace("_", r"\_")


class Table(object):
    def __init__(self, data, title="", totals=False,
                 row_info=None, rows=(), columns=(), hline_before=()):
        self.title = title
        self.rows = list(rows) or sorted(set(row for (row, col) in data))
        self.columns = list(columns) or sorted(set(col for (row, col) in data))
        self.data = data
        self.totals = totals
        self.row_info = row_info or {}
        self.hline_before = set(hline_before)
        if totals:
            self.add_totals()

    def add_totals(self):
        col_totals = defaultdict(self.guess_cell_type())
        for (row, col), item in self.data.iteritems():
            col_totals[col] += item
        self.rows.append("total")
        for col in self.columns:
            self.data["total", col] = col_totals[col]

    def guess_cell_type(self):
        types = set(type(cell) for cell in self.data.itervalues())
        if float in types:
            return float
        else:
            return int

    def format_title(self, title):
        return r"\textbf{%s}" % escape(title)

    def format_column_title(self, column):
        column = column.replace("_", "").replace("-", "")
        return r"\textbf{%s}" % escape(column)

    def format_row_title(self, row):
        if row in self.row_info:
            info = " (%s)" % escape(self.row_info[row])
        else:
            info = ""
        return r"\textbf{%s}%s" % (escape(row), info)

    def format_cell(self, row, column, entry):
        return escape(entry)

    def want_hline_before(self, row):
        return row in self.hline_before

    def dump(self):
        print r"\tablehead{"
        print r"\hline"
        print self.format_title(self.title)
        for column in self.columns:
            print r"& %s" % self.format_column_title(column)
        print r"\\ \hline \hline"
        print r"}"
        print r"\tabletail{"
        print r"\hline"
        print r"}"
        print r"\begin{supertabular}{|l||%s}" % ("c|" * len(self.columns))
        for row in self.rows:
            if (self.totals and row is self.rows[-1]) or (
                self.want_hline_before(row)):
                print r"\hline"
            print self.format_row_title(row)
            for column in self.columns:
                entry = self.data.get((row, column))
                print r"& %s" % self.format_cell(row, column, entry)
            print r"\\"
        print r"\end{supertabular}"

class Document(object):
    def __init__(self, parts, landscape=False):
        self.parts = parts
        self.landscape = landscape

    def dump(self):
        print r"\documentclass[a4paper]{article}"
        if self.landscape:
            print r"\usepackage[landscape,margin=1cm]{geometry}"
        else:
            print r"\usepackage[margin=1cm]{geometry}"
        print r"\usepackage{supertabular}"
        print r"\begin{document}"
        for no, part in enumerate(self.parts):
            if no:
                print r"\clearpage"
            part.dump()
        print r"\end{document}"
