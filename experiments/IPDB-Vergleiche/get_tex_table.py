#from datetime import datetime

filenames_old = ["../ipdb_hhh_old/logistics00-iPDB-default.txt",
                 "../ipdb_hhh_old/airport-b.txt",
                 "../ipdb_hhh_old/pnt-iPDB-best.txt",
                 "../ipdb_hhh_old/pwt-iPDB-best.txt",
                 "../ipdb_hhh_old/psr-iPDB-default.txt",
                 "../ipdb_hhh_old/sat-iPDB-default.txt",
                 "../ipdb_hhh_old/tpp-iPDB-default.txt"]
filenames_downward = [
                      "../hhh_20110605/exp-ss-hhh-v2-eval-p-abs.html",
                      "../hhh_ap_20110605/exp-ss-hhh-ap-v2-eval-p-abs.html",
                      "../hhh_pw_20110605/exp-ss-hhh-pw-v2-eval-p-abs.html",
                      "../hhh_pw_20110605/exp-ss-hhh-pw-v2-eval-p-abs.html",
                      "../hhh_20110605/exp-ss-hhh-v2-eval-p-abs.html",
                      "../hhh_20110605/exp-ss-hhh-v2-eval-p-abs.html",
                      "../hhh_20110605/exp-ss-hhh-v2-eval-p-abs.html"]
domains = ["log", "air", "pipesworld-not", "pipesworld-tan", "psr", "sat", "tpp"]
index = 6
assert(len(filenames_old) == len(filenames_downward))
domain = domains[index]

def evaluate_old(filename):
    prob = []
    t_h = []
    exp = []
    t_s = []

    for line in open(filename):
        if len(line.split(" ")) == 14:

            if line.split(" ")[1] == "1":
                prob_raw = line.split(" ")[0]
                if (prob_raw.startswith("log")):
                    prob.append(prob_raw[4:-6])
                elif (prob_raw.startswith("air")):
                    prob.append(prob_raw[7:9])
                elif (prob_raw.startswith("pnt")):
                    prob.append(prob_raw[3:5])
                elif (prob_raw.startswith("pwt")):
                    prob.append(prob_raw[3:5])
                elif (prob_raw.startswith("psr")):
                    prob.append(prob_raw[3:5])
                elif (prob_raw.startswith("sat")):
                    prob.append(prob_raw[3:5])
                elif (prob_raw.startswith("tpp")):
                    prob.append(prob_raw[3:5])

                t_h_raw = line.split(" ")[4]
                if t_h_raw == "X":
                    t_h.append("X")
                else:
                    t_h.append(round(float(t_h_raw), 2))

                exp.append(line.split(" ")[9])

                t_s_raw = line.split(" ")[11]
                if t_s_raw == "X":
                    t_s.append("X")
                else:
                    t_s.append(round(float(t_s_raw), 2))

        elif len(line.split(" ")) == 13:

            if line.split(" ")[1] == "1":
                prob_raw = line.split(" ")[0]

                if (prob_raw.startswith("air")):
                    prob.append(prob_raw[7:9])

                t_h_raw = line.split(" ")[4]
                if t_h_raw == "X":
                    t_h.append("X")
                else:
                    t_h.append(round(float(t_h_raw), 2))

                exp.append(line.split(" ")[9])

                t_s_raw = line.split(" ")[10]
                if t_s_raw == "X":
                    t_s.append("X")
                else:
                    t_s.append(round(float(t_s_raw), 2))



    print("prob", prob)
    print("t_h", t_h)
    print("exp", exp)
    print("t_s", t_s)

    return(prob, t_h, exp, t_s)

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
                next_problem = line.split("-")[1] + "-" + line.split("-")[2].split(".")[0]
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

    result_old = evaluate_old(filenames_old[index])

    result_downward = evaluate_downward(filenames_downward[index])

    # latex output
    print("%%%", domains[index], filenames_old[index], filenames_downward[index], "%%%")
    # format   inst & $T_h$ & exp & $T_s$ & $T_h$ & exp & $T_s$\\\hline
    # example  $4-0$ & 3.20 & 0 & 0 & 2.02 & 21 & 0.1 \\\hline
    counter = 0
    count_hits = 0
    for prob in result_old[0]:
        st = "$" + prob + "$ & "
        st += str(result_old[1][counter]) + " & "
        st += str(result_old[2][counter]) + " & "
        st += str(result_old[3][counter]) + " & "
        if prob in result_downward[0]:
            st += str(result_downward[0][prob]) + " & "
            count_hits += 1
        else:
            st += "X & "
        if prob in result_downward[1]:
            st += str(result_downward[1][prob]) + " & "
        else:
            st += "X & "
        if prob in result_downward[2]:
            st += str(result_downward[2][prob]) + " \\\\\hline"
        else:
            st += "X \\\\\hline"
        print(st)
        counter += 1

    if count_hits < len(result_downward[0]):
        # suche die Instanzen, die FD zusätzlich gelöst hat
        fd_additional = []
        #print(result_downward[0].keys())
        for p in result_downward[0].keys():
            if p not in result_old[0]:
                fd_additional.append(p)
        #print("fd_additional", fd_additional)
        for p in sorted(fd_additional):
            st = "$" + p + "$ & "
            st += " X & "
            st += " X & "
            st += " X & "
            if p in result_downward[0]:
                st += str(result_downward[0][p]) + " & "
                count_hits += 1
            else:
                st += "X & "
            if p in result_downward[1]:
                st += str(result_downward[1][p]) + " & "
            else:
                st += "X & "
            if p in result_downward[2]:
                st += str(result_downward[2][p]) + " \\\\\hline"
            else:
                st += "X \\\\\hline"
            print(st)
