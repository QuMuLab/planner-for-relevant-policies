#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

import argparse
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
    try:
        quality = validator.validate(args.domain, args.problem, args.plan)
        print "Plan quality:", quality
    except validator.Error, e:
        print e

if __name__ == "__main__":
    main()
