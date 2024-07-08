#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest, mmap
from log_analyzer import *

class TestLogAnalyzer(unittest.TestCase):
   def setUp(self):
      self.la = LogAnalyzer()

   def test_parselog(self):
      rplist = self.la.parselog(self.la.config)
      self.assertTrue(type(rplist) is list)
      self.assertTrue(len(rplist) > 0)
      self.assertTrue(rplist[0].time_avg < rplist[0].time_max)
      self.assertTrue(rplist[0].time_med < rplist[0].time_max)

   def isjson(self,jstr):
      try:
         json.loads(jstr)
      except ValueError as e:
         return False
      return True

   def test_createjson(self):
      jsonstr = self.la.createjson(self.la.config)
      self.assertTrue(self.isjson(jsonstr))

   def isjsonwritten(self, resfile):
      with open(resfile,'r') as f:
         s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
         if s.find(b'table = [{') != -1:
             print('true')
             return True
         else:
             return False

   def test_makereport(self):
      jsonstr = self.la.createjson(self.la.config)
      resfilepath = self.la.config["REPORT_DIR"] + "/report.html"
      resfile = Path(resfilepath)

      self.la.makereport(jsonstr,resfile)
      self.assertTrue(os.path.exists(resfile))
      self.assertTrue(resfile.is_file())
      self.assertTrue(self.isjsonwritten(resfile))

if __name__ == "__main__":
    unittest.main()
