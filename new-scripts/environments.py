import os
import math

import tools

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPTS_DIR, 'data')


class Environment(object):
    @classmethod
    def add_subparser(cls, subparsers):
        pass

    @classmethod
    def write_main_script(cls, exp):
        raise NotImplementedError

    @classmethod
    def build_linked_resources(cls, run):
        """
        Only if we are building an argo experiment, we need to add all linked
        resources to the resources list.
        """
        pass

    @classmethod
    def get_end_instructions(cls, exp):
        return ''


class LocalEnvironment(Environment):
    @classmethod
    def add_subparser(cls, subparsers):
        import multiprocessing
        cores = multiprocessing.cpu_count()

        parser = subparsers.add_parser('local', help='Local Experiment')
        parser.add_argument(
            '-j', '--processes', type=int, default=1,
            choices=xrange(1, cores + 1),
            help='number of parallel processes to use (default: 1)')

    @classmethod
    def write_main_script(cls, exp):
        dirs = [repr(os.path.relpath(run.dir, exp.path)) for run in exp.runs]
        replacements = {'DIRS': ',\n'.join(dirs),
                        'PROCESSES': str(exp.processes)}

        script = open(os.path.join(DATA_DIR, 'local-job-template.py')).read()
        for orig, new in replacements.items():
            script = script.replace('"""' + orig + '"""', new)

        filename = exp._get_abs_path('run')

        with open(filename, 'w') as file:
            file.write(script)
            # Make run script executable
            os.chmod(filename, 0755)

    @classmethod
    def get_end_instructions(cls, exp):
        return ('You can run the experiment now by calling %s' %
                exp.compact_main_script_path)


class GkiGridEnvironment(Environment):
    @classmethod
    def add_subparser(cls, subparsers):
        parser = subparsers.add_parser('gkigrid', help='Gkigrid experiment')
        parser.add_argument(
            '-q', '--queue', default='opteron_core.q',
            help='name of the queue to use for the experiment')
        parser.add_argument(
            '--runs-per-task', type=int, default=1,
            help='how many runs to put into one task')
        parser.add_argument(
            '--priority', type=int, default=0, choices=xrange(-1023, 1024 + 1),
            metavar='NUM', help='priority of the job [-1023, 1024]')

    @classmethod
    def write_main_script(cls, exp):
        num_tasks = math.ceil(len(exp.runs) / float(exp.runs_per_task))
        job_params = {
            'logfile': exp.name + '.log',
            'errfile': exp.name + '.err',
            'num_tasks': num_tasks,
            'queue': exp.queue,
            'priority': exp.priority,
        }
        template_file = os.path.join(DATA_DIR, 'gkigrid-job-header-template')
        script_template = open(template_file).read()
        script = script_template % job_params

        script += '\n'

        run_groups = tools.divide_list(exp.runs, exp.runs_per_task)

        for task_id, run_group in enumerate(run_groups, start=1):
            script += 'if [[ $SGE_TASK_ID == %s ]]; then\n' % task_id
            for run in run_group:
                # Change into the run dir
                script += '  cd %s\n' % os.path.relpath(run.dir, exp.path)
                script += '  echo "queue = \'$QUEUE\'" >> properties\n'
                script += '  ./run\n'
            script += 'fi\n'

        filename = exp._get_abs_path(exp.name + '.q')

        with open(filename, 'w') as file:
            file.write(script)

    @classmethod
    def get_end_instructions(cls, exp):
        return ('You can change into the experiment directory now and submit '
                'the experiment to the '
                'queue by calling "qsub %s.q"' % exp.name)


class MaiaEnvironment(Environment):
    @classmethod
    def add_subparser(cls, subparsers):
        parser = subparsers.add_parser('maia', help='Maia experiment')
        parser.add_argument(
            '-q', '--queue', default='opteron_core.q',
            help='name of the queue to use for the experiment')
        parser.add_argument(
            '--runs-per-task', type=int, default=1,
            help='how many runs to put into one task')
        parser.add_argument(
            '--priority', type=int, default=0, choices=xrange(-1023, 1024 + 1),
            metavar='NUM', help='priority of the job [-1023, 1024]')

    @classmethod
    def write_main_script(cls, exp):
        num_tasks = math.ceil(len(exp.runs) / float(exp.runs_per_task))
        job_params = {
            'logfile': exp.name + '.log',
            'errfile': exp.name + '.err',
            'num_tasks': num_tasks,
            'queue': exp.queue,
            'priority': exp.priority,
        }
        template_file = os.path.join(DATA_DIR, 'gkigrid-job-header-template')
        script_template = open(template_file).read()
        script = script_template % job_params

        script += '\n'

        run_groups = tools.divide_list(exp.runs, exp.runs_per_task)

        for task_id, run_group in enumerate(run_groups, start=1):
            script += 'if [[ $SGE_TASK_ID == %s ]]; then\n' % task_id
            for run in run_group:
                # Change into the run dir
                script += '  cd %s\n' % os.path.relpath(run.dir, exp.path)
                script += '  ./run\n'
            script += 'fi\n'

        filename = exp._get_abs_path(exp.name + '.q')

        with open(filename, 'w') as file:
            file.write(script)

    @classmethod
    def get_end_instructions(cls, exp):
        return ('You can change into the experiment directory now and submit '
                'the experiment to the '
                'queue by calling "qsub %s.q"' % exp.name)


class ArgoEnvironment(Environment):
    """
    This environment is currently not supported, but we keep it here to hold
    the already written code.
    """

    @classmethod
    def add_subparser(cls, subparsers):
        subparsers.add_parser('argo', help='Argo Experiment')

    @classmethod
    def write_main_script(cls, exp):
        raise NotImplementedError

    @classmethod
    def build_linked_resources(cls, run):
        # Copy the linked resource into the run dir by adding the linked
        # resource to the normal resources list.
        for resource_name in run.linked_resources:
            source = run.experiment.env_vars.get(resource_name, None)
            if not source:
                logging.error('If you require a resource you have to add it '
                              'to the experiment')
                sys.exit(1)
            basename = os.path.basename(source)
            dest = run._get_abs_path(basename)
            run.resources.append((source, dest, True, False))
