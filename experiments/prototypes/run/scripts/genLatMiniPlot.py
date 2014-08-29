#!/usr/bin/python

import os
import numpy
import sys
import Gnuplot

clientOutputDir = "../client_output/"

clientToLatencyArray = {}

for file in os.listdir(clientOutputDir):
  if file[-5:] == ".mini":
    clientTag = file[:7]
    clientToLatencyArray[clientTag] = []
    latFile = open(clientOutputDir + file, 'r')
    # skip the first line (column headers)
    latFile.readline()
    for line in latFile.readlines():
      lineParts = line.strip().split()
      latency = float(lineParts[3])

      clientToLatencyArray[clientTag].append(latency)

g = Gnuplot.Gnuplot()
g.title('Latency Samples')
g.xlabel('Sample Number')
g.ylabel('Latency (ms)')
g('set yrange[0:6]')
g('set xtics scale 10.0,5.0')
g('set grid')
g("set key right bottom Right title \"Legend\"")
g("set terminal pdf dashed font \"Times-Roman,11\"")

for clientTag in clientToLatencyArray.keys():
  if len(clientToLatencyArray[clientTag]) != 0: 
    g("set output \"lat_" + clientTag + "_mini.pdf\"")
    g.plot(clientToLatencyArray[clientTag])
