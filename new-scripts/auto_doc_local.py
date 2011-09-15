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


def connect():
    wiki = xmlrpclib.ServerProxy(WIKI_URL + "?action=xmlrpc2", allow_none=True)
    auth_token = wiki.getAuthToken(BOT_USERNAME, "geheimeswort")
    multi_call = xmlrpclib.MultiCall(wiki)
    multi_call.applyAuthToken(auth_token)
    return multi_call

def get_all_pages():
    multi_call = connect()
    multi_call.getAllPages()
    result = []
    entry1, entry2 = multi_call()
    return entry2

def send_pages(pages):
    multi_call = connect()
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

def make_link(m):
    s = m.group(0)
    key = s[1:-1]
    result = s[0] + "[[DOC/" + key + "|" + key + "]]" + s[-1]
    return result

def insert_wiki_links(text):
    pages = get_all_pages()
    docpages = [page[4:] for page in pages if page.startswith("DOC/")]
    for key in docpages:
        text = re.sub("\W" + key + "\W", make_link, text)
    return text

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

    #introductions for help pages
    introductions = dict({'Heuristic': """A heuristic specification is either a newly created heuristic instance or a heuristic that has been defined previously. This page describes how one can specify a new heuristic instance. For re-using heuristics, see [[ReusingHeuristics]].
 
Definitions of ''properties'' in the descriptions below:

 * '''admissible:''' h(s) <= h*(s) for all states s
 * '''consistent:''' h(s) + c(s, s') >= h(s') for all states s connected to states s' by an action with cost c(s, s')
 * '''safe:''' h(s) = infinity is only true for states with h*(s) = infinity
 * '''preferred operators:''' this heuristic identifies preferred operators"""})

    #send to wiki:
    pagetitles = [];
    for page in pages:
        title = page[0]
        if(title == "Synergy"):
            title = "LAMAFFSynergy"
        title = "DOC/"+title
        pagetitles.append(title)
        text = page[1]
        text = "<<TableOfContents>>\n" + text
        doc = markup.Document()
        doc.add_text(text)
        text = doc.render("moin")
        text = insert_wiki_links(text)
        if(page[0] in introductions):
            text = introductions[page[0]] + text
        print "updating ", title
        send_pages([(title, text)])
    #update overview page:
    title = "AUTODOCOverview"
    text = "";
    for pagetitle in pagetitles:
        text = text + "\n * [[" + pagetitle + "]]"
    print "updating ", title
    send_pages([(title, text)])

