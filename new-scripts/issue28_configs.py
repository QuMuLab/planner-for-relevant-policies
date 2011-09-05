#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

def configs():
    return [
        ("LAMA11-initial", '''\
         --heuristic "hlm,hff=lm_ff_syn(lm_rhw(\
             reasonable_orders=true,lm_cost_type=ONE,cost_type=ONE))"\
         --search "lazy_greedy([hff,hlm],preferred=[hff,hlm],\
                               cost_type=ONE)"''')]
