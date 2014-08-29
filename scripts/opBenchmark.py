#!/usr/bin/env python

from cluster import Cluster
from random import shuffle
import subprocess
import datetime
import os
import pprint

verbose = True
server_log_level = 'ERROR'
useDisjunctBackups = False

def makeHostList(start,stop):
  return [('rc%02d' % i, '192.168.1.%d' % (100+i), '%d'%i) 
          for i in range(start,stop+1)] 

clientHosts = makeHostList(50,55)+makeHostList(59,65)
serverHosts = makeHostList(56,58)
backupHosts = makeHostList(59,59)
coordinatorHost = makeHostList(56,56)[0]

# array of experiment configurations
expConfigs = []

# RAMCloud parameters
for numMasters in [3]:
  for masterArgs in ['--totalMasterMemory 70% --segmentFrames 4200']:
    for replicas in [1]:
# Data parameters
      for tableServerSpan in [numMasters]:
        for numObjects in [100000]:
          for keySize, objectSize in [(30,100)]:
# Client parameters
            for runTime in [5.0]:
              for opType in ['WRITE']:
                if opType == 'MULTIREAD' or opType == 'MULTIWRITE':
                  multiOpSizes = [10, 20]
                else:
                  multiOpSizes = [0]
                for multiOpSize in multiOpSizes:
                  for numClientHosts in [len(clientHosts)]:
                    for threads in range(1,64,1):
                      for repeatNumber in range(0,1):
                        enableLatLogging = 0
                        expConfigs.append({ # general parameters
                                            'repeatNumber': repeatNumber,
                                            # RAMCloud parameters
                                            'numMasters': numMasters,
                                            'replicas': replicas,
                                            'masterArgs': masterArgs,
                                            # data loader parameters
                                            'tableServerSpan': tableServerSpan,
                                            'numObjects': numObjects,
                                            'keySize': keySize,
                                            'objectSize': objectSize,
                                            # client parameters
                                            'runTime': runTime,
                                            'opType': opType,
                                            'multiOpSize': multiOpSize,
                                            'numClientHosts': numClientHosts,
                                            'numThreads': threads,
                                            'enableLatLogging': enableLatLogging })

# root directories for important things
binDir = '/home/jdellit/NetBeansProjects/ramcloud/WorkloadExperiments/'
expRootDir = '/home/jdellit/Shared2/experiments/ramcloud/'
ramcloudDir = '/home/jdellit/git/ramcloud/'

# directory structures to copy for sweeps and runs
sweepPrototype = expRootDir + 'prototypes/sweep'
runPrototype = expRootDir + 'prototypes/run'

# use this date to name the folder for this series of experiments
sweepDate = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

# create sweep directory
sweepDir = expRootDir + 'results/sweep_' + sweepDate
subprocess.call([ 'cp', '-R', 
                  sweepPrototype, 
                  sweepDir])

# record config parameters for this sweep
with open(sweepDir + '/parameters.txt', 'w') as f:
  pp = pprint.PrettyPrinter(width=1)
  f.write('Experiment Configurations:\n')
  f.write(pp.pformat(expConfigs))
  f.write('\n')

# shuffle the configuration order
shuffle(expConfigs)

totalConfigs = len(expConfigs)
configsProcessed = 0

for config in expConfigs:
  # create subdir for this run
  runDate = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
  runDir = sweepDir + '/run_' + runDate 
  subprocess.call([ 'cp', '-R',
                    runPrototype,
                    runDir])

  if verbose:
    print('starting experiment %d/%d (%s) with parameters:' % (configsProcessed+1, totalConfigs, runDir))
    pp = pprint.PrettyPrinter(width=1)
    print(pp.pformat(config))

  # record config parameters for this run
  with open(runDir + '/parameters.txt', 'w') as f:
    pp = pprint.PrettyPrinter(width=1)
    f.write('Experiment Configuration:\n')
    f.write(pp.pformat(config))
    f.write('\n')

  with Cluster() as cluster:
    # configure the cluster
    cluster.verbose = False
    cluster.log_level = server_log_level
     
    # startup a ramcloud
    if verbose:
      print('starting ramcloud cluster...')
    try:
      if useDisjunctBackups:
        log_subdir = cluster.start_ramcloud(master_args = config['masterArgs'],
                                            server_hosts = serverHosts[:config['numMasters']],
                                            backup_hosts = backupHosts,
                                            coordinator_host = coordinatorHost,
                                            replicas = config['replicas'])      
      else: 
        log_subdir = cluster.start_ramcloud(master_args = config['masterArgs'],
                                            server_hosts = serverHosts[:config['numMasters']],
                                            coordinator_host = coordinatorHost,
                                            replicas = config['replicas'])
    except:
      print 'ERROR: failed to start ramcloud, aborting experiment, but will retry this configuration later'
      # destroy 'run' directory
      subprocess.call(['rm', '-rf', runDir])
      # add this config back to the end to execute later
      expConfigs.append(config)
      continue

    # load data into ramcloud
    if verbose:
      print('loading data into ramcloud...')
    clients = cluster.start_clients(  [clientHosts[0]],
                                      binDir + 'Loader'
                                      ' --tableServerSpan=' + str(config['tableServerSpan']) + 
                                      ' --numObjects=' + str(config['numObjects']) +
                                      ' --keySize=' + str(config['keySize']) +
                                      ' --objectSize=' + str(config['objectSize']) )
    
    try:   
      cluster.wait(clients, 60) # should take at most 60 seconds to finish
    except:
      print 'ERROR: failed to load data, aborting experiment, but will retry this configuration later...'
      # destroy 'run' directory
      subprocess.call(['rm', '-rf', runDir])
      # add this config back to the end to execute later
      expConfigs.append(config)
      continue
 
    # run twitter workload
    if verbose:
      print('running workload clients...')
    clients = cluster.start_clients(  clientHosts[:config['numClientHosts']],
                                      binDir + 'WorkloadClient'
                          ' --runTime=' + str(config['runTime']) + 
                          ' --opType=' + config['opType'] + 
                          ' --multiOpSize=' + str(config['multiOpSize']) + 
                          ' --numThreads=' + str(config['numThreads']) + 
                          ' --numObjects=' + str(config['numObjects']) + 
                          ' --keySize=' + str(config['keySize']) + 
                          ' --objectSize=' + str(config['objectSize']) +
                          ' --enableLatLogging=' + str(config['enableLatLogging']) + 
                          ' --outputDir=' + runDir + '/client_output/' )
                                            
    try:
      cluster.wait(clients, config['runTime'] + 10)
    except:
      print 'ERROR: failed run workload clients, aborting experiment, but will retry this configuration later...'
      # destroy 'run' directory
      subprocess.call(['rm', '-rf', runDir])
      # add this config back to the end to execute later
      expConfigs.append(config)
      continue
 
  # wrap-up
  subprocess.call([ 'cp', '-R',
                    log_subdir,
                    runDir + '/server_output/'])

  configsProcessed += 1

        

