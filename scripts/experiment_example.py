timeout = 666
memory = 1024

configurations = [
        "CausalGraph", 
        "ContextEnhancedPreferred",
]

suite = [
    "ICAPS04_PAPER",
    "satellite:p33-HC-pfile13.pddl",
    "airport",
]

def reports():
    print "blubb"
    return None
