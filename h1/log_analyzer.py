#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gzip
import glob
import os
import time
import re
import argparse
import json
from datetime import datetime
from dateutil import parser
from pathlib import Path
from collections import OrderedDict
from string import Template
import logging
import sys
import traceback
import mmap


class LogAnalyzer:
   config = {
       "REPORT_SIZE": 1000,
       "REPORT_DIR": "./reports",
       "INPUTLOG_DIR": "./input",
       "LOG_DIR": "./log",
       "LOG_FILE": "loganalyzer",
       "LOG_LEVEL": "DEBUG"
   }

   class ReportItem:
      """
      report item element with nginx requests statistical info

      """
      def  __init__(self):
         self.id = None
         self.url = None
         self.count = None
         self.time_avg = None
         self.time_max = None
         self.time_sum = None
         self.time_med = None
         self.time_perc = None
         self.count_perc = None
   
   def setlogger(self,config):
      """
      set logger parameters

      """
      if config["LOG_LEVEL"] == "INFO":
         loglev = "INFO"
      elif config["LOG_LEVEL"] == "DEBUG":
         loglev = logging.DEBUG
      elif config["LOG_LEVEL"] == "ERROR":
         loglev = logging.ERROR

      file_handler = logging.FileHandler("{0}/{1}.log".format(config["LOG_DIR"],config["LOG_FILE"]))
      stdout_handler = logging.StreamHandler(stream=sys.stdout)
      if config["LOG_FILE"]:
         handlers = [file_handler, stdout_handler]
      else:
         handlers = [stdout_handler]
      logging.basicConfig(
         level=loglev,
         format="%(asctime)s [%(levelname)s] %(message)s",
         handlers=handlers
      )

   def tmstart(self):
       """
       start timer

       """
       global _start_time 
       _start_time = time.time()
   
   def tmstop(self):
       """
       get execution passed time

       """
       t_sec = round(time.time() - _start_time)
       (t_min, t_sec) = divmod(t_sec,60)
       (t_hour,t_min) = divmod(t_min,60) 
       print('Time passed: {}min:{}sec'.format(int(t_min),int(t_sec)))
   
   
   def inputarg(self):
       """
       input command-line arguments

       returns: config file
       """
       config_file = None
       parser = argparse.ArgumentParser(description='This program analyzes nginx logs and outputs reports with statistical info')
       parser.add_argument('-c','--config',help='config file path',required=False)
      
       args = parser.parse_args()
       configpath = args.config
   
       if configpath is not None:
         config_file = Path(configpath)
         if config_file.is_file():
            #logging.info(f"arg config file {config_file} exists")
            return config_file
         else:
            logging.warning(f'Input configuration file {config_file} does not exist')
       return None


   def getconfig(self):
      """
      get config settings

      """
      input_file = self.inputarg()

      if input_file:
         config_file = input_file
      elif Path("./config").is_file():
         config_file = Path("./config")
      else:
         logging.info("No config file provided. Using next default values defined in program:\n")
         for k,v in self.config.items():
           print(f"{k}:{v}")
         print("\n",end='')
         return
      d = {}
      with open(config_file,'r') as f:
         for line in f:
            tpl = line.split(':')
            tpl[0] = tpl[0].strip().strip('"')
            tpl[1] = tpl[1].strip().strip('"')
            d[tpl[0]] = tpl[1]
      #print('\n')
      for k, v in d.items():
         for k2, v2 in self.config.items():
            if k == k2:
               self.config[k2]=v
      logging.info(f"Config file provided is: {config_file}. Using next values from it:\n")
      for k,v in self.config.items():
         print(f"{k}:{v}")
      print("\n",end='')


   def getlatestlog(self,config):
      """
      search for latest log file

      param: config dict
      returns: latestlog
      """

      list_of_files = glob.glob(config["INPUTLOG_DIR"] + "/*")

      filedt = datetime.strptime('19700101','%Y%m%d')
      for s in list_of_files:
         filename = s.split('/')[2]
         if "nginx" in filename:
            match = re.search('\d{8}', s)
            dt = match.group(0)
            dt_obj = parser.parse(dt)
            if filedt < dt_obj:
               filedt = dt_obj
               latestlog = s

      logging.info(f"filedt={filedt}, latestlog={latestlog}")

      return latestlog
   


   def getlinelist(self,config):
      """
      get list of lines

      param: config dict
      returns: linelist
      """
      logfile = self.getlatestlog(self.config)
      opener = gzip.open if ".gz" in logfile else open
      cnt = 0
      linelist, wordlist = [], []
      
      try:
         with opener(logfile,'r') as file1:
            logging.info("Processing data...")
            for line in file1:
               cnt+=1
               wordlist = line.split()
               linelist.append(wordlist)            
      except (FileNotFoundError, PermissionError, OSError):
          logging.exception(f"Error opening file {file1}")

      return linelist


   def getreportlist(self,config):
      """
      get list of reports

      param: config dict
      returns: reportlist
      """
      urldict = {}
      urllist = []
      maxtimedict = {}
      timesumdict = {}
      avgtimedict = {}
      timedict = {}   

      linelist = []
      linelist = self.getlinelist(self.config)

      allreqcnt = 0
      alltime = 0

      for el in linelist:
         if "GET" in str(el):
           allreqcnt += 1

           for el2 in el:
             if el2.startswith(b'/api'):
                alltime += float(el[-1])
                urllist.append(el2)
                if el2 not in urldict:
                   urldict[el2] = 1
                else:
                   urldict[el2] += 1
                if el2 not in timesumdict:
                   timesumdict[el2] = float(el[-1])
                else:
                   timesumdict[el2] += float(el[-1])
                if el2 not in maxtimedict:
                   maxtimedict[el2] = float(el[-1])
                else:
                   if maxtimedict[el2] < float(el[-1]):
                      maxtimedict[el2] = float(el[-1])
                if el2 not in timedict:
                   timedict[el2] = el[-1].decode("utf-8") + '\t'
                else:
                   timedict[el2] = timedict[el2] + '\t' + el[-1].decode("utf-8")   

      cnt1=0
      reportlist = []

      for url,urlcnt in urldict.items():
            cnt1+=1
            avgtimedict[url] = timesumdict[url]/float(urlcnt)
            countperc = (urlcnt/allreqcnt)*100
            timeperc = (timesumdict[url]/alltime)*100 
            timelist = []
            timelist = timedict[url].split()
            timelistlen = len(timelist)
            med = 0
            if timelistlen % 2 == 1:
               med = timelist[int(timelistlen/2)]
            else:
               med = (float(timelist[int(timelistlen/2)-1]) + float(timelist[int(timelistlen/2)]))/2
   
            r = self.ReportItem()
            r.id = cnt1
            r.count = urlcnt
            r.url = url.decode("utf-8")
            r.time_avg = round(avgtimedict[url],3)
            r.time_max = maxtimedict[url]
            r.time_sum = round(timesumdict[url],3)
            r.time_med = med
            r.time_perc = round(timeperc,3)
            r.count_perc = round(countperc,3)
            reportlist.append(r)
   
      return reportlist
   
   def createjson(self, config):
      """
      create json string

      param: config dict
      returns: jsonstr
      """
      rlist = self.getreportlist(config)
      cnt11=0
      dict1 = ()
      jsonstr = json.dumps(dict1,ensure_ascii=False)
      jsonobj = json.loads(jsonstr)
   
      for i in rlist:
         cnt11 += 1
         a1 = (("id",str(i.id)),("count",str(i.count)),("time_avg",str(i.time_avg)),("time_max",str(i.time_max)),\
         ("time_sum",str(i.time_sum)),("url",str(i.url)),\
         ("time_med",str(i.time_med)),("time_perc",str(i.time_perc)),("count_perc",str(i.count_perc)))
         b1 = OrderedDict(a1)
         jsonobj.append(b1)
      jsonstr = json.dumps(jsonobj,ensure_ascii=False,indent=None,separators=(',',':'))

      return jsonstr
   
   
   def isjsonwritten(self, resfile):
      with open(resfile,'r') as f:
         s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
         if s.find(b'table = [{') != -1:
             logging.info(f"json statistical data is successfully written to file {resfile}")
             return True
         else:
             return False

   def makereport(self, jsonstr, resfile):
      """
      make report file

      params: json string, resfile path
      """
      templfile = "./report.html"
      with open(templfile, 'r+') as f:
         temp = Template(f.read())
         res = temp.safe_substitute(table_json=jsonstr)
   
      with open(resfile,'w') as f:
         f.write(res)
      return self.isjsonwritten(resfile)


def main():
   la = LogAnalyzer()
   la.tmstart()
   try:
      la.setlogger(la.config)
      la.getconfig()
      currdir = os.getcwd()

      logdir = os.path.join(currdir, la.config["LOG_DIR"])
      reportdir = os.path.join(currdir, la.config["REPORT_DIR"])

      os.makedirs(logdir, exist_ok=True)
      os.makedirs(reportdir, exist_ok=True)

      ts = str(datetime.now().strftime("%Y_%m_%d_%H%M%S"))
      resfile = la.config["REPORT_DIR"] + "/report_" + ts +".html"

      if os.path.exists(resfile):
         os.remove(resfile)
      jsonstr = la.createjson(la.config)
      logging.info
      if la.makereport(jsonstr,resfile):
          logging.info("Successfully finished")
      la.tmstop()


   except Exception:
      ex_str = traceback.format_exc()
      logging.exception(f'Exception occured: {ex_str}')


if __name__ == "__main__":
   try:
      main()

   except KeyboardInterrupt:
        print('\ninterrupted')
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)
