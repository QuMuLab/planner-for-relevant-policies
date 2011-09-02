#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from os.path import dirname, join
import sys
import xmlrpclib
import getpass, subprocess, re
import markup


logging.basicConfig(level=logging.INFO, stream=sys.stdout)


BOT_USERNAME = "MoritzGronbach"
WIKI_URL = "http://localhost:8080"


def send_pages(pages):
    wiki = xmlrpclib.ServerProxy(WIKI_URL + "?action=xmlrpc2", allow_none=True)
    auth_token = wiki.getAuthToken(BOT_USERNAME, "geheimeswort")
    multi_call = xmlrpclib.MultiCall(wiki)
    multi_call.applyAuthToken(auth_token)
    for page_name, page_text in pages:
        multi_call.putPage(page_name, page_text)
    try:
        for entry in multi_call():
            logging.info(repr(entry))
    except xmlrpclib.Fault as error:
        print error
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    else:
        print "Update successful"

def insert_wiki_links(text):
    keywords = dict({'shrink strategy' : 'ShrinkStrategies',
                     'heuristic' : 'HeuristicSpecification',
                     'scalar evaluator' : 'ScalarEvaluator'})
    for key, target in keywords.iteritems():
        text = text.replace(key, "[[" + key + "|" + "target" + "]]")

if __name__ == '__main__':
    #update the planner executable if necessary
    build_dir = "../src/search"
    cwd = os.getcwd()
    os.chdir(build_dir)
    os.system("make")
    os.chdir(cwd)

    #retrieve documentation output from the planner
    p = subprocess.Popen(["../src/search/downward-1", "--help", "--txt2tags"], stdout=subprocess.PIPE)
    out = p.communicate()[0]
    
    #split the output into tuples (category, text)
    pagesplitter = re.compile(r'>>>>CATEGORY: ([\w\s]+?)<<<<(.+?)>>>>CATEGORYEND<<<<', re.DOTALL)
    pages = pagesplitter.findall(out)

    #nicer names for the categories
    categories = dict({'heuristics': 'HeuristicSpecification',
                       'openlists': 'OpenList',
                       'scalar evaluators': 'ScalarEvaluator',
                       'landmark graphs': 'LandmarksDefinition',
                       'search engines' : 'SearchEngine',
                       'synergys' : 'LAMAFFSynergy',
                       'shrink strategys' : 'ShrinkStrategies'})
    #introductions for help pages
    introductions = dict({'heuristics': "A heuristic specification is either a newly created heuristic instance or a heuristic that has been defined previously. This page describes how one can specify a new heuristic instance. For re-using heuristics, see ReusingHeuristics."})

    #send to wiki
    for page in pages:
        title = "AUTODOC"+categories[page[0]]
        text = page[1]
        text = "<<TableOfContents>>\n" + text
        if(page[0] in introductions):
            text = introductions[page[0]] + text
        doc = markup.Document()
        doc.add_text(text)
        text = doc.render("moin")
        insert_wiki_links(text)
        print "updating ", title
        send_pages([(title, text)])


