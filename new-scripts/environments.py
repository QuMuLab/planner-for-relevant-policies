import os
import math

import tools

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPTS_DIR, 'data')

class Environment(object):
    def get_main_script(self):
        raise NotImplemented

class GkiGridEnvironment(Environment):
    @classmethod
    def add_subparser(cls, subparsers):
        parser = subparsers.add_parser('gkigrid',
                                            help='Create a gkigrid experiment')
        parser.add_argument(
            '-q', '--queue', default='athlon_core.q',
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
            'driver_timeout': exp.timeout * exp.runs_per_task + 30,
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
                script += '  cd %s\n' % os.path.relpath(run.dir, self.base_dir)
                script += '  ./run\n'
            script += 'fi\n'

        filename = exp.name
        if not filename.endswith('.q'):
            filename += '.q'
        filename = exp._get_abs_path(filename)

        with open(filename, 'w') as file:
            file.write(script)

    @classmethod
    def get_end_instructions(cls, exp):
        return ('You can submit the experiment to the '
                'queue now by calling "qsub ./%(name)s/<q-filename.q>"' %
                exp.__dict__)


class ArgoEnvironment(Environment):
    pass
