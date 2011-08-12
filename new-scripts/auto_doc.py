#! /usr/bin/env python

import getpass, subprocess, re

import downward_xmlrpc_test
import markup

if __name__ == '__main__':
    p = subprocess.Popen(["../src/search/downward-1", "--help", "--txt2tags"], stdout=subprocess.PIPE)
    out = p.communicate()[0];
    pagesplitter = re.compile(r'>>>>CATEGORY: ([\w\s]+?)<<<<(.+?)>>>>CATEGORYEND<<<<', re.DOTALL)
    pages = pagesplitter.findall(out);

    categories = dict({'heuristics': 'HeuristicSpecification',
                       'openlists': 'OpenList',
                       'scalar evaluators': 'ScalarEvaluator',
                       'landmark graphs': 'LandmarksDefinition',
                       'search engines' : 'SearchEngine',
                       'synergys' : 'LAMAFFSynergy'})
    introductions = dict({'heuristics': "A heuristic specification is either a newly created heuristic instance or a heuristic that has been defined previously. This page describes how one can specify a new heuristic instance. For re-using heuristics, see ReusingHeuristics."})

    for page in pages:
        title = "AUTODOC"+categories[page[0]]
        text = page[1]
        text = "<<TableOfContents>>\n" + text;
        if(page[0] in introductions):
            text = introductions[page[0]] + text
        doc = markup.Document();
        doc.add_text(text);
        text = doc.render("moin");
        


