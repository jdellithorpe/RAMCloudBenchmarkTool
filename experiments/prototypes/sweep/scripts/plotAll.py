#!/usr/bin/python

import os
import Gnuplot
import re
from operator import attrgetter
import itertools

class DataPoint:
  def __init__(self):
    pass
  def __repr__(self):
    return self.__dict__.__str__()

dataPoints = []

runDirs = [os.path.join('..',d) for d in os.listdir('..')
                if os.path.isdir(os.path.join('..',d)) 
                if d[:4] == 'run_']

with open('index.txt', 'w') as indexFile:
  indexFile.write('%25s '   # runDir
                  '%7s'     # repeatNumber
                  '%7s'     # numMasters
                  '%7s'     # replicas
                  '%7s'     # tableServerSpan
                  '%7s'     # numObjects
                  '%7s'     # keySize
                  '%7s'     # objectSize
                  '%7s'     # runTime
                  '%7s'     # opType
                  '%7s'     # MultiOpSize
                  '%7s'     # numClientHosts
                  '%7s'     # numThreads
                  '%7s'     # opTPS
                  '%7s'     # avgOpLatency
                  '\n' %
                  ( "dir",
                    "rep",
                    "mast",
                    "repl",
                    "ss",
                    "nobj",
                    "keyS",
                    "objS",
                    "time",
                    "op",
                    "mopS",
                    "ncli",
                    "nthds",
                    "tps",
                    "lat"
                    ))
  for runDir in runDirs:
    paramRepeatNumber = None
    paramNumMasters = None
    paramReplicas = None
    paramTableServerSpan = None
    paramNumObjects = None
    paramKeySize = None
    paramObjectSize = None
    paramRunTime = None
    paramOpType = None
    paramMultiOpSize = None
    paramNumClientHosts = None
    paramNumThreads = None
    with open(os.path.join(runDir,'parameters.txt')) as f:
      for line in f.readlines():
        if re.search(r'repeatNumber', line):
          m = re.search(r'[0-9]+', line)
          if m:
            paramRepeatNumber = int(m.group())
        elif re.search(r'numMasters', line):
          m = re.search(r'[0-9]+', line)
          if m:
            paramNumMasters = int(m.group())
        elif re.search(r'replicas', line):
          m = re.search(r'[0-9]+', line)
          if m:
            paramReplicas = int(m.group())
        elif re.search(r'tableServerSpan', line):
          m = re.search(r'[0-9]+', line)
          if m:
            paramTableServerSpan = int(m.group())
        elif re.search(r'numObjects', line):
          m = re.search(r'[0-9]+', line)
          if m:
            paramNumObjects = int(m.group())
        elif re.search(r'keySize', line):
          m = re.search(r'[0-9]+', line)
          if m:
            paramKeySize = int(m.group())
        elif re.search(r'objectSize', line):
          m = re.search(r'[0-9]+', line)
          if m:
            paramObjectSize = int(m.group())
        elif re.search(r'runTime', line):
          m = re.search(r'[0-9]+\.[0-9]+', line)
          if m:
            paramRunTime = float(m.group())
        elif re.search(r'opType', line):
          lineParts = line.strip().split(':')
          m = re.search(r'[A-Z]+', lineParts[1])
          if m:
            paramOpType = m.group()
        elif re.search(r'multiOpSize', line):
          m = re.search(r'[0-9]+', line)
          if m:
            paramMultiOpSize = int(m.group())
        elif re.search(r'numClientHosts', line):
          m = re.search(r'[0-9]+', line)
          if m:
            paramNumClientHosts = int(m.group())
        elif re.search(r'numThreads', line):
          m = re.search(r'[0-9]+', line)
          if m:
            paramNumThreads = int(m.group())

    if  paramRepeatNumber == None or \
        paramNumMasters == None or \
        paramReplicas == None or \
        paramTableServerSpan == None or \
        paramNumObjects == None or \
        paramKeySize == None or \
        paramObjectSize == None or \
        paramRunTime == None or \
        paramOpType == None or \
        paramMultiOpSize == None or \
        paramNumClientHosts == None or \
        paramNumThreads == None:
      print runDir + ': could not parse parameter file'
      quit()
       
    datFileDir = os.path.join(runDir,'client_output')
    datFiles = [os.path.join(datFileDir,f) for f in os.listdir(datFileDir)
                if f[-4:] == '.dat']

    totalOpCount = 0
    totalOpTime = 0

    for datFile in datFiles:
      opCount = None
      avgOpLatency = None
      with open(datFile, 'r') as f:
        for line in f.readlines():
          lineParts = line.strip().split(':')
          subLineParts = lineParts[1].strip().split(' ')
          
          if lineParts[0].strip() == "OP COUNT":
            opCount = int(lineParts[1])
          if lineParts[0].strip() == "AVERAGE OP LATENCY (us)":
            avgOpLatency = float(lineParts[1])

      totalOpCount += opCount
      totalOpTime += float(opCount)*avgOpLatency

    dp = DataPoint()
   
    # independent variables 
    dp.repeatNumber = paramRepeatNumber
    dp.numMasters = paramNumMasters
    dp.replicas = paramReplicas
    dp.tableServerSpan = paramTableServerSpan
    dp.numObjects = paramNumObjects
    dp.keySize = paramKeySize
    dp.objectSize = paramObjectSize
    dp.runTime = paramRunTime
    dp.opType = paramOpType
    dp.multiOpSize = paramMultiOpSize
    dp.numClientHosts = paramNumClientHosts
    dp.numThreads = paramNumThreads

    # dependent variables
    if totalOpCount > 0: 
      dp.opTPS = float(totalOpCount)/paramRunTime
      dp.avgOpLatency = totalOpTime/float(totalOpCount)
    else:
      dp.opTPS = 0.0
      dp.avgOpLatency = 0.0
       
    dataPoints.append(dp)
                  
    indexFile.write('%25s '   # runDir
                    '%7d'     # repeatNumber
                    '%7d'     # numMasters
                    '%7d'     # replicas
                    '%7d'     # tableServerSpan
                    '%7d'     # numObjects
                    '%7d'     # keySize
                    '%7d'     # objectSize
                    '%7.1f'   # runTime
                    '%7s'     # opType
                    '%7d'     # MultiOpSize
                    '%7d'     # numClientHosts
                    '%7d'     # numThreads
                    '%10.1f'  # opTPS
                    '%10.1f'  # avgOpLatency
                    '\n' %
                    ( runDir,
                      dp.repeatNumber,
                      dp.numMasters,
                      dp.replicas,
                      dp.tableServerSpan,
                      dp.numObjects,
                      dp.keySize,
                      dp.objectSize,
                      dp.runTime,
                      dp.opType,
                      dp.multiOpSize,
                      dp.numClientHosts,
                      dp.numThreads,
                      dp.opTPS,
                      dp.avgOpLatency
                      ))

