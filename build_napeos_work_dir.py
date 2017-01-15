#!/usr/bin/python


import sys
import napeos_ops;
import gamit_ops;

def usage():
             
    print "USAGE:  build_work_dir YYYY DDD gamit/config/path"
    print
    sys.exit(1);

def main():
    
    if len(sys.argv) < 4:
        usage();
        sys.exit();
        
    year               = sys.argv[1]
    doy                = sys.argv[2]
    napeos_config_path = sys.argv[3]
    
    try:
        int(year)
        int(doy)
    except:
        print "DATE PARSE ERROR:  Check that input args 1 and 2 are YEAR and DOY!!!"
        usage();
        sys.exit()
    
    # regional solution
    if len(sys.argv) == 4:
        napeos_config = gamit_ops.build_gamit_config(napeos_config_path,year,doy)
        
    if len(sys.argv) == 5:
        napeos_config = gamit_ops.build_gamit_config(napeos_config_path,year,doy,sys.argv[4]);
    
    # do the deed ...
    napeos_ops.will_exe_napeos(napeos_config);
    
    print "cd",napeos_config['workPATH'];

        
if __name__ == "__main__":
    main()
