#!/usr/bin/env python
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock

import time

import urllib

def bug_posted(req, result):
   print('gg')

def on_fail(req, res):
    print('failed')

req = UrlRequest('https://www.python.org', on_success=bug_posted, on_failure=on_fail)

