import stnInfoLib;
import pyDomes;
import os;
import archexpl;
import re;
import pyDate;
import pyOTL;

ATX_FILE_PATH = "$HOME/db/files/atx/gps.atx";
APR_FILE_PATH = "$HOME/db/files/stat/gps.apr";

def mk2dstr(d):
    dstr = None;
    if d < 10:
        dstr = "0"+str(d);
    else:
        dstr = str(d);
        
    return dstr

class ParseException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class MetadataMgr():
    
    def __init__(self,**kwargs):
        
        self.shouldUseDate = False;
        
        # these are tempate file paths for inclusion in station.dat
        self.atxFilePath   = ATX_FILE_PATH;
        self.aprFilePath   = APR_FILE_PATH;
        
        # this could be real file path to domes def file
        self.domesFilePath = None;
        
        # init stn name registry to manage the name conflicts
        self.stnNameRegistry = None;
        
        # metadata collection
        self.metadataCollection = None;
        
        # hold the date info we might need
        self.date = None;
        
        # parse args
        for key in kwargs:
            
            arg = kwargs[key];
            #key = key.lower();
            
            if key == 'atxFilePath':
                self.atxFilePath = arg;
            elif key == 'aprFilePath':
                self.arpFilePath = arg;
            elif key == 'domesFilePath':
                self.domesFilePath = arg;
            elif key == 'pyDate':
                self.date = arg;
                self.shouldUseDate = True;
            elif key == 'metadata':
                self.metadataCollection = arg;
            else:
                os.sys.stderr.write('key-word '+key+' not recognized\n');
                
        # OK, now init the domes mgr with whatever domesFilePath you have
        try:
            self.domesMgr = pyDomes.Domes(self.domesFilePath);
        except pyDomes.domesException, e:
            print e;
            os.sys.stderr.write("Error initializing domes manager.  Will proceed with default domes manager\n");
            self.domesMgr = pyDomes.Domes();
                    
    def initWithStnList(self,stnList):
        
        # construct a date if there is one
        if self.shouldUseDate:
            dateStr = str(self.date.year)+"::"+str(self.date.doy);
        else:
            dateStr = None;
            
        # remove any station that doesn't have rnx file for the day if date give
        if self.shouldUseDate:
            for stnId in stnList[:]:
                
                try:
                    namespace,stnName = stnId.split("::");
                except:
                    os.sys.stderr.write("could not parse: "+ stnId+"\n");
                    continue
                
                if not archexpl.exists_rnx_for_stn_on_date(namespace, stnName, self.date.year, self.date.doy):
                    os.sys.stderr.write("NAPEOS METADATA MGR: no RINEX file for "\
                                        +stnId+" on "+str(self.date.year)+" "+str(self.date.doy)+"\n");
                    stnList.remove(stnId);
        
        # init the metadata
        self.metadataCollection = stnInfoLib        \
                    .StnMetadataCollection()        \
                    .initFromStnList(stnList,dateStr);
                    
        return self;
        
    def writeStnDat(self,dst=None):
        
        lines= list();
        lineCount = 0;
        
        if dst == None:
            dst = os.sys.stdout;
            
        indx = 1;
        
        for stn in self.metadataCollection:
        
            # drill down
            stn = stn.stnMetadataObj;
        
            # set the station name we're working with
            stnName = stn.getName().upper();
            
            #print "NAPEOS METADATA MGR: exporting station "+stnName;
            
            # add the station to the domes mgr if it's not already defined
            if not self.domesMgr.containsStnId(stnName):
                stnName,domesNumber = self.domesMgr.addStn(stnName);
            else:
                domesNumber = self.domesMgr.domesForStnId(stnName);
                
            # control to print "S" or "-"
            isFirstLine = True;
            
            # row header
            tag = "S";
            
            # check if date is defined.  If so, then just choose 
            # the metadata line associated with the date
            lineSrc = stn.stnInfoObj;
            if self.shouldUseDate:
                lineSrc = list();
                lineSrc.append(stn.stnInfoObj.stnInfoForYearDoy(self.date.year,self.date.doy));
            
                    # for each line in stnInfoObj ...
            for line in lineSrc:
                
                #print "NAPEOS METADATA MGR: processing station info line for station "+stnName;
                #print line;
                
                if line == None:
                    os.sys.stderr.write("NAPEOS METADATA MGR:  no station.info for "\
                                        +stnName             +" on "                \
                                        +str(self.date.year) + ", "                 \
                                        +str(self.date.doy)  +"\n");
                    continue;
                
                # adjust these dates since napeos is looking at GPS rather than UTC
                # 1998 345 00:00:00 UTC is actually 1998 344 23:59:43 in GPS time
                # but since we chose the line using UTC there is no problem here
                startDate = line.startDate - 1;
                stopDate  = line.stopDate  + 1;
                
                startDateStr = "%4d/%2s/%2s-00:00:00.000000" % (startDate.year,mk2dstr(startDate.month),mk2dstr(startDate.day));
                stopDateStr  = "%4d/%2s/%2s-00:00:00.000000" % (stopDate.year, mk2dstr(stopDate.month), mk2dstr(stopDate.day));
                rxVers = line.rx.vers;
                      
                stnDatLine = "%1s %4s GPS %10s %4d %9s %4s  0 %26s  0 %26s  %6.4f  %6.4f  %6.4f %-15s %4s %20s %-20s %-5s %-11s %-80s %-50s 1 %80s %-80s %10.2f %10.2f" % (tag,stnName.upper(),"",indx, domesNumber, stnName.upper(),startDateStr,stopDateStr, line.ant.n, line.ant.e, line.ant.ht, line.ant.type, line.ant.dome[0:4], line.ant.sn, line.rx.type,line.rx.sn[0:5], line.rx.vers[0:11], self.aprFilePath[0:80], "auto generated by info2dat.py", " ", self.atxFilePath[0:80],1575.42,1227.60);
                
                lines.append(stnDatLine);
                
                lineCount = lineCount +1;
                
                if isFirstLine:
                    tag = "-";
                    
            indx = indx + 1;
            
        dst.write("NSTADB    "+str(lineCount)+"\n");
        for line in lines:
            dst.write(line+"\n");
        dst.write("endlist"+"\n");
       
    def writeCrd(self,dst=None):
        
        if dst == None:
            dst = os.sys.stdout;
            
        
        dst.write('STATION COORDINATES AT EPOCH  2002.0\n')
    
        for stn in self.metadataCollection:
            
            # drill down
            stn = stn.stnMetadataObj;
        
            # set the station name we're working with
            stnId = stn.getName().upper();
                                
            # every line has at least this
            x     = stn.aprObj.X;
            y     = stn.aprObj.Y;
            z     = stn.aprObj.Z;
            
            sigX       = stn.aprSigmaObj.sigX;
            sigY       = stn.aprSigmaObj.sigY;
            sigZ       = stn.aprSigmaObj.sigZ;
                            
            # make sure sigmas are well behaved
            if sigX >= 10.0:
                sigX = 9.999;
            if sigY >= 10.0:
                sigY = 9.999;
            if sigZ >= 10.0:
                sigZ = 9.999; 
            
            if self.domesMgr.containsStnId(stnId):
                domesNumber = self.domesMgr.domesForStnId(stnId);
            else:
                stnName,domesNumber = self.domesMgr.addStn(stnId);
                
            self.__printAsCrd(dst,domesNumber,stnId,x,y,z,sigX,sigY,sigZ);
            
    def __printAsCrd(self,dst,domesNumber,stnId,x,y,z,sigX,sigY,sigZ):
        
            xyzStr =  "%9s %4s %9s     GPS %4s                  %12.3f %12.3f %12.3f %5.3f %5.3f %5.3f OSU" % (domesNumber, stnId.upper(), domesNumber, stnId.upper(), x, y, z, sigX, sigY, sigZ)
            velStr =  "%9s %4s %9s         %4s                  %12.3f %12.3f %12.3f %5.3f %5.3f %5.3f OSU" % (domesNumber, "", "", "", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)    
        
            dst.write(xyzStr+"\n");
            dst.write(velStr+"\n");
            
            
    def writeOTL(self,dst,workDir='./'):
        
        outFilePath = dst;
        if os.path.isdir(dst):
            outFilePath = os.path.join(dst,'otl.blq');
        
        pyotl = pyOTL.pyOTL(                                 \
                            date=self.date,                  \
                            work_dir=workDir,                \
                            otl_output_file=outFilePath,     \
                            metadata=self.metadataCollection,\
                            pyDomes=self.domesMgr            \
                           ) 
        pyotl.computeOTL();
            
    def writeSiteDat(self,dst=None):
        
        if dst == None:
            dst = os.sys.stdout;
            
        numStns = self.metadataCollection.size();    
        dst.write("SITEDB    "+str(numStns)+"\n");
            
        for stn in self.metadataCollection:
            
            stn = stn.stnMetadataObj;
            
            stnName = stn.getName().upper();
            
            # get a domes number for the station
            if self.domesMgr.containsStnId(stnName):
                domesNumber = self.domesMgr.domesForStnId(stnName);
            else:
                stnName,domesNumber = self.domesMgr.addStn(stnName);
                
            # trim the domes number down
            domesNumber = str(domesNumber).strip();
            domesNumber = domesNumber[0:5];
            
            siteStr = " %4s %-17s %-11s %7.3f %7.3f %4s" % (domesNumber,"","USA",0.000,0.000,"NOAM")
            dst.write(siteStr+"\n");
        
        dst.write("endlist\n");
        
    def exportMetadata(self,dst,tmpWorkDir="./"):
        
        # make sure to get the full path 
        dst = os.path.abspath(os.path.expanduser(dst));
        
        #  make sure dst exists
        if not os.path.isdir(dst):
            try:
                # if not then make it
                os.makedirs(dst);
            except Exception, e:
                raise ParseException("Export directory: "+dst+" does not exist nor could be made");
        
        # do it
        self.writeStnDat ( open( os.path.join( dst, "station.dat" ), 'w' ) );
        self.writeCrd    ( open( os.path.join( dst, "gps.apr"     ), 'w' ) );
        self.writeSiteDat( open( os.path.join( dst, "site.dat"    ), 'w' ) );
        
        self.writeOTL(os.path.join(dst,"otl.dat"),tmpWorkDir);
        
            
if __name__ == '__main__':
    
    year = 1998;
    doy  = 345;
    
    stnListFile = "../data/NapeosMetadataMgr/stn_list_anet_1998_345.txt";
    stnList     = open(stnListFile,'r').readlines();
    stnList     = [s.strip() for s in stnList[:]]
    
    date = pyDate.Date(year=year,doy=doy)
    mgr  = MetadataMgr(pyDate=date).initWithStnList(stnList);

    mgr.exportMetadata('../data/NapeosMetadataMgr/out');
    
            
            