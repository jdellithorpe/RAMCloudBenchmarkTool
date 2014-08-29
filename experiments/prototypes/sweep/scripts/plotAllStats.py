#!/usr/bin/python

import os
import numpy
import sys
import Gnuplot

clientOutputDir = "./client_output/"
serverOutputDir = "./server_output/"

threadsArrayST = []
txArrayST = []
tpsArrayST = []
minArrayST = []
meanArrayST = []
maxArrayST = []
stdArrayST = []
p99ArrayST = []
p999ArrayST = []
p9999ArrayST = []

threadsArrayTW = []
txArrayTW = []
tpsArrayTW = []
minArrayTW = []
meanArrayTW = []
maxArrayTW = []
stdArrayTW = []
p99ArrayTW = []
p999ArrayTW = []
p9999ArrayTW = []

meanArraySTDat = []
meanArrayTWDat = []

TW_AvgIncTimes = []
TW_AvgWrTweetTimes = []
TW_AvgRdTweetListTimes = []
TW_AvgWrTweetListTimes = []
TW_AvgRdFollowersTimes = []
TW_AvgMultiRdFollowerStreamTimes = []
TW_AvgMultiWrFollowerStreamTimes = []

runTime = 0

for subDir, dirs, files in os.walk(".."):
  if subDir == "..":
    for expDir in sorted(dirs):
      if expDir[:4] == "run_":
        aggLatencyArray = {"ST": [], "TW": []}

        latFiles = 0
        datFiles = 0
        totalStreamTx = 0
        totalTweetTx = 0
        totalStreamTxTime = 0.0
        totalTweetTxTime = 0.0

        totalIncTime = 0.0
        totalWrTweetTime = 0.0
        totalRdTweetListTime = 0.0
        totalWrTweetListTime = 0.0
        totalRdFollowersTime = 0.0
        totalMultiRdFollowerStreamTime = 0.0
        totalMultiWrFollowerStreamTime = 0.0

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
            datFile = open(subDir + "/" + expDir + "/" + clientOutputDir + file, 'r')
            streamTx = 0
            tweetTx = 0
            avgStreamTxTime = 0
            avgTweetTxTime = 0

            avgIncTime = 0.0
            avgWrTweetTime = 0.0
            avgRdTweetListTime = 0.0
            avgWrTweetListTime = 0.0
            avgRdFollowersTime = 0.0
            avgMultiRdFollowerStreamTime = 0.0
            avgMultiWrFollowerStreamTime = 0.0

            for line in datFile.readlines():
              lineParts = line.strip().split(":")
              if lineParts[0].strip() == "RUNTIME":
                if runTime == 0:
                  runTime = float(lineParts[1][:-1])
                  print 'Setting runtime: ' + str(runTime) + 's'
              elif lineParts[0].strip() == "STREAM TRANSACTIONS":
                streamTx = int(lineParts[1])
              elif lineParts[0].strip() == "AVERAGE STREAM TX TIME":
                avgStreamTxTime = float(lineParts[1][:-2])
              elif lineParts[0].strip() == "TWEET TRANSACTIONS":
                tweetTx = int(lineParts[1])
              elif lineParts[0].strip() == "AVERAGE TWEET TX TIME":
                avgTweetTxTime = float(lineParts[1][:-2])
              elif lineParts[0].strip() == "AVERAGE INCREMENT TWEETID":
                avgIncTime = float(lineParts[1][:-2])
              elif lineParts[0].strip() == "AVERAGE WRITE TWEETID:DATA"
                avgWrTweetTime = float(lineParts[1][:-2]) 
              elif lineParts[0].strip() == "AVERAGE READ USERID:TWEETS"
                avgRdTweetListTime = float(lineParts[1][:-2]) 
              elif lineParts[0].strip() == "AVERAGE WRITE USERID:TWEETS"
                avgWrTweetListTime = float(lineParts[1][:-2]) 
              elif lineParts[0].strip() == "AVERAGE READ USERID:FOLLOWERS"
                avgRdFollowersTime = float(lineParts[1][:-2])
              elif lineParts[0].strip() == "AVERAGE MULTIREAD USERID:STREAM"
                avgMultiRdFollowerStreamTime = float(lineParts[1][:-2])
              elif lineParts[0].strip() == "AVERAGE MULTIWRITE USERID:STREAM"
                avgMultiWrFollowerStreamTime = float(lineParts[1][:-2]) 
                
            totalStreamTx += streamTx
            totalTweetTx += tweetTx
            totalStreamTxTime += float(streamTx)*avgStreamTxTime
            totalTweetTxTime += float(tweetTx)*avgTweetTxTime

            totalIncTime += float(tweetTx)*avgIncTime
            totalWrTweetTime += float(tweetTx)*avgWrTweetTime
            totalRdTweetListTime += float(tweetTx)*avgRdTweetListTime
            totalWrTweetListTime += float(tweetTx)*avgWrTweetListTime
            totalRdFollowersTime += float(tweetTx)*avgRdFollowersTime
            totalMultiRdFollowerStreamTime += float(tweetTx)*avgMultiRdFollowerStreamTime
            totalMultiWrFollowerStreamTime += float(tweetTx)*avgMultiWrFollowerStreamTime

        if totalStreamTx != 0:
          meanArraySTDat.append(totalStreamTxTime/totalStreamTx)
        
        if totalTweetTx != 0:
          meanArrayTWDat.append(totalTweetTxTime/totalTweetTx)
          TW_AvgIncTimes.append(totalIncTime/totalTweetTx)
          TW_AvgWrTweetTimes.append(totalWrTweetTime/totalTweetTx)
          TW_AvgRdTweetListTimes.append(totalRdTweetListTime/totalTweetTx)
          TW_AvgWrTweetListTimes.append(totalWrTweetListTime/totalTweetTx)
          TW_AvgRdFollowersTimes.append(totalRdFollowersTime/totalTweetTx)
          TW_AvgMultiRdFollowerStreamTimes.append(totalMultiRdFollowerStreamTime/totalTweetTx)
          TW_AvgMultiWrFollowerStreamTimes.append(totalMultiWrFollowerStreamTime/totalTweetTx)

        if runTime == 0:
          print 'Critical Error: did not catch runTime value'

        # calculate overall statistics for stream transactions
        if len(aggLatencyArray["ST"]) != 0:
          threadsArrayST.append(datFiles)
          txArrayST.append(totalStreamTx)
          tpsArrayST.append((float(totalStreamTx)/float(runTime)))
          minArrayST.append(numpy.min(aggLatencyArray["ST"]))
          meanArrayST.append(numpy.mean(aggLatencyArray["ST"]))
          maxArrayST.append(numpy.max(aggLatencyArray["ST"]))
          stdArrayST.append(numpy.std(aggLatencyArray["ST"]))
          if hasattr(numpy, "percentile"):
            p99ArrayST.append(numpy.percentile(aggLatencyArray["ST"], 99.0)) 
            p999ArrayST.append(numpy.percentile(aggLatencyArray["ST"], 99.9))
            p9999ArrayST.append(numpy.percentile(aggLatencyArray["ST"], 99.99)) 
          else:
            p99ArrayST.append(0.00)
            p999ArrayST.append(0.00)
            p9999ArrayST.append(0.00)

        # calculate overall statistics for tweet transactions
        if len(aggLatencyArray["TW"]) != 0:
          threadsArrayTW.append(datFiles)
          txArrayTW.append(totalTweetTx)
          tpsArrayTW.append((float(totalTweetTx)/float(runTime)))
          minArrayTW.append(numpy.min(aggLatencyArray["TW"]))
          meanArrayTW.append(numpy.mean(aggLatencyArray["TW"]))
          maxArrayTW.append(numpy.max(aggLatencyArray["TW"]))
          stdArrayTW.append(numpy.std(aggLatencyArray["TW"]))
          if hasattr(numpy, "percentile"):
            p99ArrayTW.append(numpy.percentile(aggLatencyArray["TW"], 99.0)) 
            p999ArrayTW.append(numpy.percentile(aggLatencyArray["TW"], 99.9))
            p9999ArrayTW.append(numpy.percentile(aggLatencyArray["TW"], 99.99)) 
          else:
            p99ArrayTW.append(0.00)
            p999ArrayTW.append(0.00)
            p9999ArrayTW.append(0.00)
  
