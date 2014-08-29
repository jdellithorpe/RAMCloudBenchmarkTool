#!/usr/bin/python

import os
import numpy
import sys

# arguments
# runTime	
# argv[1]	
runTime = sys.argv[1]

clientOutputDir = "./client_output/"
serverOutputDir = "./server_output/"

cols = ("threads", "tx", "time(s)", "tps", "min", "mean", "max", "std", "99", "99.9", "99.99", "folder")
spaces = 14
formatString = ""
for i in range(0,len(cols)-1):
  formatString += "%"+str(spaces)+"s"
formatString += "%20s"
print formatString % cols


for subDir, dirs, files in os.walk(".."):
  if subDir == "..":
    for expDir in sorted(dirs):
      if expDir[:4] == "run_":
        aggLatencyArray = {"ST": [], "TW": []}

        latFiles = 0
        datFiles = 0
        for file in os.listdir(subDir + "/" + expDir + "/" + clientOutputDir):
          if file[-4:] == ".lat":
            latFiles += 1
            clientTag = file[:7]
            latFile = open(subDir + "/" + expDir + "/" + clientOutputDir + file, 'r')
            # skip the first line (column headers)
            latFile.readline()
            for line in latFile.readlines(): 
              lineParts = line.strip().split()
              userId = lineParts[0]
              txType = lineParts[1]
              latency = float(lineParts[2])
              
              aggLatencyArray[txType].append(latency)
          elif file[-4:] == ".dat":
            datFiles += 1

        # calculate overall statistics for stream transactions
        if len(aggLatencyArray["TW"]) != 0:
          tx = "%s" % len(aggLatencyArray["TW"])
          tps = "%.2f" % (float(tx)/float(runTime))
          min = "%.2f" % numpy.min(aggLatencyArray["TW"])
          mean = "%.2f" % numpy.mean(aggLatencyArray["TW"])
          max = "%.2f" % numpy.max(aggLatencyArray["TW"])
          std = "%.2f" % numpy.std(aggLatencyArray["TW"])
          if hasattr(numpy, "percentile"):
            twonines = "%.2f" % numpy.percentile(aggLatencyArray["TW"], 99.0)
            threenines = "%.2f" % numpy.percentile(aggLatencyArray["TW"], 99.9)
            fournines = "%.2f" % numpy.percentile(aggLatencyArray["TW"], 99.99)
          else:
            twonines = "%.2f" % 0
            threenines = "%.2f" % 0
            fournines = "%.2f" % 0

          print formatString % (datFiles, tx, str(runTime), tps, min, mean, max, std, twonines, threenines, fournines, expDir)
        else:
          print "all: Nothing to summarize..."


