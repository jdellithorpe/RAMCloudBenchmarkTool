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

bool checkData = true;
bool debug = false;

int
main(int argc, char *argv[])
try {
    uint64_t clientIndex;
    uint64_t numClients;
    uint32_t tableServerSpan;
    uint64_t numObjects;
    uint64_t keySize;
    uint64_t objectSize;
    
    // Set line buffering for stdout so that printf's and log messages
    // interleave properly.
    setvbuf(stdout, NULL, _IOLBF, 1024);

    // need external context to set log levels with OptionParser
    Context context(false);

    OptionsDescription clientOptions("Loader");
    clientOptions.add_options()
            // These first two arguments are currently ignored. They are here
            // so that this client can be run with cluster.py
            ("clientIndex",
            ProgramOptions::value<uint64_t>(&clientIndex)->
                default_value(0),
            "Index of this client (first client is 0; currently ignored)")
            ("numClients",
            ProgramOptions::value<uint64_t>(&numClients)->
                default_value(1),
            "Total number of clients running (currently ignored)")
    
            ("tableServerSpan",
            ProgramOptions::value<uint32_t>(&tableServerSpan),
            "The serverSpan setting for the table into which the objects will be loaded.")
            ("numObjects",
            ProgramOptions::value<uint64_t>(&numObjects),
            "Number of objects to load.")
            ("keySize",
            ProgramOptions::value<uint64_t>(&keySize),
            "Size of keys in bytes.")
            ("objectSize",
            ProgramOptions::value<uint64_t>(&objectSize),
            "Object size in bytes.");

    OptionParser optionParser(clientOptions, argc, argv);

    LOG(NOTICE, "Loader: tableServerSpan: %d, numObjects: %lu, keySize: %luB, objectSize: %luB", tableServerSpan, numObjects, keySize, objectSize);
    
    // Check that keys are at least sizeof(uint64_t) bytes
    if( keySize < sizeof(uint64_t)) {
        LOG(ERROR, "keySize (%lu) must be at least %lu bytes", keySize, sizeof(uint64_t));
        return -1;
    }
    
    context.transportManager->setSessionTimeout(
            optionParser.options.getSessionTimeout());

    LOG(NOTICE, "connecting to %s with cluster name %s",
            optionParser.options.getCoordinatorLocator().c_str(),
            optionParser.options.getClusterName().c_str());

    RamCloud client(&context,
            optionParser.options.getCoordinatorLocator().c_str(),
            optionParser.options.getClusterName().c_str());

    uint64_t tableId = client.createTable("ObjectTable", tableServerSpan);

    LOG(NOTICE, "created ObjectTable (id %lu)\n", tableId);
    
    char key[keySize];
    memset(key, 0, keySize);
    
    char object[objectSize];
    memset(object, 0, objectSize);
    
    uint64_t start_time = Cycles::rdtsc();
    for(uint64_t i = 0; i < numObjects; i++) {
        memcpy(key, (const void*)&i, sizeof(uint64_t));
        memcpy(object, (const void*)&i, sizeof(uint64_t));
        
        client.write(tableId,
                (const void*) key, (uint16_t) keySize,
                (const void*) object, (uint32_t)objectSize);

        if (i % (uint64_t)100000 == 0)
            LOG(NOTICE, "wrote %lu objects (%0.2f MB to RamCloud) in %0.2f seconds, avg. %0.2f MB/s", i, (float) (i*(keySize + objectSize)) / 1000000.0, (float) Cycles::toSeconds(Cycles::rdtsc() - start_time), ((float) (i*(keySize + objectSize)) / (float) Cycles::toSeconds(Cycles::rdtsc() - start_time)) / 1000000.0);
    }
    LOG(NOTICE, "wrote %lu objects (%0.2f MB to RamCloud) in %0.2f seconds, avg. %0.2f MB/s", numObjects, (float) (numObjects*(keySize + objectSize)) / 1000000.0, (float) Cycles::toSeconds(Cycles::rdtsc() - start_time), ((float) (numObjects*(keySize + objectSize)) / (float) Cycles::toSeconds(Cycles::rdtsc() - start_time)) / 1000000.0);

    if(checkData) {
        LOG(NOTICE, "checking data...");
        
        Buffer buf;
        memset(key, 0, keySize);
        
        char expectedObject[objectSize];
        memset(expectedObject, 0, objectSize);
        for(uint64_t i = 0; i < 1000; i++) {
            uint64_t randomObjectIndex = (uint64_t) rand() % numObjects;
            
            memcpy(key, (const void*)&randomObjectIndex, sizeof(uint64_t));
            memcpy(expectedObject, (const void*)&randomObjectIndex, sizeof(uint64_t));
            
            client.read(tableId, key, (uint16_t) keySize, &buf);
            
            if(buf.size() != objectSize) {
                LOG(ERROR, "Object %lu is of size %d but should be of size %lu", randomObjectIndex, buf.size(), objectSize);
                return -1;
            }
            
            if(memcmp(expectedObject, buf.getRange(0, buf.size()), objectSize)) {
                LOG(ERROR, "Object %lu contains a different value than was expected", randomObjectIndex);
                if(debug) {
                    char* receivedObject = (char*)buf.getRange(0, buf.size());
                    for(uint64_t i = 0; i < objectSize; i++)
                        printf("(%5lu): expectedObject: %20d receivedObject: %20d\n", i, expectedObject[i], receivedObject[i]);
                }
                return -1;
            }
            
        }
        LOG(NOTICE, "data check passed!");
    }
    
    return 0;
} catch (RAMCloud::ClientException& e) {
    fprintf(stderr, "RAMCloud exception: %s\n", e.str().c_str());
    return 1;
} catch (RAMCloud::Exception& e) {
    fprintf(stderr, "RAMCloud exception: %s\n", e.str().c_str());
    return 1;
}
