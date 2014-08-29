/* Copyright (c) 2009-2014 Stanford University
 *
 * Permission to use, copy, modify, and distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR(S) DISCLAIM ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL AUTHORS BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */

#include <stdio.h>
#include <string.h>
#include <getopt.h>
#include <assert.h>
#include <fstream>
#include <thread>
#include <random>

#include "ClusterMetrics.h"
#include "Cycles.h"
#include "ShortMacros.h"
#include "Crc32C.h"
#include "ObjectFinder.h"
#include "OptionParser.h"
#include "RamCloud.h"
#include "Tub.h"

using namespace RAMCloud;

// USERID, TXTYPE, LATENCY
#define LATFILE_HDRFMTSTR "%12s%12s%12s\n"
#define LATFILE_ENTFMTSTR "%12lu%12s%12.2f\n"

// RUNTIME, STREAM_UPDATE_FAILURES
#define DATFILE_HDRFMTSTR "%12s\n"
#define DATFILE_ENTFMTSTR "%12.2f\n"

#define NUM_STATS 10

typedef struct {
  uint64_t startTime;
  uint64_t endTime;
  uint64_t totalTime;
  uint64_t keyBytes;
  uint64_t totalKeyBytes;
  uint64_t valueBytes;
  uint64_t totalValueBytes;
  uint64_t multiOpSize;
  uint64_t totalMultiOpSize;
  uint64_t opCount;
  uint64_t rejectCount;
} opStat_t;

uint64_t timePassed(opStat_t x) {
    return x.endTime - x.startTime;
}

void
WorkloadThread(
        OptionParser& optionParser,
        uint64_t clientIndex,
        uint64_t threadIndex,
        double runTime,
        string opType,
        uint64_t multiOpSize,
        uint64_t numObjects,
        uint64_t keySize,
        uint64_t objectSize,
        bool enableLatLogging,
        string outputDir) {
    
    LOG(NOTICE, "Client(%02lu) Thread(%02lu): Starting...", clientIndex, threadIndex);

    LOG(NOTICE, "Client(%02lu) Thread(%02lu): Connecting to coordinator at %s", clientIndex, threadIndex, optionParser.options.getCoordinatorLocator().c_str());
    
    // need external context to set log levels with OptionParser
    Context context(false);
    
    RamCloud client(&context,
            optionParser.options.getCoordinatorLocator().c_str(),
            optionParser.options.getClusterName().c_str());
    
    LOG(NOTICE, "Client(%02lu) Thread(%02lu): Looking for ObjectTable...", clientIndex, threadIndex);
    
    uint64_t tableId = client.getTableId("ObjectTable");
    
    LOG(NOTICE, "Client(%02lu) Thread(%02lu): Found ObjectTable (id %lu)...", clientIndex, threadIndex, tableId);
    
    string latFileName = format("%sc%02lu_t%02lu.lat", outputDir.c_str(), clientIndex, threadIndex);
    
    std::ofstream latFile;
    if(clientIndex == 0 && threadIndex == 0 && enableLatLogging) {
        LOG(NOTICE, "Client(%02lu) Thread(%02lu): Recording latency measurements in file %s", clientIndex, threadIndex, latFileName.c_str());
        latFile.open(latFileName.c_str());
        latFile << format(LATFILE_HDRFMTSTR, "#KEY", "OPTYPE", "LATENCY(us)");
    }
    
    opStat_t opStat;
    memset(&opStat, 0, sizeof(opStat));
    
    if(opType == "READ") {
        Buffer buf;
        char key[keySize];
        memset(key, 0, keySize);
        
        uint64_t runTimeStart = Cycles::rdtsc();
        while (Cycles::toSeconds(Cycles::rdtsc() - runTimeStart) < runTime) {
            uint64_t randomObjectIndex = (uint64_t) rand() % numObjects;
            memset(key, 0, keySize);
            memcpy(key, (const void*)&randomObjectIndex, sizeof(randomObjectIndex));
            
            opStat.startTime = Cycles::rdtsc();
            client.read(tableId, key, (uint16_t) keySize, &buf);
            opStat.endTime = Cycles::rdtsc();
            opStat.totalTime += timePassed(opStat);
            opStat.opCount++;
            
            if(clientIndex == 0 && threadIndex == 0 && enableLatLogging)
                latFile << format(LATFILE_ENTFMTSTR, randomObjectIndex, opType.c_str(), (double)Cycles::toNanoseconds(timePassed(opStat))/1000.0);
        }
    } else if(opType == "WRITE") {
        char key[keySize];
        memset(key, 0, keySize);
        
        char object[objectSize];
        memset(object, 0, objectSize);
    
        uint64_t runTimeStart = Cycles::rdtsc();
        while (Cycles::toSeconds(Cycles::rdtsc() - runTimeStart) < runTime) {
            uint64_t randomObjectIndex = (uint64_t) rand() % numObjects;
            memset(key, 0, keySize);
            memcpy(key, (const void*)&randomObjectIndex, sizeof(randomObjectIndex));
            
            memset(object, 0, objectSize);
            memcpy(object, (const void*)&randomObjectIndex, sizeof(randomObjectIndex));
            
            opStat.startTime = Cycles::rdtsc();
            client.write(tableId,
                    (const void*) key, (uint16_t) keySize,
                    (const void*) object, (uint32_t)objectSize);
            opStat.endTime = Cycles::rdtsc();
            opStat.totalTime += timePassed(opStat);
            opStat.opCount++;
            
            if(clientIndex == 0 && threadIndex == 0 && enableLatLogging)
                latFile << format(LATFILE_ENTFMTSTR, randomObjectIndex, opType.c_str(), (double)Cycles::toNanoseconds(timePassed(opStat))/1000.0);
        }
    } else if(opType == "MULTIREAD") {
        
    } else if(opType == "MULTIWRITE") {
        
    } else {
        LOG(ERROR, "Client(%02lu) Thread(%02lu): Unrecognized opType %s", clientIndex, threadIndex, opType.c_str());
        if(clientIndex == 0 && threadIndex == 0 && enableLatLogging)
            latFile.close();
        return;
    }
    
    if(clientIndex == 0 && threadIndex == 0 && enableLatLogging)
        latFile.close();

    string datFileName = format("%sc%02lu_t%02lu.dat", outputDir.c_str(), clientIndex, threadIndex);
    
    LOG(NOTICE, "Client(%02lu) Thread(%02lu): Recording summary information in file %s", clientIndex, threadIndex, datFileName.c_str());
    
    std::ofstream datFile(datFileName.c_str());
    
    if(opStat.opCount > 0) {
        datFile << format("%-35s:%lu\n", "OP COUNT", opStat.opCount);
        datFile << format("%-35s:%0.2f\n", "AVERAGE OP LATENCY (us)", (double)Cycles::toNanoseconds(opStat.totalTime) / (double)opStat.opCount / 1000.0);
    } else {
        datFile << format("%-35s:%lu\n", "OP COUNT", (uint64_t)0);
        datFile << format("%-35s:%0.2f\n", "AVERAGE OP LATENCY (us)", 0.0);
    }
    
    datFile.close();
}

