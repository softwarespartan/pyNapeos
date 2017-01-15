#!/usr/bin/python


import sys
import gamit_ops
import napeos_ops

def usage():
             
    print "USAGE:  g2_napeos YYYY DDD gamit/config/path [stn/list/path]"
    print "USAGE:  This program is meant to be launched by g2_admin"
    sys.exit(1);

def main():
    
    if len(sys.argv) < 4:
        usage()
    
    year              = sys.argv[1]
    doy               = sys.argv[2]
    napeos_config_path = sys.argv[3]
    
    try:
        int(year)
        int(doy)
    except:
        print "DATE PARSE ERROR:  Check that input args 1 and 2 are YEAR and DOY!!!"
        sys.exit()
    
    if len(sys.argv) == 4:
        # regional solution
        napeos_config = gamit_ops.build_gamit_config(napeos_config_path,\
                                                    year,doy)
        
        # do the deed ...
        napeos_ops.exe_napeos(napeos_config)
        
    elif len(sys.argv) == 5:
        
        stationlistPATH = sys.argv[4]

        # multi-network solution
        napeos_config = gamit_ops.build_gamit_config(napeos_config_path,\
                                                    year,doy,         \
                                                    stationlistPATH)
        
        # start the majik ...
        napeos_ops.exe_napeos(napeos_config)
        
    else:  
        usage()
        sys.exit()
        
    # run globk_ops
#    globk_config_path = os.path.join(os.path.dirname(napeos_config_path),'globk.config')
#    globk_ops.run_globk(globk_config_path, year, doy)
        
if __name__ == "__main__":
    main()
