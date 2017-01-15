#!/usr/bin/python

import os;
import sys;
import snxParse;

def usage():
             
    print "USAGE:  snx2crd snxFile sigma";
    sys.exit(1);

def main():
        
    if len(sys.argv) != 3:
        usage()

    # get the command line args
    file   = sys.argv[1];
    sigXYZ = sys.argv[2];
    
    # make sure snx file actually exists
    if not os.path.isfile(file):
        os.sys.stderr.write("SINEX file "+file+" does not exist\n");
        sys.exit(2);
        
    # make sure the sigma that was input is a number
    try:
        sigXYZ = float(sigXYZ);
    except:
        os.sys.stderr.write("CRD sigma "+sigXYZ+" must be a number\n");
        sys.exit(3);
    
    # parse the specified file
    snxParser = snxParse.snxFileParser(file).parse();
    
    # print the header line
    os.sys.stdout.write('STATION COORDINATES AT EPOCH  2002.0\n');
    
    # organize the coordinates for the data object
    for stn in snxParser:

        try:
            # get the snx data from the parser
            stnData = snxParser.get(stn);
            
            #print stn, stnData.domesNumber, stnData.X, stnData.Y, stnData.Z;
    
            xyzStr =  "%9s %4s %9s     GPS %4s                  %12.3f %12.3f %12.3f %5.3f %5.3f %5.3f OSU" % (stnData.domesNumber, stn, stnData.domesNumber, stn, stnData.X, stnData.Y, stnData.Z, sigXYZ, sigXYZ, sigXYZ)
            velStr =  "%9s %4s %9s         %4s                  %12.3f %12.3f %12.3f %5.3f %5.3f %5.3f OSU" % (stnData.domesNumber, "", "", "", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)    
        
            os.sys.stdout.write(xyzStr+"\n");
            os.sys.stdout.write(velStr+"\n");
        except:
            os.sys.stderr.write("failed to export station "+stn+"\n");
        
if __name__ == "__main__":
    main()