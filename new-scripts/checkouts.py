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
    def __init__(self, part, repo, rev, checkout_dir):
        # Directory name of the planner part (translate, preprocess, search)
        self.part = part
        self.repo = repo
        self.rev = str(rev)

        if not os.path.isabs(checkout_dir):
            checkout_dir = os.path.join(CHECKOUTS_DIR, checkout_dir)
        self.checkout_dir = os.path.abspath(checkout_dir)

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    @property
    def name(self):
        """
        Nickname for the checkout that is used for the reports and comparisons.
        """
        if self.rev == 'WORK':
            return 'WORK'
        return os.path.basename(self.checkout_dir)

    def checkout(self):
        # We don't need to check out the working copy
        if self.rev == 'WORK':
            return

        # If there's already a checkout, don't checkout again
        path = self.checkout_dir
        if os.path.exists(path):
            logging.info('Checkout "%s" already exists' % path)
        else:
            cmd = self.get_checkout_cmd()
            print cmd
            subprocess.call(cmd, shell=True)
        assert os.path.exists(path), 'Could not checkout to "%s"' % path

    def get_checkout_cmd(self):
        raise Exception('Not implemented')

    def compile(self):
        """
        We issue the build_all command unconditionally and let "make" take care
        of checking if something has to be recompiled.
        """
        cwd = os.getcwd()
        os.chdir(self.src_dir)
        try:
            subprocess.call(['./build_all'])
        except OSError:
            logging.warning('Changeset %s does not have the build_all script. '
                            'Please compile it manually.' % self.rev)
        os.chdir(cwd)

    def get_path(self, *rel_path):
        return os.path.join(self.checkout_dir, *rel_path)

    def get_bin(self, *bin_path):
        """Return the absolute path to this part's src directory."""
        return os.path.join(self.bin_dir, *bin_path)

    def get_path_dest(self, *rel_path):
        return os.path.join('code-' + self.name, *rel_path)

    def get_bin_dest(self):
        return self.get_path_dest(self.part)

    @property
    def src_dir(self):
        """Returns the path to the global Fast Downward source directory.

        The directory "downward" dir has been renamed to "src", but we still
        want to support older changesets."""
        assert os.path.exists(self.checkout_dir), self.checkout_dir
        src_dir = self.get_path('downward')
        if not os.path.exists(src_dir):
            src_dir = self.get_path('src')
        return src_dir

    @property
    def bin_dir(self):
        return os.path.join(self.src_dir, self.part)

    @property
    def parent_rev(self):
        raise Exception('Not implemented')

    @property
    def shell_name(self):
        return '%s_%s' % (self.part.upper(), self.name)


# ---------- Mercurial --------------------------------------------------------

class HgCheckout(Checkout):
    """
    Base class for the three checkout types (translate, preprocess, search).
    """
    DEFAULT_URL = tools.BASE_DIR
    DEFAULT_REV = 'WORK'

    def __init__(self, part, repo=DEFAULT_URL, rev=DEFAULT_REV, dest=''):
        """
        part: One of translate, preprocess, search
        repo: Path to the hg repository. Can be either local or remote.
        rev:  Changeset. Can be any valid hg revision specifier or "WORK"
        dest: If set this will be the checkout's name. Use this if you need to
              checkout the same revision multiple times and want to alter each
              checkout manually (e.g. for comparing Makefile options).
        """
        if dest and rev == 'WORK':
            logging.error('You cannot have multiple copies of the working dir')
            sys.exit(1)

        # Find proper absolute revision
        rev = self.get_abs_rev(repo, rev)

        if rev.upper() == 'WORK':
            checkout_dir = tools.BASE_DIR
        else:
            checkout_dir = dest if dest else rev

        Checkout.__init__(self, part, repo, rev, checkout_dir)
        self.parent = None

    def get_abs_rev(self, repo, rev):
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


class Translator(HgCheckout):
    def __init__(self, *args, **kwargs):
        HgCheckout.__init__(self, 'translate', *args, **kwargs)


class Preprocessor(HgCheckout):
    def __init__(self, *args, **kwargs):
        HgCheckout.__init__(self, 'preprocess', *args, **kwargs)


class Planner(HgCheckout):
    def __init__(self, *args, **kwargs):
        HgCheckout.__init__(self, 'search', *args, **kwargs)


# ---------- Subversion -------------------------------------------------------

class SvnCheckout(Checkout):
    DEFAULT_URL = 'svn+ssh://downward-svn/trunk/'
    DEFAULT_REV = 'WORK'

    REV_REGEX = re.compile(r'Revision: (\d+)')

    def __init__(self, part, repo=DEFAULT_URL, rev=DEFAULT_REV):
        rev = str(rev)
        rev = self._get_abs_rev(repo, rev)

        if rev == 'WORK':
            logging.error('Comparing SVN working copy is not supported')
            sys.exit(1)

        checkout_dir = rev

        Checkout.__init__(self, part, repo, rev, checkout_dir)

    def _get_abs_rev(self, repo, rev):
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

    @property
    def parent_rev(self):
        return self._get_rev(self.checkout_dir)


class TranslatorSvn(SvnCheckout):
    def __init__(self, *args, **kwargs):
        SvnCheckout.__init__(self, 'translate', *args, **kwargs)


class PreprocessorSvn(SvnCheckout):
    def __init__(self, *args, **kwargs):
        SvnCheckout.__init__(self, 'preprocess', *args, **kwargs)


class PlannerSvn(SvnCheckout):
    def __init__(self, *args, **kwargs):
        SvnCheckout.__init__(self, 'search', *args, **kwargs)

# -----------------------------------------------------------------------------


def checkout(combinations):
    """Checks out the code once for each separate checkout directory."""
    # Checkout and compile each revision only once
    for part in sorted(set(itertools.chain(*combinations))):
        part.checkout()


def compile(combinations):
    """Compiles the code."""
    # Checkout and compile each revision only once
    for part in sorted(set(itertools.chain(*combinations))):
        part.compile()
