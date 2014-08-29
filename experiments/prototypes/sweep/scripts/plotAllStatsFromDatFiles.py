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
                  '%7s' # runTime
                  '%7s'   # replicas
                  '%7s'   # numMasters
                  '%7s'   # repeatNumber
                  '%7s' # streamProb
                  '%7s'   # numThreads
                  '%7s'   # numClientHosts
                  '%7s'   # streamTPS
                  '%10s' # avgStreamTxTime
                  '%7s'   # tweetTPS
                  '%10s' # avgTweetTxTime
                  '\n' %
                  ( "dir",
                    "time",
                    "repl",
                    "mast",
                    "rep",
                    "sprob",
                    "thds",
                    "clie",
                    "stps",
                    "slat",
                    "ttps",
                    "tlat"
                    ))
  for runDir in runDirs:
    paramRunTime = None
    paramNumThreads = None
    paramReplicas = None
    paramNumMasters = None
    paramNumClientHosts = None
    paramRepeatNumber = None
    paramStreamProb = None
    with open(os.path.join(runDir,'parameters.txt')) as f:
      for line in f.readlines():
        if re.search(r'runTime', line):
          m = re.search(r'[0-9]+\.[0-9]+', line)
          if m:
            paramRunTime = float(m.group())*60.0
        elif re.search(r'numThreads', line):
          m = re.search(r'[0-9]+', line)
          if m:
            paramNumThreads = int(m.group())
        elif re.search(r'replicas', line):
          m = re.search(r'[0-9]+', line)
          if m:
            paramReplicas = int(m.group())
        elif re.search(r'numMasters', line):
          m = re.search(r'[0-9]+', line)
          if m:
            paramNumMasters = int(m.group())
        elif re.search(r'numClientHosts', line):
          m = re.search(r'[0-9]+', line)
          if m:
            paramNumClientHosts = int(m.group())
        elif re.search(r'repeatNumber', line):
          m = re.search(r'[0-9]+', line)
          if m:
            paramRepeatNumber = int(m.group())
        elif re.search(r'streamProb', line):
          m = re.search(r'[0-9]+\.[0-9]+', line)
          if m:
            paramStreamProb = float(m.group())
       
    if  paramRunTime != None and \
        paramNumThreads != None and \
        paramReplicas != None and \
        paramNumMasters != None and \
        paramNumClientHosts != None and \
        paramStreamProb != None and \
        paramRepeatNumber != None:
      pass
    else:
      print runDir + ': could not parse parameter file'
      quit()

    datFileDir = os.path.join(runDir,'client_output')
    datFiles = [os.path.join(datFileDir,f) for f in os.listdir(datFileDir)
                if f[-4:] == '.dat']

    totalStreamUpdateFailures = 0
    totalStreamTx = 0
    totalStreamTxTime = 0.0
    totalRdUserIDStreamTime = 0.0
    totalMultiRdTweetDataTime = 0.0
    totalTweetTx = 0
    totalTweetTxTime = 0.0
    totalIncTweetIDTime = 0.0
    totalWrTweetIDDataTime = 0.0
    totalRdUserIDTweetsTime = 0.0
    totalWrUserIDTweetsTime = 0.0
    totalRdUserIDFollowersTime = 0.0
    totalMultiRdUserIDStreamTime = 0.0
    totalMultiWrUserIDStreamTime = 0.0

    for datFile in datFiles:
      streamUpdateFailures = None
      streamTx = None
      avgStreamTxTime = None
      avgRdUserIDStreamTime = None
      avgMultiRdTweetDataTime = None
      tweetTx = None
      avgTweetTxTime = None
      avgIncTweetIDTime = None
      avgWrTweetIDDataTime = None
      avgRdUserIDTweetsTime = None
      avgWrUserIDTweetsTime = None
      avgRdUserIDFollowersTime = None
      avgMultiRdUserIDStreamTime = None
      avgMultiWrUserIDStreamTime = None
      with open(datFile, 'r') as f:
        for line in f.readlines():
          lineParts = line.strip().split(':')
          subLineParts = lineParts[1].strip().split(' ')
          
          if lineParts[0].strip() == "RUNTIME":
            pass
          if lineParts[0].strip() == "STREAM UPDATE FAILURES":
            streamUpdateFailures = int(lineParts[1])
          if lineParts[0].strip() == "STREAM TRANSACTIONS":
            streamTx = int(lineParts[1])
          if lineParts[0].strip() == "AVERAGE STREAM TX TIME":
            avgStreamTxTime = float(lineParts[1][:-2])
          if lineParts[0].strip() == "AVERAGE READ USERID STREAM":
            avgRdUserIDStreamTime = float(subLineParts[0][:-2]) 
          if lineParts[0].strip() == "AVERAGE MULTIREAD TWEET DATA":
            avgMultiRdTweetDataTime = float(subLineParts[0][:-2]) 
          if lineParts[0].strip() == "TWEET TRANSACTIONS":
            tweetTx = int(lineParts[1])
          if lineParts[0].strip() == "AVERAGE TWEET TX TIME":
            avgTweetTxTime = float(lineParts[1][:-2]) 
          if lineParts[0].strip() == "AVERAGE INCREMENT TWEETID":
            avgIncTweetIDTime = float(lineParts[1][:-2]) 
          if lineParts[0].strip() == "AVERAGE WRITE TWEETID DATA":
            avgWrTweetIDDataTime = float(subLineParts[0][:-2]) 
          if lineParts[0].strip() == "AVERAGE READ USERID TWEETS":
            avgRdUserIDTweetsTime = float(subLineParts[0][:-2]) 
          if lineParts[0].strip() == "AVERAGE WRITE USERID TWEETS":
            avgWrUserIDTweetsTime = float(subLineParts[0][:-2]) 
          if lineParts[0].strip() == "AVERAGE READ USERID FOLLOWERS":
            avgRdUserIDFollowersTime = float(subLineParts[0][:-2]) 
          if lineParts[0].strip() == "AVERAGE MULTIREAD USERID STREAM":
            avgMultiRdUserIDStreamTime = float(subLineParts[0][:-2]) 
          if lineParts[0].strip() == "AVERAGE MULTIWRITE USERID STREAM":
            avgMultiWrUserIDStreamTime = float(subLineParts[0][:-2]) 
      
      totalStreamUpdateFailures += streamUpdateFailures
      totalStreamTx += streamTx
      totalStreamTxTime += float(streamTx)*avgStreamTxTime
      totalRdUserIDStreamTime += float(streamTx)*avgRdUserIDStreamTime
      totalMultiRdTweetDataTime += float(streamTx)*avgMultiRdTweetDataTime
      totalTweetTx += tweetTx
      totalTweetTxTime += float(tweetTx)*avgTweetTxTime
      totalIncTweetIDTime += float(tweetTx)*avgIncTweetIDTime
      totalWrTweetIDDataTime += float(tweetTx)*avgWrTweetIDDataTime
      totalRdUserIDTweetsTime += float(tweetTx)*avgRdUserIDTweetsTime
      totalWrUserIDTweetsTime += float(tweetTx)*avgWrUserIDTweetsTime
      totalRdUserIDFollowersTime += float(tweetTx)*avgRdUserIDFollowersTime
      totalMultiRdUserIDStreamTime += float(tweetTx)*avgMultiRdUserIDStreamTime
      totalMultiWrUserIDStreamTime += float(tweetTx)*avgMultiWrUserIDStreamTime

    dp = DataPoint()
   
    # independent variables 
    dp.threads = paramNumThreads
    dp.runTime = paramRunTime
    dp.replicas = paramReplicas
    dp.numMasters = paramNumMasters
    dp.numClientHosts = paramNumClientHosts
    dp.repeatNumber = paramRepeatNumber
    dp.streamProb = paramStreamProb

    # dependent variables
    if totalStreamTx > 0: 
      dp.streamTPS = float(totalStreamTx)/paramRunTime
      dp.avgStreamTxTime = totalStreamTxTime/float(totalStreamTx)
      dp.avgRdUserIDStreamTime = totalRdUserIDStreamTime/float(totalStreamTx)
      dp.avgMultiRdTweetDataTime = totalMultiRdTweetDataTime/float(totalStreamTx)
    else:
      dp.streamTPS = 0.0
      dp.avgStreamTxTime = 0.0
      dp.avgRdUserIDStreamTime = 0.0
      dp.avgMultiRdTweetDataTime = 0.0
       
    if totalTweetTx > 0:
      dp.tweetTPS = float(totalTweetTx)/paramRunTime
      dp.avgTweetTxTime = totalTweetTxTime/float(totalTweetTx)
      dp.avgIncTweetIDTime = totalIncTweetIDTime/float(totalTweetTx)
      dp.avgWrTweetIDDataTime = totalWrTweetIDDataTime/float(totalTweetTx)
      dp.avgRdUserIDTweetsTime = totalRdUserIDTweetsTime/float(totalTweetTx)
      dp.avgWrUserIDTweetsTime = totalWrUserIDTweetsTime/float(totalTweetTx)
      dp.avgRdUserIDFollowersTime = totalRdUserIDFollowersTime/float(totalTweetTx)
      dp.avgMultiRdUserIDStreamTime = totalMultiRdUserIDStreamTime/float(totalTweetTx)
      dp.avgMultiWrUserIDStreamTime = totalMultiWrUserIDStreamTime/float(totalTweetTx)
    else:
      dp.tweetTPS = 0.0
      dp.avgTweetTxTime = 0.0
      dp.avgIncTweetIDTime = 0.0
      dp.avgWrTweetIDDataTime = 0.0
      dp.avgRdUserIDTweetsTime = 0.0
      dp.avgWrUserIDTweetsTime = 0.0
      dp.avgRdUserIDFollowersTime = 0.0
      dp.avgMultiRdUserIDStreamTime = 0.0
      dp.avgMultiWrUserIDStreamTime = 0.0

    dataPoints.append(dp)
                  
    indexFile.write('%25s '   # runDir
                    '%7.1f' # runTime
                    '%7d'   # replicas
                    '%7d'   # numMasters
                    '%7d'   # repeatNumber
                    '%7.1f' # streamProb
                    '%7d'   # numThreads
                    '%7d'   # numClientHosts
                    '%7d'   # streamTPS
                    '%10.1f' # avgStreamTxTime
                    '%7d'   # tweetTPS
                    '%10.1f' # avgTweetTxTime
                    '\n' %
                    ( runDir,
                      dp.runTime,
                      dp.replicas,
                      dp.numMasters,
                      dp.repeatNumber,
                      dp.streamProb,
                      dp.threads,
                      dp.numClientHosts,
                      dp.streamTPS,
                      dp.avgStreamTxTime,
                      dp.tweetTPS,
                      dp.avgTweetTxTime
                      ))

