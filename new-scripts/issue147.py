#! /usr/bin/env python
from issue102 import build_makefile_experiment

def satellite_big():
    probs = [
        #'p30-HC-pfile10.pddl', 'p31-HC-pfile11.pddl', 'p32-HC-pfile12.pddl', 
        #'p33-HC-pfile13.pddl', 'p34-HC-pfile14.pddl', 'p35-HC-pfile15.pddl', 
        'p36-HC-pfile16.pddl',
        ]
    return ['satellite:' + prob for prob in probs]
    
def arch_comp_suite():
    return satellite_big() + ['logistics00:probLOGISTICS-7-0.pddl']


def compare_architectures():
    settings = [('32bit', []), ('64bit', [('-m32', '-m64')])]
    build_makefile_experiment(settings)

if __name__ == '__main__':
    compare_architectures()
