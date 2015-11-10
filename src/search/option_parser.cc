#include "globals.h"
#include "option_parser.h"
#include "ext/tree_util.hh"
#include "plugin.h"
#include "rng.h"
#include <algorithm>
#include <iostream>
#include <string>
#include <utility>

using namespace std;

ParseError::ParseError(string m, ParseTree pt)
    : msg(m),
      parse_tree(pt) {
}

ParseError::ParseError(string m, ParseTree pt, string correct_substring)
    : msg(m),
      parse_tree(pt),
      substr(correct_substring) {
}

void OptionParser::error(string msg) {
    throw ParseError(msg, *this->get_parse_tree());
}

void OptionParser::warning(string msg) {
    cout << "Parser Warning: " << msg << endl;
}


/*
Functions for printing help:
*/

DocStore *DocStore::instance_ = 0;

void OptionParser::set_help_mode(bool m) {
    dry_run_ = dry_run_ && m;
    help_mode_ = m;
    opts.set_help_mode(m);
}

template <class T>
static void get_help_templ(const ParseTree &pt) {
    if (Registry<T>::instance()->contains(pt.begin()->value)) {
        OptionParser p(pt, true);
        p.set_help_mode(true);
        p.start_parsing<T>();
    }
}

static void get_help(string k) {
    ParseTree pt;
    pt.insert(pt.begin(), ParseNode(k));
    get_help_templ<SearchEngine *>(pt);
    get_help_templ<Heuristic *>(pt);
    get_help_templ<ScalarEvaluator *>(pt);
    get_help_templ<Synergy *>(pt);
    get_help_templ<LandmarkGraph *>(pt);
    Plugin<OpenList<int> >::register_open_lists();
    get_help_templ<OpenList<int> *>(pt);
    get_help_templ<ShrinkStrategy *>(pt);
}

template <class T>
static void get_full_help_templ() {
    DocStore::instance()->set_synopsis(TypeNamer<T>::name(), "",
                                       TypeDocumenter<T>::synopsis());
    vector<string> keys = Registry<T>::instance()->get_keys();
    for (size_t i(0); i != keys.size(); ++i) {
        ParseTree pt;
        pt.insert(pt.begin(), ParseNode(keys[i]));
        get_help_templ<T>(pt);
    }
}

static void get_full_help() {
    get_full_help_templ<SearchEngine *>();
    get_full_help_templ<Heuristic *>();
    get_full_help_templ<ScalarEvaluator *>();
    get_full_help_templ<Synergy *>();
    get_full_help_templ<LandmarkGraph *>();
    Plugin<OpenList<int> >::register_open_lists();
    get_full_help_templ<OpenList<int> *>();
    get_full_help_templ<ShrinkStrategy *>();
}


/*
Predefining landmarks and heuristics:
*/

//takes a string of the form "word1, word2, word3 " and converts it to a vector
//(used for predefining synergies)
static std::vector<std::string> to_list(std::string s) {
    std::vector<std::string> result;
    std::string buffer;
    for (size_t i(0); i != s.size(); ++i) {
        if (s[i] == ',') {
            result.push_back(buffer);
            buffer.clear();
        } else if (s[i] == ' ') {
            continue;
        } else {
            buffer.push_back(s[i]);
        }
    }
    result.push_back(buffer);
    return result;
}

//Note: originally the following function was templated (predefine<T>),
//but there is no Synergy<LandmarkGraph>, so I split it up for now.
static void predefine_heuristic(std::string s, bool dry_run) {
    //remove newlines so they don't mess anything up:
    s.erase(std::remove(s.begin(), s.end(), '\n'), s.end());

    size_t split = s.find("=");
    std::string ls = s.substr(0, split);
    std::vector<std::string> definees = to_list(ls);
    std::string rs = s.substr(split + 1);
    OptionParser op(rs, dry_run);
    if (definees.size() == 1) { //normal predefinition
        Predefinitions<Heuristic * >::instance()->predefine(
            definees[0], op.start_parsing<Heuristic *>());
    } else if (definees.size() > 1) { //synergy
        if (!dry_run) {
            std::vector<Heuristic *> heur =
                op.start_parsing<Synergy *>()->heuristics;
            for (size_t i(0); i != definees.size(); ++i) {
                Predefinitions<Heuristic *>::instance()->predefine(
                    definees[i], heur[i]);
            }
        } else {
            for (size_t i(0); i != definees.size(); ++i) {
                Predefinitions<Heuristic *>::instance()->predefine(
                    definees[i], 0);
            }
        }
    } else {
        op.error("predefinition has invalid left side");
    }
}