int
main(int argc, char *argv[])
try {
    uint64_t clientIndex;
    uint64_t numClients;
    double runTime;
    string opType;
    uint64_t multiOpSize;
    uint64_t numThreads;
    uint64_t numObjects;
    uint64_t keySize;
    uint64_t objectSize;
    bool enableLatLogging;
    string outputDir;

    // Set line buffering for stdout so that printf's and log messages
    // interleave properly.
    setvbuf(stdout, NULL, _IOLBF, 1024);

    // need external context to set log levels with OptionParser
    Context context(false);

    OptionsDescription clientOptions("TwitterWorkloadClient");
    clientOptions.add_options()
            ("clientIndex",
            ProgramOptions::value<uint64_t>(&clientIndex)->
                default_value(0),
            "Index of this client (first client is 0; default 0)")
            ("numClients",
            ProgramOptions::value<uint64_t>(&numClients)->
                default_value(1),
            "Total number of client servers running (default 1)")
            ("runTime",
            ProgramOptions::value<double>(&runTime),
            "Total time to run (seconds).")
            ("opType",
            ProgramOptions::value<string>(&opType),
            "Type of operation to benchmark (READ, WRITE, MULTIREAD, MULTIWRITE).")
            ("multiOpSize",
            ProgramOptions::value<uint64_t>(&multiOpSize)->
                default_value(0),
            "If opType is one of {MULTIREAD, MULTIWRITE}, then this parameter determines the size of a multiOp (default 0).")
            ("numThreads",
            ProgramOptions::value<uint64_t>(&numThreads)->
                default_value(1),
            "Total number of threads spread over clients (default 1).")
            ("numObjects",
            ProgramOptions::value<uint64_t>(&numObjects),
            "Perform ops uniformly distributed over numObjects.")
            ("keySize",
            ProgramOptions::value<uint64_t>(&keySize),
            "Size of keys in bytes.")
            ("objectSize",
            ProgramOptions::value<uint64_t>(&objectSize),
            "Object size in bytes.")
            ("enableLatLogging",
            ProgramOptions::value<bool>(&enableLatLogging)->
                default_value(false),
            "Enable outputting of each individual latency measurement (default false).")
            ("outputDir",
            ProgramOptions::value<string>(&outputDir)->
                default_value("./"),
            "Output directory for measurement files (default \"./\".");


    OptionParser optionParser(clientOptions, argc, argv);
    
    LOG(NOTICE, "WorkloadClient: \n"
            "clientIndex: %lu\n"
            "numClients: %lu\n"
            "runTime: %0.2f\n"
            "opType: %s\n"
            "multiOpSize: %lu\n"
            "numThreads: %lu\n"
            "numObjects: %lu\n"
            "keySize: %lu\n"
            "objectSize: %lu\n"
            "enableLatLogging: %d\n"
            "outputDir: %s\n",
            clientIndex,
            numClients,
            runTime,
            opType.c_str(),
            multiOpSize,
            numThreads,
            numObjects,
            keySize,
            objectSize,
            enableLatLogging,
            outputDir.c_str());

    uint64_t numLocalThreads = numThreads / numClients;
    numLocalThreads += ((numThreads % numClients) > clientIndex) ? 1 : 0;

    LOG(NOTICE, "Launching workload threads...");

    Tub<std::thread> threads[numLocalThreads];

    for (uint64_t i = 0; i < numLocalThreads; i++)
        threads[i].construct(WorkloadThread, optionParser, clientIndex, i, runTime, opType, multiOpSize, numObjects, keySize, objectSize, enableLatLogging, outputDir);

    for (uint64_t i = 0; i < numLocalThreads; i++)
        threads[i].get()->join();

    return 0;
} catch (RAMCloud::ClientException& e) {
    fprintf(stderr, "RAMCloud exception: %s\n", e.str().c_str());
    return 1;
} catch (RAMCloud::Exception& e) {
    fprintf(stderr, "RAMCloud exception: %s\n", e.str().c_str());
    return 1;
}