g = Gnuplot.Gnuplot()

if l

if len(threadsArrayST) != 0:           
  meanPlotSTLat = Gnuplot.Data(threadsArrayST, meanArrayST, with_="lines")
  meanPlotSTDat = Gnuplot.Data(threadsArrayST, meanArraySTDat, with_="lines")
  tpsPlotST = Gnuplot.Data(threadsArrayST, tpsArrayST, with_="lines")

  g('set grid')
  
  g.title('Mean Stream TX Latency vs. Workload Threads')
  g.xlabel('Workload Threads')
  g.ylabel('Mean Latency (us)')
  g('set yrange [0:*]')
  g('set terminal pdf dashed font \"Times-Roman,11\"')
  g('set output \"mean_st_lat.lat.pdf\"')
  g.plot(meanPlotSTLat)

  g('set terminal png size 640,480')
  g('set output \"mean_st_lat.lat.png\"')
  g.plot(meanPlotSTLat)

  g('set terminal pdf dashed font \"Times-Roman,11\"')
  g('set output \"mean_st_lat.dat.pdf\"')
  g.plot(meanPlotSTDat)

  g('set terminal png size 640,480')
  g('set output \"mean_st_lat.dat.png\"')
  g.plot(meanPlotSTDat)

  g.title('Mean Stream TPS vs. Workload Threads')
  g.ylabel('Mean TPS')
  g('set terminal pdf dashed font \"Times-Roman,11\"')   
  g('set output \"mean_st_tps.pdf\"')
  g.plot(tpsPlotST)

  g('set terminal png size 640,480')
  g('set output \"mean_st_tps.png\"')
  g.plot(tpsPlotST)

