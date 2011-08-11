#! /usr/bin/env python

import getpass, subprocess, re

import MoinMoin
import xmlrpclib

import markup

if __name__ == '__main__':
    p = subprocess.Popen(["../src/search/downward-1", "--help", "--txt2tags"], stdout=subprocess.PIPE)
    out = p.communicate()[0];
    pagesplitter = re.compile(r'>>>>CATEGORY: ([\w\s]+?)<<<<(.+?)>>>>CATEGORYEND<<<<', re.DOTALL)
    pages = pagesplitter.findall(out);
    name = "MoritzGronbach"
    password = getpass.getpass()
    wikiurl = "http://localhost:8080"
    homewiki = xmlrpclib.ServerProxy(wikiurl + "?action=xmlrpc2", allow_none=True)
    auth_token = homewiki.getAuthToken(name, password)
    mc = xmlrpclib.MultiCall(homewiki)
    mc.applyAuthToken(auth_token)
    for page in pages:
        title = page[0]
        text = "<<TableOfContents>>\n" + page[1]
        doc = markup.Document();
        doc.add_text(text);
        text = doc.render("moin");
        mc.putPage(title, text)
        result = mc()


