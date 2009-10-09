# -*- coding: utf-8 -*-

def latex_format_heur(text):
    text = {
        "h+": r"\hplus",
        "hmax": r"\hmax",
        "K&D": r"\hla",
        "lmcut": r"\hlmcut",
        }.get(text, text)
    text = text.replace("&", r"\&")
    return text


def latex_format_planner(text):
    text = {
        "lmcut": r"\hlmcut",
        "lsuda": r"\hla",
        "hmax": r"\hmax",
        "gamer": r"\gamer",
        "hhh 10k": r"\hmas",
        "blind": r"\hblind",
        "hsp-f": r"\hspsf",
        }.get(text, text)
    return text


def latex_format_domain(text):
    text = text.capitalize()
    text = {
        "Freecell": "FreeCell",
        "Logistics98": "Logistics-1998",
        "Logistics00": "Logistics-2000",
        "Miconic": "Miconic-STRIPS",
        "Mprime": "MPrime",
        "Openstacks-strips": "Openstacks",
        "Pathways-noneg": "Pathways",
        "Pipesworld-tankage": "Pipesworld-Tankage",
        "Pipesworld-notankage": "Pipesworld-NoTankage",
        "Psr-small": "PSR-Small",
        "Tpp": "TPP",
        "Trucks-strips": "Trucks",
        }.get(text, text)
    return text


def latex_format_task(domain, text):
    if domain == "satellite":
        text = text.partition("-")[2]
    for prefix in ["probblocks-", "pfile", "prob", "p"]:
        if text.startswith(prefix):
            text = text[len(prefix):]
    for suffix in [".pddl"]:
        if text.endswith(suffix):
            text = text[:-len(suffix)]
    text = text.lstrip("0")
    return r"\#%s" % text


def isfloat(text):
    try:
        float(text)
        return True
    except ValueError:
        return False


def add_bold(parts, best, start=0, step=1, end=None):
    def trim(text):
        return text.strip().strip(r"\%&").strip()
    if end is None:
        end = len(parts)
    values = map(trim, parts[start:end:step])
    best_val = best(map(float, filter(isfloat, values)))
    for pos in xrange(start, end, step):
        val = parts[pos]
        if isfloat(trim(val)) and float(trim(val)) == best_val:
            left, mid, right = val.partition("&")
            parts[pos] = r"%s%s\textbf{%s}" % (left, mid, right)
