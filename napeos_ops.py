
import os;
import gamit_ops;
import NapeosMetadataMgr;
import shutil;
import archexpl;
import pyDate;
import glob;
import pickle;

NAPEOS_TEMPLATE = "/media/fugu/processing/src/napeos_OSX";

class NapeosException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def mk_work_dir(napeos_config):
    
    os.makedirs(napeos_config['workPATH']);
    
    # copy the template
    #shutil.copytree(NAPEOS_TEMPLATE,napeos_config['workPATH']);
    #print 'cp -a '+NAPEOS_TEMPLATE +' '+napeos_config['workPATH']
    os.system('cp -a '+NAPEOS_TEMPLATE+'/*' +' '+napeos_config['workPATH']);
    
    # copy the scenarios into working dir
    src = os.path.join(napeos_config['tablesROOT'],'sc');
    dst = os.path.join(napeos_config['workPATH'],'sc');
    sc_status = os.system("cp -a "+src+" "+dst);
    
    # copy the database into work dir
    src = os.path.join(napeos_config['tablesROOT'],'db');
    dst = os.path.join(napeos_config['workPATH'],'db');
    db_status = os.system("cp -a "+src+" "+dst);
    
def init_work_dir(napeos_config):
    
    # NOTE:  make sure data in the input directory first
    # CALL this just before exe_napeos!!
    
    # convert str to doubles
    year = float(napeos_config['year']);
    doy  = float(napeos_config['doy']);
    
    # make date object to compute yyyy mm dd
    date = pyDate.Date(year=year,doy=doy);
    
    year  = str(int(date.year));
    month = str(int(date.month));
    day   = str(int(date.day));
    
    #print napeos_config['workPATH'];
    #os.chdir(napeos_config['workPATH'])
    #os.system();
    #init_exe = 'cd '+napeos_config['workPATH']+';';
    init_exe = './init.sh'+' '+year+' '+month+' '+day;
    
    # OK, need to add this as first step of
    tmpRunFilePath = os.path.join(napeos_config['workPATH'],'runtmp');
    runFilePath    = os.path.join(napeos_config['workPATH'],'run.sh');
    
    # open the tempoary run file for writing
    tmpRunFile = open(tmpRunFilePath,'w');
    
    # open the actual run file for reading
    runFile    = open(runFilePath,'r');
    
    # write the shabang line
    tmpRunFile.write("#!/bin/bash\n");
    
    # write the init line
    tmpRunFile.write(init_exe+"\n");
    
    # write the rest of the lines from the actual run file
    tmpRunFile.writelines(runFile.readlines());
     
    # closem up
    tmpRunFile.close();
    runFile.close();
    
    # rename the modified run file to the actual
    os.rename(tmpRunFilePath, runFilePath); 
    
    # give the modified run script exe permisions
    os.chmod(runFilePath, 0777);
    
    # add trigger for other scripts
    doInitFilePath = os.path.join(napeos_config['workPATH'],'doInit.sh');
    
    # opent the file for writing;
    doInitFile = open(doInitFilePath,'w');
    
    # write the shabang line
    doInitFile.write("#!/bin/bash\n");
    
    # write the init line
    doInitFile.write(init_exe+"\n");
    
    # clean up
    doInitFile.close();
    
    # give the script exe permisions
    os.chmod(doInitFilePath, 0777);
    
    
def init_metadata(napeos_config):
    
    # construct the path for metadata export
    metadata_path = os.path.join(napeos_config['workPATH'],'metadata');
    
    # make date object to compute yyyy mm dd
    date = pyDate.Date(year=int(napeos_config['year']),\
                       doy=int(napeos_config['doy']));
                       
    # build the napeos metadata object
    mgr  = NapeosMetadataMgr.MetadataMgr(pyDate=date,\
                                         metadata=napeos_config['stnMetadata']);
                                    
    # export the metadata to the temp metadata directory
    mgr.exportMetadata(metadata_path,napeos_config['workPATH']);
    
    # finally, move the metadata into place
    wp = napeos_config['workPATH'];
    
    stn_file_src  = os.path.join(metadata_path,'station.dat');
    stn_file_dst  = os.path.join(wp,"db/tables/station.dat");
    shutil.copyfile(stn_file_src, stn_file_dst);
    
    site_file_src = os.path.join(metadata_path,'site.dat');
    site_file_dst = os.path.join(wp,'db/tables/site.dat');
    shutil.copyfile(site_file_src, site_file_dst);
    
    apr_file_src  = os.path.join(metadata_path,'gps.apr'); 
    apr_file_dst  = os.path.join(wp,'db/files/stat/gps.apr');
    shutil.copyfile(apr_file_src, apr_file_dst);
    
    otl_file_src  = os.path.join(metadata_path,'otl.dat');
    otl_file_dst  = os.path.join(wp,'db/files/stat/FES2004_CMC.blq');
    shutil.copyfile(otl_file_src, otl_file_dst);

def build_work_dir(napeos_config):
    
    # actually make the temp directory
    mk_work_dir(napeos_config);
    
    # fill it up with rinex files
    gamit_ops.get_rinex_files(napeos_config,'input');
    
    # get an sp3 file for the run
    #gamit_ops.get_sp3_files(napeos_config['workPATH'], napeos_config['sp3fileLIST'], 'input');
    
    if len(napeos_config['sp3fileLIST']) == 0:
        raise NapeosException('No sp3 file for to execute the run');
    
    #if len(napeos_config['sp3fileLIST']) != 1:
    #    raise NapeosException('Multiple sp3 files match sp3 type.  edit napeos.config for the run');
    
    # choose the first file in the list
    #sp3_file = napeos_config['sp3fileLIST'][0];
    
    for sp3_file in napeos_config['sp3fileLIST']:
        # set the source of the sp3 file
        src  = sp3_file;
        
        # set the dstination for the sp3 file
        dst  = os.path.join(napeos_config['workPATH'],'input/orbit.sp3.Z');
        
        # copy the sp3 file
        shutil.copyfile(src, dst);
    
    # choose orbit fixed or orbit estimation based
    # on exptType = baseline or relax
    link_bahn_sat(napeos_config);
        
