from os.path import abspath, dirname, join

ROOT_DIR = dirname(dirname(abspath(__file__)))

BENCHMARKS_DIR = join(ROOT_DIR, "benchmarks")
DOWNWARD_DIR = join(ROOT_DIR, "downward")
RESULTS_DIR = join(ROOT_DIR, "results")



