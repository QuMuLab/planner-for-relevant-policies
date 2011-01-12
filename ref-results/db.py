# -*- coding: utf-8 -*-

import hashlib
import os.path
import subprocess
import sys

import util


class Result(object):
    def __init__(self, domain_text, problem_text,
                 plan_text, plan_comment, plan_quality):
        self.hash_id = self._calculate_hash_id(domain_text, problem_text)
        self.domain_text = domain_text
        self.problem_text = problem_text
        self.plan_text = plan_text
        self.plan_comment = plan_comment
        self.plan_quality = plan_quality

    def _calculate_hash_id(self, domain_text, problem_text):
        # We add the length strings to the hash at the start so that
        # different (domain, problem) pairs that concatenate to the same
        # text can be distinguished. This is a bit paranoid, but better
        # safe than sorry.
        sha1 = hashlib.sha1()
        sha1.update("%d %d " % (len(domain_text), len(problem_text)))
        sha1.update(domain_text)
        sha1.update(problem_text)
        return sha1.hexdigest()

    def update_db(self):
        ## TODO: Perform some kind of locking. Use a context manager.
        ## => http://packages.python.org/lockfile/lockfile.html
        db = get_db()
        previous_best = db.lookup(self.hash_id, "plan.quality")
        print "previous best quality: %s" % previous_best
        if previous_best is None:
            print "insert new entry with quality: %d" % self.plan_quality
            db.insert(self.hash_id, {
                "domain.pddl": self.domain_text,
                "problem.pddl": self.problem_text,
                "plan.soln": self.plan_text,
                "plan.quality": "%d\n" % self.plan_quality,
                "plan.comment": self.plan_comment + "\n",
                })
        else:
            previous_best = int(previous_best)
            if self.plan_quality < previous_best:
                print "new best quality: %d" % self.plan_quality
                db.update(self.hash_id, {
                    "plan.soln": self.plan_text,
                    "plan.quality": "%d\n" % self.plan_quality,
                    "plan.comment": self.plan_comment + "\n",
                    })
            else:
                print "no improvement"


class Database(object):
    def __init__(self, db_dir):
        self.db_dir = db_dir
        if not os.path.exists(self.db_dir):
            print "no ref-result database found -- creating a new one"
            self._hg(["init", "db"], pass_repository=False)

    def lookup(self, key, attribute):
        attrfile = self._attr_file(key, attribute)
        if os.path.exists(attrfile):
            return util.read_file(attrfile)
        else:
            return None

    def insert(self, key, attrdict):
        util.make_dir(self._key_dir(key))
        self._write_attributes(key, attrdict)
        self._hg(["commit", "-m", "Added entry %s." % key])

    def update(self, key, update_dict):
        self._write_attributes(key, update_dict)
        self._hg(["commit", "-m", "Updated entry %s." % key])

    def _key_dir(self, key):
        return os.path.join(self.db_dir, "key-%s" % key)

    def _attr_file(self, key, attribute):
        return os.path.join(self._key_dir(key), attribute)

    def _write_attributes(self, key, attrdict):
        for attr, new_value in sorted(attrdict.items()):
            attrfile = self._attr_file(key, attr)
            is_new_attribute = not os.path.exists(attrfile)
            util.write_file(attrfile, new_value)
            if is_new_attribute:
                self._hg(["add", attrfile])

    def _hg(self, args, pass_repository=True):
        cmd = ["hg"]
        if pass_repository:
            cmd.extend(["--repository", self.db_dir])
        cmd.extend(args)
        subprocess.check_call(cmd)


_the_db = None

def get_db():
    global _the_db
    if _the_db is None:
        src_dir = os.path.dirname(os.path.abspath(__file__))
        db_dir = os.path.join(src_dir, "db")
        _the_db = Database(db_dir)
    return _the_db