if len(runDirs) != len(dataPoints):
  print 'Had %d runs but collected only %d datapoints' % (len(runDirs), len(dataPoints))
  quit()

g = Gnuplot.Gnuplot()

dataPoints = sorted(dataPoints, key=attrgetter('repeatNumber', 'numMasters', 'replicas', 'tableServerSpan', 'numObjects', 'keySize', 'objectSize', 'runTime', 'opType', 'multiOpSize', 'numClientHosts', 'numThreads'))

opTPSPlots = []
opLatencyPlots = []
for key, group in itertools.groupby(dataPoints, attrgetter('repeatNumber', 'numMasters', 'replicas', 'tableServerSpan', 'numObjects', 'keySize', 'objectSize', 'runTime', 'opType', 'multiOpSize', 'numClientHosts')):
  numThreads = []
  opTPS = []
  opLatency = []
  for dp in group:
    numThreads.append(dp.numThreads)
    opTPS.append(dp.opTPS)
    opLatency.append(dp.avgOpLatency)

  opTPSPlots.append(Gnuplot.Data(numThreads, opTPS, with_="lines", title=str(key)))
 
  g.title('Ops per Second vs. Workload Threads ' + str(key))
  g.xlabel('Workload Threads')
  g.ylabel('Ops per Second')
  g('set yrange [0:*]')
  g('set xrange [1:*]')
  g('set grid')
  g('set terminal pdf dashed font \"Times-Roman,8\"')
  g('set output \"tps' + str(key) + '.pdf\"')
  g.plot(opTPSPlots[-1])

  g('reset')

  opLatencyPlots.append(Gnuplot.Data(numThreads, opLatency, with_="lines", title=str(key)))  

  g.title('Op Latency vs. Workload Threads ' + str(key))
  g.xlabel('Workload Threads')
  g.ylabel('Latency (us)')
  g('set yrange [0:*]')
  g('set xrange [1:*]')
  g('set grid')
  g('set key left top Right title \"Legend\"')
  g('set terminal pdf dashed font \"Times-Roman,8\"')
  g('set output \"latency' + str(key) + '.pdf\"')
  g.plot(opLatencyPlots[-1]) 

  g('reset')


g.title('Ops per Second vs. Workload Threads')
g.xlabel('Workload Threads')
g.ylabel('Ops per Second')
g('set yrange [0:*]')
g('set xrange [1:*]')
g('set grid')
g('set terminal pdf dashed font \"Times-Roman,8\"')
g('set output \"tps.pdf\"')
g.plot(*opTPSPlots)

g('reset')

g.title('Op Latency vs. Workload Threads')
g.xlabel('Workload Threads')
g.ylabel('Latency (us)')
g('set yrange [0:*]')
g('set xrange [1:*]')
g('set grid')
g('set key left top Right title \"Legend\"')
g('set terminal pdf dashed font \"Times-Roman,8\"')
g('set output \"latency.pdf\"')
g.plot(*opLatencyPlots)