static void predefine_lmgraph(std::string s, bool dry_run) {
    //remove newlines so they don't mess anything up:
    s.erase(std::remove(s.begin(), s.end(), '\n'), s.end());

    size_t split = s.find("=");
    std::string ls = s.substr(0, split);
    std::vector<std::string> definees = to_list(ls);
    std::string rs = s.substr(split + 1);
    OptionParser op(rs, dry_run);
    if (definees.size() == 1) {
        Predefinitions<LandmarkGraph *>::instance()->predefine(
            definees[0], op.start_parsing<LandmarkGraph *>());
    } else {
        op.error("predefinition has invalid left side");
    }
}


/*
Parse command line options
*/

SearchEngine *OptionParser::parse_cmd_line(
    int argc, const char **argv, bool dry_run) {
    SearchEngine *engine(0);
    for (int i = 1; i < argc; ++i) {
        string arg = string(argv[i]);
        if (arg.compare("--heuristic") == 0) {
            ++i;
            predefine_heuristic(argv[i], dry_run);
        } else if (arg.compare("--landmarks") == 0) {
            ++i;
            predefine_lmgraph(argv[i], dry_run);
        } else if (arg.compare("--search") == 0) {
            ++i;
            OptionParser p(argv[i], dry_run);
            engine = p.start_parsing<SearchEngine *>();
        } else if (arg.compare("--random-seed") == 0) {
            ++i;
            if (!g_seeded) {
                g_seeded = true;
                srand(atoi(argv[i]));
                g_rng.seed(atoi(argv[i]));
                if (!g_silent_planning)
                    cout << "random seed " << argv[i] << endl;
            }
        } else if ((arg.compare("--help") == 0) && dry_run) {
            cout << "Help:" << endl;
            bool txt2tags = false;
            vector<string> helpiands;
            if (i + 1 < argc) {
                for (int j = i + 1; j < argc; ++j) {
                    if (string(argv[j]).compare("--txt2tags") == 0) {
                        txt2tags = true;
                    } else {
                        helpiands.push_back(string(argv[j]));
                    }
                }
            }
            if (helpiands.empty()) {
                get_full_help();
            } else {
                for (int i(0); i != helpiands.size(); ++i) {
                    get_help(helpiands[i]);
                }
            }
            DocPrinter *dp;
            if (txt2tags) {
                dp = new Txt2TagsPrinter(cout);
            } else {
                dp = new PlainPrinter(cout);
            }
            dp->print_all();
            cout << "Help output finished." << endl;
            exit(0);
        } else if (arg.compare("--plan-file") == 0) {
            ++i;
            g_plan_filename = argv[i];
        } else if (arg.compare("--jic-limit") == 0) {
            ++i;
            g_jic_limit = atof(argv[i]);
        } else if (arg.compare("--trials") == 0) {
            ++i;
            g_num_trials = atoi(argv[i]);
        } else if (arg.compare("--epochs") == 0) {
            ++i;
            g_num_epochs = atoi(argv[i]);
        } else if (arg.compare("--depth") == 0) {
            ++i;
            g_trial_depth = atoi(argv[i]);
        } else if (arg.compare("--forgetpolicy") == 0) {
            ++i;
            g_forgetpolicy = (1 == atoi(argv[i]));
        } else if (arg.compare("--replan-on-failure") == 0) {
            ++i;
            g_replan_during_simulation = (1 == atoi(argv[i]));
        } else if (arg.compare("--fullstate") == 0) {
            ++i;
            g_fullstate = (1 == atoi(argv[i]));
        } else if (arg.compare("--planlocal") == 0) {
            ++i;
            g_plan_locally = (1 == atoi(argv[i]));
        } else if (arg.compare("--partial-planlocal") == 0) {
            ++i;
            g_partial_planlocal = (1 == atoi(argv[i]));
        } else if (arg.compare("--plan-with-policy") == 0) {
            ++i;
            g_plan_with_policy = (1 == atoi(argv[i]));
        } else if (arg.compare("--limit-planlocal") == 0) {
            ++i;
            g_plan_locally_limited = (1 == atoi(argv[i]));
        } else if (arg.compare("--detect-deadends") == 0) {
            ++i;
            g_detect_deadends = (1 == atoi(argv[i]));
        } else if (arg.compare("--generalize-deadends") == 0) {
            ++i;
            g_generalize_deadends = (1 == atoi(argv[i]));
        } else if (arg.compare("--online-deadends") == 0) {
            ++i;
            g_record_online_deadends = (1 == atoi(argv[i]));
        } else if (arg.compare("--sample-for-depth1-deadends") == 0) {
            ++i;
            g_sample_for_depth1_deadends = (1 == atoi(argv[i]));
        } else if (arg.compare("--combine-deadends") == 0) {
            ++i;
            g_combine_deadends = (1 == atoi(argv[i]));
        } else if (arg.compare("--repeat-fsaps-backwards") == 0) {
            ++i;
            g_repeat_fsap_backwards = (1 == atoi(argv[i]));
        } else if (arg.compare("--relevant-deadend-regression") == 0) {
            ++i;
            g_regress_only_relevant_deadends = (1 == atoi(argv[i]));
        } else if (arg.compare("--repeat-strengthening") == 0) {
            ++i;
            g_repeat_strengthening = (1 == atoi(argv[i]));
        } else if (arg.compare("--optimized-scd") == 0) {
            ++i;
            g_optimized_scd = (atoi(argv[i]) > 0);
            g_safetybelt_optimized_scd = (2 == atoi(argv[i]));
        } else if (arg.compare("--final-fsap-free-round") == 0) {
            ++i;
            g_final_fsap_free_round = atoi(argv[i]);
        } else if (arg.compare("--optimize-final-policy") == 0) {
            ++i;
            g_optimize_final_policy = atoi(argv[i]);
        } else if (arg.compare("--dump-policy") == 0) {
            ++i;
            g_dump_policy = atoi(argv[i]);
        } else if (arg.compare("--debug-output") == 0) {
            ++i;
            g_silent_planning = (1 != atoi(argv[i]));
        } else {
            cerr << "unknown option " << arg << endl << endl;
            cout << OptionParser::usage(argv[0]) << endl;
            exit_with(EXIT_INPUT_ERROR);
        }
    }

    return engine;
}

