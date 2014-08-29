#!/usr/bin/python

import os
import numpy
import sys

# arguments
# runTime	
# argv[1]	
runTime = sys.argv[1]

clientOutputDir = "../client_output/"
serverOutputDir = "../server_output/"

cols = ("client", "tx", "time(s)", "tps", "min", "mean", "max", "std", "99", "99.9", "99.99")
spaces = 10
formatString = ""
for i in range(0,len(cols)):
  formatString += "%"+str(spaces)+"s"

clientToLatencyArray = {}
aggLatencyArray = {"ST": [], "TW": []}

for file in os.listdir(clientOutputDir):
  if file[-4:] == ".lat":
    clientTag = file[:7]
    clientToLatencyArray[clientTag] = {"ST": [], "TW": []}
    latFile = open(clientOutputDir + file, 'r')
    # skip the first line (column headers)
    latFile.readline()
    for line in latFile.readlines(): 
      lineParts = line.strip().split()
      userId = lineParts[0]
      txType = lineParts[1]
      latency = float(lineParts[2])
      
      clientToLatencyArray[clientTag][txType].append(latency)
      aggLatencyArray[txType].append(latency)

print "Stream Transaction Statistics:\n"
print formatString % cols
for clientTag in clientToLatencyArray.keys():
  if len(clientToLatencyArray[clientTag]["ST"]) != 0:
    tx = "%s" % len(clientToLatencyArray[clientTag]["ST"])
    tps = "%.2f" % (float(tx)/float(runTime))
    min = "%.2f" % numpy.min(clientToLatencyArray[clientTag]["ST"])
    mean = "%.2f" % numpy.mean(clientToLatencyArray[clientTag]["ST"])
    max = "%.2f" % numpy.max(clientToLatencyArray[clientTag]["ST"])
    std = "%.2f" % numpy.std(clientToLatencyArray[clientTag]["ST"])
    if hasattr(numpy, "percentile"):
      twonines = "%.2f" % numpy.percentile(clientToLatencyArray[clientTag]["ST"], 99.0)
      threenines = "%.2f" % numpy.percentile(clientToLatencyArray[clientTag]["ST"], 99.9)
      fournines = "%.2f" % numpy.percentile(clientToLatencyArray[clientTag]["ST"], 99.99)
    else:
      twonines = "%.2f" % 0
      threenines = "%.2f" % 0
      fournines = "%.2f" % 0
  
    print formatString % (clientTag, tx, str(runTime), tps, min, mean, max, std, twonines, threenines, fournines)

  else:
    print clientTag + ": No measurements for this client"
 
# calculate overall statistics for stream transactions
if len(aggLatencyArray["ST"]) != 0:
  tx = "%s" % len(aggLatencyArray["ST"])
  tps = "%.2f" % (float(tx)/float(runTime))
  min = "%.2f" % numpy.min(aggLatencyArray["ST"])
  mean = "%.2f" % numpy.mean(aggLatencyArray["ST"])
  max = "%.2f" % numpy.max(aggLatencyArray["ST"])
  std = "%.2f" % numpy.std(aggLatencyArray["ST"])
  if hasattr(numpy, "percentile"):
    twonines = "%.2f" % numpy.percentile(aggLatencyArray["ST"], 99.0)
    threenines = "%.2f" % numpy.percentile(aggLatencyArray["ST"], 99.9)
    fournines = "%.2f" % numpy.percentile(aggLatencyArray["ST"], 99.99)
  else:
    twonines = "%.2f" % 0
    threenines = "%.2f" % 0
    fournines = "%.2f" % 0

  print formatString % ("all", tx, str(runTime), tps, min, mean, max, std, twonines, threenines, fournines)
else:
  print "all: Nothing to summarize..."

print ""
print "Tweet Transaction Statistics:\n"
print formatString % cols
for clientTag in clientToLatencyArray.keys():
  if len(clientToLatencyArray[clientTag]["TW"]) != 0:
    tx = "%s" % len(clientToLatencyArray[clientTag]["TW"])
    tps = "%.2f" % (float(tx)/float(runTime))
    min = "%.2f" % numpy.min(clientToLatencyArray[clientTag]["TW"])
    mean = "%.2f" % numpy.mean(clientToLatencyArray[clientTag]["TW"])
    max = "%.2f" % numpy.max(clientToLatencyArray[clientTag]["TW"])
    std = "%.2f" % numpy.std(clientToLatencyArray[clientTag]["TW"])
    if hasattr(numpy, "percentile"):
      twonines = "%.2f" % numpy.percentile(clientToLatencyArray[clientTag]["TW"], 99.0)
      threenines = "%.2f" % numpy.percentile(clientToLatencyArray[clientTag]["TW"], 99.9)
      fournines = "%.2f" % numpy.percentile(clientToLatencyArray[clientTag]["TW"], 99.99)
    else:
      twonines = "%.2f" % 0
      threenines = "%.2f" % 0
      fournines = "%.2f" % 0

    
    print formatString % (clientTag, tx, str(runTime), tps, min, mean, max, std, twonines, threenines, fournines)

  else:
    print clientTag + ": No measurements for this client"
 
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

  print formatString % ("all", tx, str(runTime), tps, min, mean, max, std, twonines, threenines, fournines)
else:
  print "all: Nothing to summarize..."
