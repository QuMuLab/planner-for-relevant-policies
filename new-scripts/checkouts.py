import os
import sys
import subprocess
import logging
import re
import itertools

import tools

CHECKOUTS_DIR = os.path.join(tools.SCRIPTS_DIR, 'checkouts')
tools.makedirs(CHECKOUTS_DIR)

ABS_REV_CACHE = {}
_sentinel = object()


class Checkout(object):
    def __init__(self, part, repo, rev, checkout_dir, name):
        # Directory name of the planner part (translate, preprocess, search)
        self.part = part
        self.repo = repo
        self.rev = str(rev)
        # Nickname for the checkout (used for reports and checkout directory)
        self.name = name

        if not os.path.isabs(checkout_dir):
            checkout_dir = os.path.join(CHECKOUTS_DIR, checkout_dir)
        self.checkout_dir = os.path.abspath(checkout_dir)

        self._executable = None

    def __eq__(self, other):
        return self.rev == other.rev

    def __hash__(self):
        return hash(self.checkout_dir)

    def checkout(self):
        # We don't need to check out the working copy
        if not self.rev == 'WORK':
            # If there's already a checkout, don't checkout again
            path = self.checkout_dir
            if os.path.exists(path):
                logging.debug('Checkout "%s" already exists' % path)
            else:
                cmd = self.get_checkout_cmd()
                print cmd
                subprocess.call(cmd, shell=True)
            assert os.path.exists(path), 'Could not checkout to "%s"' % path

    def get_checkout_cmd(self):
        raise Exception('Not implemented')

    def compile(self):
        """
        We need to compile the code if the executable does not exist.
        Additionally we want to compile it, when we run an experiment with
        the working copy to make sure the executable is based on the latest
        version of the code.
        """
        cwd = os.getcwd()
        src_dir = os.path.dirname(self.exe_dir)
        os.chdir(src_dir)
        subprocess.call(['./build_all'])
        os.chdir(cwd)

    def _get_executable(self, default=_sentinel):
        """ Returns the path to the python module or a binary """
        names = ['translate.py', 'preprocess',
                'downward', 'release-search', 'search',
                'downward-debug', 'downward-profile']
        for name in names:
            planner = os.path.join(self.exe_dir, name)
            if os.path.exists(planner):
                return planner
        if default is _sentinel:
            logging.error('%s executable could not be found in %s' %
                            (self.part, self.exe_dir))
            sys.exit(1)
        return default

    @property
    def binary(self):
        if not self._executable:
            self._executable = self._get_executable()
        return self._executable

    @property
    def parent_rev(self):
        raise Exception('Not implemented')

    @property
    def exe_dir(self):
        raise Exception('Not implemented')

    @property
    def rel_dest(self):
        return 'code-%s/%s' % (self.rev, self.part)

    @property
    def shell_name(self):
        return '%s_%s' % (self.part.upper(), self.rev)

    @property
    def src_dir(self):
        return os.path.join(self.checkout_dir, 'src')


# ---------- Mercurial --------------------------------------------------------

class HgCheckout(Checkout):
    DEFAULT_URL = tools.BASE_DIR
    DEFAULT_REV = 'WORK'

    def __init__(self, part, repo=DEFAULT_URL, rev=DEFAULT_REV, name=''):
        rev_nick = str(rev).upper()
        # Find proper absolute revision
        rev_abs = self.get_rev_abs(repo, rev)

        if rev_nick == 'WORK':
            checkout_dir = tools.BASE_DIR
        else:
            checkout_dir = name if name else rev_abs

        if not name:
            name = part + '-' + rev_nick

        Checkout.__init__(self, part, repo, rev_abs, checkout_dir, name)
        self.parent = None

    def get_rev_abs(self, repo, rev):
        if str(rev).upper() == 'WORK':
            return 'WORK'
        cmd = 'hg id -ir %s %s' % (str(rev).lower(), repo)
        if cmd in ABS_REV_CACHE:
            return ABS_REV_CACHE[cmd]
        abs_rev = tools.run_command(cmd)
        if not abs_rev:
            logging.error('Revision %s not present in repo %s' % (rev, repo))
            sys.exit(1)
        ABS_REV_CACHE[cmd] = abs_rev
        return abs_rev

    def get_checkout_cmd(self):
        cwd = os.getcwd()
        clone = 'hg clone -r %s %s %s' % (self.rev, self.repo,
                                          self.checkout_dir)
        cd_to_repo_dir = 'cd %s' % self.checkout_dir
        update = 'hg update -r %s' % self.rev
        cd_back = 'cd %s' % cwd
        return '; '.join([clone, cd_to_repo_dir, update, cd_back])

    @property
    def parent_rev(self):
        if self.parent:
            return self.parent
        rev = self.rev
        if self.rev == 'WORK':
            rev = 'tip'
        cmd = 'hg log -r %s --template {node|short}' % rev
        self.parent = tools.run_command(cmd)
        return self.parent

    @property
    def exe_dir(self):
        assert os.path.exists(self.checkout_dir), self.checkout_dir
        exe_dir = os.path.join(self.checkout_dir, 'downward', self.part)
        # "downward" dir has been renamed to "src"
        if not os.path.exists(exe_dir):
            exe_dir = os.path.join(self.checkout_dir, 'src', self.part)
        return exe_dir


