# -*- coding: utf-8 -*-

import os.path
import re
import shutil
import subprocess
import tempfile


class Error(Exception):
    pass


expected_output = re.compile(r"""^Checking plan: (.*)
Plan executed successfully - checking goal
Plan valid
Final value: (\d+)

Successful plans:
Value: (\d+)
 (.*)$""")


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
        with open(filepath, "w") as file:
            file.write(contents)
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
        ["validate", domain_file, problem_file, plan_file],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = validator.communicate()
    retcode = validator.returncode
    stdout = stdout.strip()
    stderr = stderr.strip()

    if stderr:
        fail("Validator wrote to stderr", "stderr", stderr)
    if retcode:
        fail("Validator returned %d" % retcode, "stdout", stdout)
    match = expected_output.match(stdout)
    if not match:
        fail("Validator output did not match regexp", "stdout", stdout)
    plan_name, quality, quality_copy, plan_name_copy = match.groups()
    if (plan_name != plan_name_copy or quality != quality_copy or
        plan_name != plan_file):
        fail("Validator output looks unexpected", "stdout", stdout)
    return int(quality)
