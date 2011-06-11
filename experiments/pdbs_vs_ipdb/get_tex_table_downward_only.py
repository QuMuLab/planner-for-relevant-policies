#from datetime import datetime

filenames_downward_1 = [
                        "../pdbs_20110610/exp-mo-pdbs_1b-eval-p-abs.html",
                        "../pdbs_20110610/exp-mo-pdbs_2b-eval-p-abs.html",
                        "../pdbs_20110610/exp-mo-pdbs_3b-eval-p-abs.html",
                        "../pdbs_20110610/exp-mo-pdbs_3b-eval-p-abs.html",
                        "../pdbs_20110610/exp-mo-pdbs_1b-eval-p-abs.html",
                        "../pdbs_20110610/exp-mo-pdbs_1b-eval-p-abs.html",
                        "../pdbs_20110610/exp-mo-pdbs_1b-eval-p-abs.html"]
filenames_downward_2 = [
                        "../hhh_20110605/exp-ss-hhh-v2-eval-p-abs.html",
                        "../hhh_ap_20110605/exp-ss-hhh-ap-v2-eval-p-abs.html",
                        "../hhh_pw_20110605/exp-ss-hhh-pw-v2-eval-p-abs.html",
                        "../hhh_pw_20110605/exp-ss-hhh-pw-v2-eval-p-abs.html",
                        "../hhh_20110605/exp-ss-hhh-v2-eval-p-abs.html",
                        "../hhh_20110605/exp-ss-hhh-v2-eval-p-abs.html",
                        "../hhh_20110605/exp-ss-hhh-v2-eval-p-abs.html"]
domains = ["log", "air", "pipesworld-not", "pipesworld-tan", "psr", "sat", "tpp"]
index = 
assert(len(filenames_downward_1) == len(filenames_downward_2))
domain = domains[index]

def evaluate_downward(filename):
    prob = []
    exp = {}
    t_s = {}
    t_total = {} # we calculate t_h from t_total - t_s

    coll_exp, coll_t_s, coll_t_total = False, False, False
    collect_next = False
    next_problem = ""

    for line in open(filename):
        #print(line)

        if line.startswith("<th>expansions"):
            # the next values are the expansion
            coll_exp = True
            #print("coll_exp == True")

        elif line.startswith("<th>total_time"):
            # the next values are total times
            coll_t_total = True

        elif line.startswith("<th>search_time"):
            # the next values are total times
            coll_t_s = True

        elif line.startswith("<td><b>SUM"):
            coll_exp, coll_t_s, coll_t_total = False, False, False
            #print("every coll is False")

        elif line.startswith("<td><b>GM"):
            coll_exp, coll_t_s, coll_t_total = False, False, False
            #print("every coll is False")

        elif coll_exp:
            if collect_next:
                #print(line)
                #TODO
                raw_exp = line.split(">")[2].split("<")[0]
                if raw_exp.isnumeric():
                    exp[next_problem] = raw_exp

                collect_next = False
                #print("collect_next == False")

        elif coll_t_total:
            if collect_next:
                #print(line)
                raw_total = line.split(">")[2].split("<")[0]
                #print("raw_total", raw_total)
                #print("next_problem", next_problem)
                if raw_total != "\n":
                    t_total[next_problem] = round(float(raw_total), 2)

                collect_next = False

        elif coll_t_s:
            if collect_next:
                #print(line)
                raw_t_s = line.split(">")[2].split("<")[0]
                #print("raw_t_s", raw_t_s)
                #print("next_problem", next_problem)
                if raw_t_s != "\n":
                    t_s[next_problem] = round(float(raw_t_s), 2)

                collect_next = False

        if line.startswith("<td><b>" + domain):
            #print("line starts with <td><b>", domain)
            collect_next = True
            if domain == "log":
                next_problem = line.split("-")[1] + "-" + \
                line.split("-")[2].split(".")[0]
            elif domain == "air":
                next_problem = line[16:18]
            elif domain == "pipesworld-not":
                next_problem = line[29:31]
            elif domain == "pipesworld-tan":
                next_problem = line[27:29]
            elif domain == "psr":
                next_problem = line[18:20]
            elif domain == "sat":
                next_problem = line[18:20]
            elif domain == "tpp":
                next_problem = line[12:14]


    print(exp)
    print(t_total)
    print(t_s)

    # now calculate the construction time
    assert len(t_s) == len(t_total)
    t_h = {}
    for prob in t_total.keys():
        t_h[prob] = round(float(t_total[prob]) - float(t_s[prob]), 2)

    print(t_h)
    return(t_h, exp, t_s)


if __name__ == '__main__':

    result_downward_1 = evaluate_downward(filenames_downward_1[index])

    result_downward_2 = evaluate_downward(filenames_downward_2[index])

    # latex output
    print("%%%", domains[index], filenames_downward_1[index],
          filenames_downward_2[index], "%%%")
    # format   inst & $T_h$ & exp & $T_s$ & $T_h$ & exp & $T_s$\\\hline
    # example  $4-0$ & 3.20 & 0 & 0 & 2.02 & 21 & 0.1 \\\hline

    # first get all problems and sort them
    all_probs = set(result_downward_1[0]).union(result_downward_2[0])
    list_all_probs = sorted(all_probs)
    for prob in list_all_probs:
        st = "$" + prob + "$ & "
        if prob in result_downward_1[0]:
            st += str(result_downward_1[0][prob]) + " & "
        else:
            st += "X & "

        if prob in result_downward_1[1]:
            st += str(result_downward_1[1][prob]) + " & "
        else:
            st += "X & "

        if prob in result_downward_1[2]:
            st += str(result_downward_1[2][prob]) + " &"
        else:
            st += "X &"

        if prob in result_downward_2[0]:
            st += str(result_downward_2[0][prob]) + " & "
        else:
            st += "X & "

        if prob in result_downward_2[1]:
            st += str(result_downward_2[1][prob]) + " & "
        else:
            st += "X & "

        if prob in result_downward_2[2]:
            st += str(result_downward_2[2][prob]) + " \\\\\hline"
        else:
            st += "X \\\\\hline"

        print(st)
