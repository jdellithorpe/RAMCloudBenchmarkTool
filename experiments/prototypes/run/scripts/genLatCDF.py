#!/usr/bin/python

import os
import numpy
import sys
import Gnuplot

clientOutputDir = "../client_output/"

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

percentiles = range(1,100)
d = []
for clientTag in clientToLatencyArray.keys():
  for txType in clientToLatencyArray[clientTag].keys():
    if len(clientToLatencyArray[clientTag][txType]) != 0:
      pValues = []
      for p in percentiles:
        pValues.append(numpy.percentile(clientToLatencyArray[clientTag][txType], p))

      d.append(Gnuplot.Data(pValues, percentiles, title=clientTag + "_" + txType, with_="lines"))


g = Gnuplot.Gnuplot()
g.title('CDF of transaction latency')
g.xlabel('latency (us)')
g.ylabel('percentile (%)')
g("set key right bottom Right title \"Legend\"")
g("set terminal pdf dashed font \"Times-Roman,11\"")
g("set output \"lat_cdf.pdf\"")
g.plot(*d)