g('reset')

if len(threadsArrayTW) != 0:
  meanPlotTWLat = Gnuplot.Data(threadsArrayTW, meanArrayTW, with_="lines")
  meanPlotTWDat = Gnuplot.Data(threadsArrayTW, meanArrayTWDat, with_="lines")
  tpsPlotTW = Gnuplot.Data(threadsArrayTW, tpsArrayTW, with_="lines")

  g('set grid')

  g.title('Mean Tweet TX Latency vs. Workload Threads')
  g.xlabel('Workload Threads')
  g.ylabel('Mean Latency (us)')
  g('set yrange [0:*]')
  g('set terminal pdf dashed font \"Times-Roman,11\"')
  g('set output \"mean_tw_lat.lat.pdf\"')
  g.plot(meanPlotTWLat)

  g('set terminal png size 640,480')
  g('set output \"mean_tw_lat.lat.png\"')
  g.plot(meanPlotTWLat)

  g('set terminal pdf dashed font \"Times-Roman,11\"')
  g('set output \"mean_tw_lat.dat.pdf\"')
  g.plot(meanPlotTWDat)

  g('set terminal png size 640,480')
  g('set output \"mean_tw_lat.dat.png\"')
  g.plot(meanPlotTWDat)

  g.title('Mean Tweet TPS vs. Workload Threads')
  g.ylabel('Mean TPS')
  g('set terminal pdf dashed font \"Times-Roman,11\"')   
  g('set output \"mean_tw_tps.pdf\"')
  g.plot(tpsPlotTW)

  g('set terminal png size 640,480')
  g('set output \"mean_tw_tps.png\"')
  g.plot(tpsPlotTW)