def link_bahn_sat(napeos_config):
    
    # get the original starting directory
    pwd = os.curdir;
    
    # hate to hard code this but dont know better fix at the moment
    bahnFreePath = 'sc/REF_GPS/mode/bahn/IGSFREE';
    bahnFixPath = 'sc/REF_GPS/mode/bahn/IGSFIX';
    
    for path in (bahnFreePath, bahnFixPath):
        
        # local processing dir tables
        bahnDir = os.path.join(napeos_config['workPATH'],path);
        
        # relocate to the bahn directory
        os.chdir(bahnDir);
        
        # sestbl.RELAX or sestbl.BASELINE
        #src = os.path.join(bahnDir,'bahn_sat.dat.'+napeos_config['exptTYPE']);
        src = 'bahn_sat.dat.'+napeos_config['exptTYPE'];
        
        # gamit looks for "sestbl."
        #dest = os.path.join(bahnDir,'bahn_sat.dat');
        dest = 'bahn_sat.dat';
        
        # make soft link "ln -s"
        os.symlink(src, dest);
    
    # restore original directory
    os.chdir(pwd);
    
def run_napeos(napeos_config):
    
    # move to the working directory
    os.chdir(napeos_config['workPATH']);
    
    # either iterate or just execute the run
    if napeos_config['shouldIterate']:
        os.system('bin/iter.sh > solution/napeos.out');
    else:
        os.system('./run.sh > solution/napeos.out');       
    
def export_napeos_config(napeos_config):

    # name of the pkl file
    fileName = napeos_config['solnFileName']+'.pkl';
    
    # directory to store the pkl file
    exportPath = os.path.join(napeos_config['workPATH'],'solution');
    
    # the full file path of the pkl file
    pklFile = os.path.join(exportPath,fileName);
    
    # write the pickel     
    try:                  
        fid = open(pklFile,'wb')
        pickle.dump(napeos_config,fid,-1);
        fid.close
    except Exception, e:
        print "PICKLE ERROR:  Could not write napeos pkl to file: "+pklFile;  
        print e
    
def will_exe_napeos(napeos_config):
    
    build_work_dir(napeos_config);
    init_metadata(napeos_config);
    init_work_dir(napeos_config);
    
    # keep this as last action (!)
    export_napeos_config(napeos_config);
    
def did_exe_napeos(napeos_config):

    copy_solution(napeos_config);
    rm_work_dir(napeos_config)

def exe_napeos(napeos_config):
    
    # everything needed to setup
    will_exe_napeos(napeos_config);
    
    # just exe ./run.sh
    run_napeos(napeos_config);
    
    # cleanup, copy solutions, rm etc
    did_exe_napeos(napeos_config);
        
def copy_solution(napeos_config):
    
    # convert str to doubles
    fileName = napeos_config['solnFileName'];
    
    # make sure that the solution destination actually exists
    if not os.path.isdir(napeos_config['projsolnPATH']):
        # if not then make it
        os.makedirs(napeos_config['projsolnPATH']);
    
    # copy the orbit if type is relax
    if napeos_config['exptTYPE'] == 'RELAX':
        
        sp3Src = os.path.join(napeos_config['workPATH'],'solution/orbit.sp3.Z');        
        sp3Dst = os.path.join(napeos_config['projsolnPATH'],fileName+'.sp3.Z');
        
        if os.path.isfile(sp3Src):
            os.system('mv -f '+sp3Src + ' ' + sp3Dst);
     
    # always copy over the SINEX file to the archive   
    snxSrc = os.path.join(napeos_config['workPATH'],'solution/bahnfix.snx.Z');
    snxDst = os.path.join(napeos_config['projsolnPATH'],fileName+'.snx.Z');
    
    # check if the SINEX file exists if so move it over to archive
    if os.path.isfile(snxSrc):
        os.system('mv -f '+snxSrc +' ' + snxDst);
        
    # always copy over the standard out file to the archive   
    outSrc = os.path.join(napeos_config['workPATH'],'solution/napeos.out.Z');
    outDst = os.path.join(napeos_config['projsolnPATH'],fileName+'.out.Z');
    
    # check if the SINEX file exists if so move it over to archive
    if os.path.isfile(outSrc):
        os.system('mv -f '+outSrc +' ' + outDst);
    
    # move over anything else that's left
    solnSrc = os.path.join(napeos_config['workPATH'],'solution/*');
    solnDst = napeos_config['projsolnPATH'];
    solution_files = glob.glob(solnSrc);
    for file in solution_files:
        os.system('mv -f '+file+ ' '+solnDst);
        
def rm_work_dir(napeos_config):
    rm_cmd = 'rm -rf '+napeos_config['workPATH'];
    print rm_cmd;
    os.system(rm_cmd);
    
if __name__ == "__main__":
    
    # test run
    
    year = 2003;
    doy  = 319;
    file     = "/media/fugu/processing/projects/osuGlobal/napeos/orbit/napeos.config";
    stn_list = "/media/fugu/processing//projects/osuGLOBAL/shared/networks/orbit/osuGlobal6/stn_list.2003.314";
    stn_list = "/media/fugu/processing/projects/osuGLOBAL/napeos/orbit/networks/stn_list.2003.319";
    
    napeos_config = gamit_ops.build_gamit_config(file,year,doy,stn_list);
    exe_napeos(napeos_config)

        