class TranslatorHgCheckout(HgCheckout):
    def __init__(self, *args, **kwargs):
        HgCheckout.__init__(self, 'translate', *args, **kwargs)


class PreprocessorHgCheckout(HgCheckout):
    def __init__(self, *args, **kwargs):
        HgCheckout.__init__(self, 'preprocess', *args, **kwargs)


class PlannerHgCheckout(HgCheckout):
    def __init__(self, *args, **kwargs):
        HgCheckout.__init__(self, 'search', *args, **kwargs)


# ---------- Subversion -------------------------------------------------------

class SvnCheckout(Checkout):
    DEFAULT_URL = 'svn+ssh://downward-svn/trunk/downward'
    DEFAULT_REV = 'WORK'

    REV_REGEX = re.compile(r'Revision: (\d+)')

    def __init__(self, part, repo, rev=DEFAULT_REV):
        rev = str(rev)
        name = part + '-' + rev
        rev_abs = self.get_rev_abs(repo, rev)

        if rev == 'WORK':
            logging.error('Comparing SVN working copy is not supported')
            sys.exit(1)

        checkout_dir = part + '-' + rev_abs

        Checkout.__init__(self, part, repo, rev_abs, checkout_dir, name)

    def get_rev_abs(self, repo, rev):
        try:
            # If we have a number string, return it
            int(rev)
            return rev
        except ValueError:
            pass

        if rev.upper() == 'WORK':
            return 'WORK'
        elif rev.upper() == 'HEAD':
            # We want the HEAD revision number
            return self._get_rev(repo)
        else:
            logging.error('Invalid SVN revision specified: %s' % rev)
            sys.exit()

    def _get_rev(self, repo):
        """
        Returns the revision for the given repo. If the repo is a remote URL,
        the HEAD revision is returned. If the repo is a local path, the
        working copy's version is returned.
        """
        env = {'LANG': 'C'}
        cmd = 'svn info %s' % repo
        if cmd in ABS_REV_CACHE:
            return ABS_REV_CACHE[cmd]
        output = tools.run_command(cmd, env=env)
        match = self.REV_REGEX.search(output)
        if not match:
            logging.error('Unable to get HEAD revision number')
            sys.exit()
        rev_number = match.group(1)
        ABS_REV_CACHE[cmd] = rev_number
        return rev_number

    def get_checkout_cmd(self):
        return 'svn co %s@%s %s' % (self.repo, self.rev, self.checkout_dir)

    def compile(self):
        """
        We need to compile the code if the executable does not exist.
        Additionally we want to compile it, when we run an experiment with
        the working copy to make sure the executable is based on the latest
        version of the code. Obviously we don't need no compile the
        translator code.
        """
        if self.part == 'translate':
            return

        if self.rev == 'WORK' or self._get_executable(default=None) is None:
            cwd = os.getcwd()
            os.chdir(self.exe_dir)
            subprocess.call(['make'])
            os.chdir(cwd)

    @property
    def parent_rev(self):
        return self._get_rev(self.checkout_dir)

    @property
    def exe_dir(self):
        # checkout_dir is exe_dir for SVN
        assert os.path.exists(self.checkout_dir)
        return self.checkout_dir


class TranslatorSvnCheckout(SvnCheckout):
    DEFAULT_URL = 'svn+ssh://downward-svn/trunk/downward/translate'

    def __init__(self, repo=DEFAULT_URL, rev=SvnCheckout.DEFAULT_REV):
        SvnCheckout.__init__(self, 'translate', repo, rev)


class PreprocessorSvnCheckout(SvnCheckout):
    DEFAULT_URL = 'svn+ssh://downward-svn/trunk/downward/preprocess'

    def __init__(self, repo=DEFAULT_URL, rev=SvnCheckout.DEFAULT_REV):
        SvnCheckout.__init__(self, 'preprocess', repo, rev)


class PlannerSvnCheckout(SvnCheckout):
    DEFAULT_URL = 'svn+ssh://downward-svn/trunk/downward/search'

    def __init__(self, repo=DEFAULT_URL, rev=SvnCheckout.DEFAULT_REV):
        SvnCheckout.__init__(self, 'search', repo, rev)

# -----------------------------------------------------------------------------


def make_checkouts(combinations):
    """
    Checks out and compiles the code
    """
    # Checkout and compile each revision only once
    for part in set(itertools.chain(*combinations)):
        part.checkout()
        part.compile()
