# -*- coding: utf-8 -*-

import re
import subprocess


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


def validate(domain, problem, plan):
    """Validate the plan for the given domain and problem and return
    its quality. Raise validator.Error if validation failed. Other
    kinds of error such as OSError can be raised if there are external
    problems (e.g. if the validator is not found)."""

    validator = subprocess.Popen(
        ["validate", domain, problem, plan],
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
        plan_name != plan):
        fail("Validator output looks unexpected", "stdout", stdout)
    return int(quality)
