from os.path import abspath, dirname, join

ROOT_DIR = dirname(dirname(abspath(__file__)))

BENCHMARKS_DIR = join(ROOT_DIR, "benchmarks")
SRC_DIR = join(ROOT_DIR, "src")
RESULTS_DIR = join(ROOT_DIR, "results")
VALIDATOR_DIR = join(ROOT_DIR, "src")
