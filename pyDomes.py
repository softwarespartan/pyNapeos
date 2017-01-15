
import re;
import os;
import sys;
import random;


class domesException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def parseStnId(stnId):
    
    if len(stnId) < 4:
        raise domesException("station identifier "+stnId+" must be at least 4 char");
    
    stnId = stnId.lower();
    
    if len(stnId) == 4:
        return stnId;   
    
    elif stnId.endswith('_gps'):
        return stnId[0:4];
    
    elif len(stnId) == 9 and stnId[3:5] == "::":
        return stnId[5:];
    
    else:
        raise domesException("station identifier "+ stnId + "is invalid");


class Domes():

    def __init__(self, domesFile=None):
        
        self.domes = dict();
        self.file  = None;
        
        if domesFile != None:
            
            # save for later export
            self.file = domesFile;
            
            
            if os.path.isfile(domesFile):
                # parse what's in the file now
                self.parseDomesFile(domesFile);
              
    def parseDomesFile(self,domesFile):
        
        # make sure the file exists before try to parse it
        if not os.path.isfile(domesFile):
            raise domesException("file "+domesFile+" does not exist");
                        
        for line in open(domesFile,'r'):
            
            # remove the white spaces from both ends
            line = line.strip();
        
            # split the line into two parts (hopefully)
            lineParts = re.split('\W+',line);
            
            # check that the line is two parts
            if len(lineParts) != 2:
                os.sys.stderr.write("line: "+line+ " has invalid format and is being rejected\n");
                continue;
            
            # assign the items
            stnId   = lineParts[0];
            domesNumber = lineParts[1].upper();
            
            # try to parse the station identifyer
            try:
                stnId = parseStnId(stnId);
            except domesException, err:
                print err
                os.sys.stderr.write('could not parse station id for line: '+ line+"\n");
                continue;
            
            self.addStnWithDomes(stnId, domesNumber); 
        
    def size(self):
        return len(self.domes.keys());
    
    def containsStnId(self,stnId):
        
        # make sure the stnId will match
        stnId = parseStnId(stnId);
        
        # just check for the key in dict
        return self.domes.has_key(stnId);
    
    def containsDomes(self, domesNumber):
        
        # make sure the domesNumber is all upper case
        domesNumber = domesNumber.upper();
        
        # just check the values of all station ids
        return domesNumber in self.domes.values();
    
    def generateDomesNumber(self):
        
        d5=  str(random.randint(0, 9)) \
           + str(random.randint(0, 9)) \
           + str(random.randint(0, 9)) \
           + str(random.randint(0, 9)) \
           + str(random.randint(0, 9));
        
        d = d5+"M"+"001";
        
        while self.containsDomes(d):
            
            d5=  str(random.randint(0, 9)) \
               + str(random.randint(0, 9)) \
               + str(random.randint(0, 9)) \
               + str(random.randint(0, 9)) \
               + str(random.randint(0, 9));
        
            d = d5+"M"+"001";
            
        return d;
               
    def addStn(self,stnId):
        
        # for good measure
        stnId = parseStnId(stnId);
        
        # make sure that the station does not already exist!
        if self.containsStnId(stnId):
            raise domesException("stnId "+ stnId                  \
                                 + " already exists with DOMES# " \
                                 + self.domesForStnId(stnId)); 
        
        # assign some random domes number
        domesNumber = self.generateDomesNumber();
        self.domes[stnId] = domesNumber;
        
        return stnId,domesNumber;
        
    def addStnWithDomes(self,stnId,domesNumber):
        
        # for good measure
        stnId = parseStnId(stnId);
        
        # make sure that the station does not already exist!
        if self.containsStnId(stnId):
            raise domesException("stnId "+ stnId                   \
                                 + " already exists with DOMES# "  \
                                 + self.domesForStnId(stnId)); 
        
        # make sure that the domesnumber does not already exist!
        if self.containsDomes(domesNumber):
            raise domesException("DOMES # "                     \
                                 +domesNumber+                  \
                                 " already exists for station " \
                                 + self.stnIdForDomes(domesNumber));
        
        self.domes[stnId] =  domesNumber;
        
        
    def stnIdForDomes(self,domesNumber):

        # do the reverse look up
        for key in self.domes.keys():
            if self.domes[key] == domesNumber:
                return key;
            
        return None;
        
    def domesForStnId(self,stnId):
        
        stnId = parseStnId(stnId);
        if self.domes.has_key(stnId):
            return self.domes[stnId];
        else:
            return None;
    def export(self,exportPath=None):
        
        # make sure that there is some file to export to 
        if self.file == None and exportPath == None:
            raise domesException(" no path for export");
        
        dst = None;
        if exportPath != None:
            dst = exportPath;
        else:
            dst = self.file;
        
        fid = open(dst,'w');
        
        for key in self.domes.keys():
            fid.write(key + " " + self.domes[key]+"\n");
            
        fid.close();
    
if __name__ == '__main__':
    
    d = Domes("../data/pyDomes/domes.txt");
    print d.size();
    
    #d.addStn("fucd");
    #d.addStn("igs::zier")
    #d.addStn("NICc_GPS")
    
    print d.size()
    
    for key in d.domes.keys():
        print key, d.domes[key];
        
    d.export();