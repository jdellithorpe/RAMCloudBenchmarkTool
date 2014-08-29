#!/usr/bin/python

import os
import numpy
import sys
import Gnuplot

clientOutputDir = "../client_output/"

clientToLatencyArray = {}

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

g = Gnuplot.Gnuplot()
g.title('Latency Samples')
g.xlabel('Sample Number')
g.ylabel('Latency (us)')
g('set yrange[0:100]')
g("set key right bottom Right title \"Legend\"")
g("set terminal pdf dashed font \"Times-Roman,11\"")

for clientTag in clientToLatencyArray.keys():
  for txType in clientToLatencyArray[clientTag].keys():
    if len(clientToLatencyArray[clientTag][txType]) != 0: 
      g("set output \"lat_" + clientTag + "_" + txType + ".pdf\"")
      g.plot(clientToLatencyArray[clientTag][txType])