string OptionParser::usage(string progname) {
    string usage =
        "usage: \n" +
        progname + " [OPTIONS] --search SEARCH < OUTPUT\n\n"
        "* SEARCH (SearchEngine): configuration of the search algorithm\n"
        "* OUTPUT (filename): preprocessor output\n\n"
        "Options:\n"
        "--help [NAME]\n"
        "    Prints help for all heuristics, openlists, etc. called NAME.\n"
        "    Without parameter: prints help for everything available\n"
        "--landmarks LANDMARKS_PREDEFINITION\n"
        "    Predefines a set of landmarks that can afterwards be referenced\n"
        "    by the name that is specified in the definition.\n"
        "--heuristic HEURISTIC_PREDEFINITION\n"
        "    Predefines a heuristic that can afterwards be referenced\n"
        "    by the name that is specified in the definition.\n"
        "--random-seed SEED\n"
        "    Use random seed SEED\n\n"
        "--plan-file FILENAME\n"
        "    Plan will be output to a file called FILENAME\n\n"
        "--jic-limit TIME_LIMIT\n"
        "    Only perform JIC for the given time. This will be cut in half if final-fsap-free-round is used.\n\n"
        "--epochs EPOCH_COUNT (default=1)\n"
        "    Minimum number of times to execute the JIC loop. Useful if deadends are present and a single pass takes too long.\n\n"
        "--forgetpolicy 1/0\n"
        "    Throw out the policy after every simulation.\n\n"
        "--replan-on-failure 1/0 (default=1)\n"
        "    Replan if the state isn't recognized.\n\n"
        "--fullstate 1/0\n"
        "    Use full states in the regression.\n\n"
        "--planlocal 1/0\n"
        "    Plan locally to recover before planning for the goal.\n\n"
        "--partial-planlocal 1/0\n"
        "    Use the partial state that matches the expect state when planning locally.\n\n"
        "--limit-planlocal 1/0\n"
        "    Limit the planlocal searching to a fixed number of search steps.\n\n"
        "--plan-with-policy 1/0\n"
        "    Stop searching when the policy matches the current state.\n\n"
        "--depth NUM_ACTIONS (default=1000)\n"
        "    Stop simulations and consider it a failure after NUM_ACTIONS actions.\n\n"
        "--trials NUM_TRIALS (default=1)\n"
        "    Number of trials to run for the simulator.\n\n"
        "--detect-deadends 1/0\n"
        "    Use primitive deadend detection to ensure a strongly cyclic solution.\n\n"
        "--generalize-deadends 1/0\n"
        "    Generalize the deadends found based on relaxed reachability.\n\n"
        "--online-deadends 1/0\n"
        "    Generate and store deadend states that are found online.\n\n"
        "--sample-for-depth1-deadends 1/0 (default=1)\n"
        "    Analyze the non-deterministic alternate states from the generated weak plans for deadends.\n\n"
        "--combine-deadends 1/0 (default=0)\n"
        "    Combine the FSAP conditions if every applicable action is forbidden to be a new deadend.\n\n"
        "--repeat-fsaps-backwards 1/0 (default=0)\n"
        "    Keep making FSAPs as long as states where they hold have no applicable actions (experimental and mostly damaging)\n\n"
        "--optimized-scd 2/1/0 (default=2)\n"
        "    Perform optimized strong cyclic detection when checking the partial policy. A value of 2 means that it will gradually disable the scd check if it is unhelpful for the particular problem being solved.\n\n"
        "--repeat-strengthening 1/0 (default=0)\n"
        "    Repeat the strong cyclic strengthening step back to the initial state. Adds many more state-action pairs, and so is disabled by default. Only useful when optimized-scd is very effective.\n\n"
        "--relevant-deadend-regression 1/0 (default=0)\n"
        "    Regress deadends in the FSAP construction only through actions that trigger the deadend.\n\n"
        "--final-fsap-free-round 1/0 (default=0)\n"
        "    Do one final JIC round with the best policy found (closing every leaf possible).\n\n"
        "--optimize-final-policy 1/0 (default=0)\n"
        "    Do a final simulation and throw out any pair (or FSAP) not used.\n\n"
        "--dump-policy 1/2\n"
        "    Dump the policy to the file policy.out. 1 creates a switch graph (currently unsafe to use), while 2 creates a human readable form (preferred for use with the prp_api.py file).\n\n"
        "--debug-output 1/0\n"
        "    Output plans and other information during the planning process.\n\n"
        "See http://www.haz.ca/research/prp for details.";
    return usage;
}