if len(runDirs) != len(dataPoints):
  print 'Had %d runs but collected only %d datapoints' % (len(runDirs), len(dataPoints))
  quit()

g = Gnuplot.Gnuplot()

dataPoints = sorted(dataPoints, key=attrgetter('runTime', 'replicas', 'numMasters', 'numClientHosts', 'repeatNumber', 'streamProb', 'threads'))

streamTPSPlots = []
tweetTPSPlots = []
streamLatencyPlots = []
tweetLatencyPlots = []
for key, group in itertools.groupby(dataPoints, attrgetter('runTime', 'replicas', 'numMasters', 'numClientHosts', 'repeatNumber', 'streamProb')):
  threads = []
  streamTPS = []
  tweetTPS = []
  streamLatency = []
  tweetLatency = []
  for dp in group:
    threads.append(dp.threads)
    streamTPS.append(dp.streamTPS)
    tweetTPS.append(dp.tweetTPS)
    streamLatency.append(dp.avgStreamTxTime)
    tweetLatency.append(dp.avgTweetTxTime)

  # check if streamProb > 0.0
  if key[4] > 0.0:  
    streamTPSPlots.append(Gnuplot.Data(threads, streamTPS, with_="lines", title=str(key)))
   
    g.title('Read Stream TPS vs. Workload Threads ' + str(key))
    g.xlabel('Workload Threads')
    g.ylabel('Transactions Per Second')
    g('set yrange [0:*]')
    g('set xrange [1:*]')
    g('set grid')
    g('set terminal pdf dashed font \"Times-Roman,8\"')
    g('set output \"stream_tps' + str(key) + '.pdf\"')
    g.plot(streamTPSPlots[-1])

    g('reset')

    streamLatencyPlots.append(Gnuplot.Data(threads, streamLatency, with_="lines", title=str(key)))  

    g.title('Read Stream Latency vs. Workload Threads ' + str(key))
    g.xlabel('Workload Threads')
    g.ylabel('Latency (us)')
    g('set yrange [0:*]')
    g('set xrange [1:*]')
    g('set grid')
    g('set key right bottom Right title \"Legend\"')
    g('set terminal pdf dashed font \"Times-Roman,8\"')
    g('set output \"stream_latency' + str(key) + '.pdf\"')
    g.plot(streamLatencyPlots[-1]) 

    g('reset')

  # check if streamProb < 1.0
  if key[4] < 1.0:
    tweetTPSPlots.append(Gnuplot.Data(threads, tweetTPS, with_="lines", title=str(key)))

    g.title('Write Tweet TPS vs. Workload Threads ' + str(key))
    g.xlabel('Workload Threads')
    g.ylabel('Transactions Per Second')
    g('set yrange [0:*]')
    g('set xrange [1:*]')
    g('set grid')
    g('set terminal pdf dashed font \"Times-Roman,8\"')
    g('set output \"tweet_tps' + str(key) + '.pdf\"')
    g.plot(tweetTPSPlots[-1])

    g('reset')

    tweetLatencyPlots.append(Gnuplot.Data(threads, tweetLatency, with_="lines", title=str(key)))

    g.title('Write Tweet Latency vs. Workload Threads ' + str(key))
    g.xlabel('Workload Threads')
    g.ylabel('Latency (us)')
    g('set yrange [0:*]')
    g('set xrange [1:*]')
    g('set grid')
    g('set key left top Right title \"Legend\"')
    g('set terminal pdf dashed font \"Times-Roman,8\"')
    g('set output \"tweet_latency' + str(key) + '.pdf\"')
    g.plot(tweetLatencyPlots[-1])

    g('reset')

