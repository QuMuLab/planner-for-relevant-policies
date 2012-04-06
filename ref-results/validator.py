# -*- coding: utf-8 -*-

import os.path
import re
import shutil
import subprocess
import tempfile

import util


class Error(Exception):
    pass


def fail(reason, stream_name, stream_text):
    dashes = "-" * 72
    errmsg = "".join(["%s -- treating as failed.\n" % reason,
                      "%s is:\n" % stream_name,
                      dashes + "\n",
                      stream_text + "\n",
                      dashes])
    raise Error(errmsg)


def validate(domain_text, problem_text, plan_text):
    """Validate the plan for the given domain and problem and return
    its quality. Raise validator.Error if validation failed. Other
    kinds of error such as OSError can be raised if there are external
    problems (e.g. if the validator is not found)."""

    tempdir = tempfile.mkdtemp(prefix="tmp-ref-results-")
    def make_temp_file(filename, contents):
        filepath = os.path.join(tempdir, filename)
        util.write_file(filepath, contents)
        return filepath
    try:
        return validate_files(
            make_temp_file("domain.pddl", domain_text),
            make_temp_file("problem.pddl", problem_text),
            make_temp_file("plan.soln", plan_text))
    finally:
        shutil.rmtree(tempdir)


def validate_files(domain_file, problem_file, plan_file):
    validator = subprocess.Popen(
        ["validate", "-S", domain_file, problem_file, plan_file],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = validator.communicate()
    if stderr.strip():
        fail("Validator wrote to stderr", "stderr", stderr)
    if validator.returncode != 0:
        fail("Validator returned %d" % validator.returncode, "stdout", stdout)
    if not stdout.strip().isdigit():
        fail("Validator output does not look as expected", "stdout", stdout)
    return int(stdout)