static ParseTree generate_parse_tree(string config) {
    //remove newlines so they don't mess anything up:
    config.erase(std::remove(config.begin(), config.end(), '\n'), config.end());

    ParseTree tr;
    ParseTree::iterator top = tr.begin();
    ParseTree::sibling_iterator pseudoroot =
        tr.insert(top, ParseNode("pseudoroot", ""));
    ParseTree::sibling_iterator cur_node = pseudoroot;
    string buffer(""), key("");
    char next = ' ';
    for (size_t i(0); i != config.size(); ++i) {
        next = config.at(i);
        if ((next == '(' || next == ')' || next == ',') && buffer.size() > 0) {
            tr.append_child(cur_node, ParseNode(buffer, key));
            buffer.clear();
            key.clear();
        } else if (next == '(' && buffer.size() == 0) {
            throw ParseError("misplaced opening bracket (", *cur_node, config.substr(0, i));
        }
        switch (next) {
        case ' ':
            break;
        case '(':
            cur_node = last_child(tr, cur_node);
            break;
        case ')':
            if (cur_node == pseudoroot)
                throw ParseError("missing (", *cur_node, config.substr(0, i));
            cur_node = tr.parent(cur_node);
            break;
        case '[':
            if (!buffer.empty())
                throw ParseError("misplaced opening bracket [", *cur_node, config.substr(0, i));
            tr.append_child(cur_node, ParseNode("list", key));
            key.clear();
            cur_node = last_child(tr, cur_node);
            break;
        case ']':
            if (!buffer.empty()) {
                tr.append_child(cur_node, ParseNode(buffer, key));
                buffer.clear();
                key.clear();
            }
            if (cur_node->value.compare("list") != 0) {
                throw ParseError("mismatched brackets", *cur_node, config.substr(0, i));
            }
            cur_node = tr.parent(cur_node);
            break;
        case ',':
            break;
        case '=':
            if (buffer.empty())
                throw ParseError("expected keyword before =", *cur_node, config.substr(0, i));
            key = buffer;
            buffer.clear();
            break;
        default:
            buffer.push_back(tolower(next));
            break;
        }
    }
    if (cur_node->value.compare("pseudoroot") != 0)
        throw ParseError("missing )", *cur_node);
    if (buffer.size() > 0)
        tr.append_child(cur_node, ParseNode(buffer, key));


    //the real parse tree is the first (and only) child of the pseudoroot.
    //pseudoroot is only a placeholder.
    ParseTree real_tr = subtree(tr, tr.begin(pseudoroot));
    return real_tr;
}

