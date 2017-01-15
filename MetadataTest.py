import stnInfoLib;


def main():
    
    year = "1997";
    doy  = "207";
    
    # get station list path from gamit.config
    file = "../data/MetadataTest/stn_list.test";
    stnList = open(file,'r').readlines();

    # remove blank lines
    for stn in stnList[:]:   
        if len(stn.strip())==0:
            stnList.remove(stn);

    # initialize a station name registry to handle the name conflicts
    stnNameRegistry = stnInfoLib.StnNameRegistry().initWithStnList(stnList);
    
    # get list of station from the registry
    stnList = list(stnNameRegistry.stnIdSet);
    
    # init the metadata
    metadata = stnInfoLib                               \
                .StnMetadataCollection(stnNameRegistry) \
                .initFromStnList(stnList,year+'::'+doy);
    
    # iterate over each station
    for stn in metadata:
        
        # get the metadata for each object
        stn = stn.stnMetadataObj;
        
        # choose station info line for specific day and year
        stnInfoLine = stn.stnInfoObj.stnInfoForYearDoy(int(year),int(doy));
        
        # if there's a line to print the print it
        if stnInfoLine != None:
            stnInfoLine.Print();
            print stn.getName();
            
        

if __name__ == '__main__':
    main();