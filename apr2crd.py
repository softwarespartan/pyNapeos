#!/usr/bin/python

import getopt
import os
import sys
import stnInfoLib;
import pyDate;
import re;
import pyDomes;

class apr2crdException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
    
shortArgs = "f:d:h"

longArgs = []
longArgs.append("file=");
longArgs.append("crdFile=");
longArgs.append("domesFile=");
longArgs.append("help");

def usage():
    print
    print
    print " info2dat -f /path/to/stninfo/file"
    print
    print "Convert XYZ VxVyVz refEpoch to NAPEOS CRD format"
    print
    print "NOTE:  station info can be piped via stdin.  However, -f will veto stdin"
    print
    print " Two formats can be input:"
    print "  "
    print "     1.  TAG  X Y Z  (default sigmas: 0.5 m)"
    print
    print "     2.  TAG X Y Z sigX sigY sigZ"
    print
    print " NOTE: TAGs will always be parsed to 4 char "
    print
    print "         igs::amun  --> amun"
    print
    print "         AMUN_GPS   --> amun"
    print
    print "options:"
    print "-f, --file=          path to input apr file"
    print "  , --crdFile=       path for output CRD file (optional, stdout otherwise)"
    print "-d, --domesFile=     path with station DOMES# key value pairs"
    print "-h, --help           display this message"
    print
    
def getInputArgs():
    
    aprFilePath   = None;
    crdFilePath   = None;
    domesFilePath = None;
    
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], shortArgs, longArgs)
        
    except getopt.GetoptError, err:
        
        # print help information and exit:
        print str(err)
        usage()
        sys.exit(2)
        
    for option,arg in opts:
        
        #print option, arg
            
        if option in ("-f","--file"):
            
            if not os.path.isfile(arg):
                raise apr2crdException(" file: "+ arg+" does not exist ");
            
            aprFilePath = arg;
            
        if option in ("--crdFile"):
            crdFilePath = arg;
            
        if option in ("-d","--domesFile"):
            domesFilePath = arg;
            
        if option in ("-h","--help"):
            usage();
            sys.exit();

    
    return aprFilePath, crdFilePath, domesFilePath;

def parseApr(src,crdFilePath=None,domesFilePath=None):
    
    dst = None;
    if crdFilePath !=None:
        dst = open(crdFilePath,'w');
    else:
        dst = sys.stdout;
        
    # init a domes number management system
    domesMgr = pyDomes.Domes(domesFilePath);
        
    dst.write('STATION COORDINATES AT EPOCH  2002.0\n')
    
    for line in src.readlines():
        
        # kill white spaces either side
        line = line.strip();
        
        # decompose the line
        lineParts = re.split("\s+",line);
        
        if len(lineParts) != 4 and len(lineParts) != 7:
            os.sys.stderr.write("line: "+ line+" is invalid.  must have 4 or 8 fields.  Use -h option");
            continue;
                
        # every line has at least this
        stnId = lineParts[0]; 
        x     = float(lineParts[1]);
        y     = float(lineParts[2]);
        z     = float(lineParts[3]);
                
        # check for additional velocity info
        if len(lineParts) == 7:
            sigX       = float(lineParts[4]);
            sigY       = float(lineParts[5]);
            sigZ       = float(lineParts[6]);
        else:
            # assign default values
            dfltSigma  = 0.5;
            sigX       = dfltSigma;
            sigY       = dfltSigma;
            sigZ       = dfltSigma;
                        
        # make sure sigmas are well behaved
        if sigX >= 10.0:
            sigX = 9.999;
        if sigY >= 10.0:
            sigY = 9.999;
        if sigZ >= 10.0:
            sigZ = 9.999; 
                        
        # make sure station identification is 
        # in same flavor as domes mgr    
        stnId = pyDomes.parseStnId(stnId);
        
        if domesMgr.containsStnId(stnId):
            domesNumber = domesMgr.domesForStnId(stnId);
        else:
            stnId,domesNumber = domesMgr.addStn(stnId);
            
        printAsCrd(dst,domesNumber,stnId,x,y,z,sigX,sigY,sigZ);
            
    if domesFilePath != None:
        domesMgr.export();
               
def printAsCrd(dst,domesNumber,stnId,x,y,z,sigX,sigY,sigZ):
    
        xyzStr =  "%9s %4s %9s     GPS %4s                  %12.3f %12.3f %12.3f %5.3f %5.3f %5.3f OSU" % (domesNumber, stnId.upper(), domesNumber, stnId.upper(), x, y, z, sigX, sigY, sigZ)
        velStr =  "%9s %4s %9s         %4s                  %12.3f %12.3f %12.3f %5.3f %5.3f %5.3f OSU" % (domesNumber, "", "", "", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)    
    
        dst.write(xyzStr+"\n");
        dst.write(velStr+"\n");
        
          
def main():
    
    aprFilePath, crdFilePath, domesFilePath = getInputArgs();
    
    src = None;
    if aprFilePath != None:
        src = open(aprFilePath,'r');
    else:
        src = sys.stdin;
        
    parseApr(src, crdFilePath, domesFilePath)

if __name__ == '__main__':
    
    main()
           