OptionParser::OptionParser(const string config, bool dr)
    : opts(false),
      parse_tree(generate_parse_tree(config)),
      dry_run_(dr),
      help_mode_(false),
      next_unparsed_argument(first_child_of_root(parse_tree)) {
}


OptionParser::OptionParser(ParseTree pt, bool dr)
    : opts(false),
      parse_tree(pt),
      dry_run_(dr),
      help_mode_(false),
      next_unparsed_argument(first_child_of_root(parse_tree)) {
}


string str_to_lower(string s) {
    transform(s.begin(), s.end(), s.begin(), ::tolower);
    return s;
}

void OptionParser::add_enum_option(string k,
                                   vector<string > enumeration,
                                   string h, string def_val,
                                   vector<string> enum_docs,
                                   const OptionFlags &flags) {
    if (help_mode_) {
        ValueExplanations value_explanations;
        string enum_descr = "{";
        for (size_t i(0); i != enumeration.size(); ++i) {
            enum_descr += enumeration[i];
            if (i != enumeration.size() - 1) {
                enum_descr += ", ";
            }
            if (enum_docs.size() > i) {
                value_explanations.push_back(make_pair(enumeration[i],
                                                       enum_docs[i]));
            }
        }
        enum_descr += "}";

        DocStore::instance()->add_arg(parse_tree.begin()->value,
                                      k, h,
                                      enum_descr, def_val, flags.mandatory,
                                      value_explanations);
        return;
    }

    //enum arguments can be given by name or by number:
    //first parse the corresponding string like a normal argument...
    add_option<string>(k, h, def_val, flags);

    if (!flags.mandatory && !opts.contains(k))
        return;

    string name = str_to_lower(opts.get<string>(k));

    //...then check if the parsed string can be treated as a number
    stringstream str_stream(name);
    int x;
    if (!(str_stream >> x).fail()) {
        if (x > enumeration.size()) {
            error("invalid enum argument " + name
                  + " for option " + k);
        }
        opts.set<int>(k, x);
    } else {
        //...otherwise try to map the string to its position in the enumeration vector
        transform(enumeration.begin(), enumeration.end(), enumeration.begin(),
                  str_to_lower); //make the enumeration lower case
        vector<string>::const_iterator it =
            find(enumeration.begin(), enumeration.end(), name);
        if (it == enumeration.end()) {
            error("invalid enum argument " + name
                  + " for option " + k);
        }
        opts.set<int>(k, it - enumeration.begin());
    }
}

Options OptionParser::parse() {
    //check if there were any arguments with invalid keywords,
    //or positional arguments after keyword arguments
    string last_key = "";
    for (ParseTree::sibling_iterator pti = first_child_of_root(parse_tree);
         pti != end_of_roots_children(parse_tree); ++pti) {
        if (pti->key.compare("") != 0) {
            bool valid_key = false;
            for (size_t i(0); i != valid_keys.size(); ++i) {
                if (valid_keys[i].compare(pti->key) == 0) {
                    valid_key = true;
                    break;
                }
            }
            if (!valid_key) {
                error("invalid keyword "
                      + pti->key + " for "
                      + parse_tree.begin()->value);
            }
        }
        if (pti->key.compare("") == 0 &&
            last_key.compare("") != 0) {
            error("positional argument after keyword argument");
        }
        last_key = pti->key;
    }
    return opts;
}

void OptionParser::document_values(string argument,
                                   ValueExplanations value_explanations) const {
    DocStore::instance()->add_value_explanations(
        parse_tree.begin()->value,
        argument, value_explanations);
}

void OptionParser::document_synopsis(string name, string note) const {
    DocStore::instance()->set_synopsis(parse_tree.begin()->value,
                                       name, note);
}

void OptionParser::document_property(string property, string note) const {
    DocStore::instance()->add_property(parse_tree.begin()->value,
                                       property, note);
}

void OptionParser::document_language_support(string feature,
                                             string note) const {
    DocStore::instance()->add_feature(parse_tree.begin()->value,
                                      feature, note);
}

void OptionParser::document_note(string name,
                                 string note, bool long_text) const {
    DocStore::instance()->add_note(parse_tree.begin()->value,
                                   name, note, long_text);
}

void OptionParser::document_hide() const {
    DocStore::instance()->hide(parse_tree.begin()->value);
}

bool OptionParser::dry_run() const {
    return dry_run_;
}

bool OptionParser::help_mode() const {
    return help_mode_;
}

void OptionParser::set_parse_tree(const ParseTree &pt) {
    parse_tree = pt;
}

ParseTree *OptionParser::get_parse_tree() {
    return &parse_tree;
}

