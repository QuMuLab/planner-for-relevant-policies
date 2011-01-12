#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

import argparse

import db
import util
import validator


def parse_args():
    parser = argparse.ArgumentParser(
        description="PDDL benchmark reference results tool")
    parser.add_argument("domain", type=str, help="domain file name")
    parser.add_argument("problem", type=str, help="problem file name")
    parser.add_argument("plan", type=str, help="plan file name")
    return parser.parse_args()


def main():
    args = parse_args()

    # We read all these upfront to avoid race conditions where VAL
    # sees a different domain/problem/plan than what we compute the
    # hash ID for.
    domain_text = util.read_file(args.domain)
    problem_text = util.read_file(args.problem)
    plan_text = util.read_file(args.plan)

    try:
        quality = validator.validate(domain_text, problem_text, plan_text)
    except validator.Error as e:
        print e
    else:
        result = db.Result(
            domain_text=domain_text,
            problem_text=problem_text,
            plan_text=plan_text,
            plan_comment="<no comment for this plan>",
            plan_quality=quality)
        result.update_db()


if __name__ == "__main__":
    ## TODO: We should be able to set the plan_comment
    ##       (e.g. to the planner revision and option string).
    main()
