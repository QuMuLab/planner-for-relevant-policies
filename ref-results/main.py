#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

import argparse
import os.path

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

    domain_filename = os.path.basename(args.domain)
    problem_filename = os.path.basename(args.problem)

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
        ## TODO: In most cases, the basenames are not actually very
        ##       interesting. What to do about that? Store the full
        ##       text?
        domain_name = os.path.basename(args.domain)
        problem_name = os.path.basename(args.problem)
        print "domain:", domain_name
        print "problem:", problem_name
        print "plan quality:", quality
        db.update_reference_quality(
            domain_name, domain_text, problem_name, problem_text, quality)


if __name__ == "__main__":
    main()