g.title('Read Stream TPS vs. Workload Threads')
g.xlabel('Workload Threads')
g.ylabel('Transactions Per Second')
g('set yrange [0:*]')
g('set xrange [1:*]')
g('set grid')
g('set terminal pdf dashed font \"Times-Roman,8\"')
g('set output \"stream_tps.pdf\"')
g.plot(*streamTPSPlots)

g('reset')

g.title('Write Tweet TPS vs. Workload Threads')
g.xlabel('Workload Threads')
g.ylabel('Transactions Per Second')
g('set yrange [0:*]')
g('set xrange [1:*]')
g('set grid')
g('set terminal pdf dashed font \"Times-Roman,8\"')
g('set output \"tweet_tps.pdf\"')
g.plot(*tweetTPSPlots)

g('reset')

g.title('Read Stream Latency vs. Workload Threads')
g.xlabel('Workload Threads')
g.ylabel('Latency (us)')
g('set yrange [0:*]')
g('set xrange [1:*]')
g('set grid')
g('set key right bottom Right title \"Legend\"')
g('set terminal pdf dashed font \"Times-Roman,8\"')
g('set output \"stream_latency.pdf\"')
g.plot(*streamLatencyPlots)

g('reset')

g.title('Write Tweet Latency vs. Workload Threads')
g.xlabel('Workload Threads')
g.ylabel('Latency (us)')
g('set yrange [0:*]')
g('set xrange [1:*]')
g('set grid')
g('set key left top Right title \"Legend\"')
g('set terminal pdf dashed font \"Times-Roman,8\"')
g('set output \"tweet_latency.pdf\"')
g.plot(*tweetLatencyPlots)

g('reset')


