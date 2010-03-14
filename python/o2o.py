#!/usr/bin/env python

#########################################################################
#
# HCAL o2o script
#
# by Gena Kukartsev, December 10, 2009
#
# Usage: ./o2o.py
# base_dir must contain: o2o.py, query .sql files, dbwrite_o2o_template.py
#
# Pararmeters: see section below marked "parameters" for all changeable parameters
#
#########################################################################

import os
import sys
import subprocess

#
#_____ parameters _______________________________________________________
#
#
mode = 'online'
input_pool_connect_string = "oracle://CMSDEVR_LB/CMS_COND_HCAL"    # read list of tags/iovs from
output_pool_connect_string = "oracle://CMSDEVR_LB/CMS_COND_HCAL"   # where to write changes
pool_auth_path = "/nfshome0/popcondev/conddb"
pool_logconnect = "sqlite_file:log.db"                   # pool log DB file
omds_accessor_string = "occi://CMS_HCL_APPUSER_R@anyhost/cms_omds_lb?PASSWORD=HCAL_Reader_44"
base_dir = "."
output_dir = "."
o2o_tag_list_file = "o2o_tag_list.txt"
python_popcon_template_file = "dbwrite_o2o_template.py"
python_popcon_file = "dbwrite_o2o.py"
#
# dropbox config (optional)
#use_dropbox = 'true'
use_dropbox = 'false'
dropbox_dir = "./dropbox"
dropbox_destination_db = 'oracle://cms_orcon_prod/CMS_COND_31X_HCAL'
dropbox_comment = 'generated by CaloOnlineTools/HcalOnlineDb/test/o2o.py script'
#mode = 'online_dropbox'
#mode = 'offline_development'
#
#_____ end of parameters ______________________________________________

#
#_____ define helper functions __________________________________________
#
def make_popcon_config_file(filename):
    py_templ_file = open(base_dir+"/"+python_popcon_template_file)
    py_file = open(str(filename), "w")
    for line in py_templ_file:
        line=line.replace('CONNECT_STRING', output_pool_connect_string)
        line=line.replace('POOL_AUTH_PATH', pool_auth_path)
        line=line.replace('CONDITION_TYPE', condition_type)
        line=line.replace('OMDS_CONDITION_TAG', tag)
        line=line.replace('OMDS_IOV', str(iov))
        line=line.replace('OMDS_ACCESSOR_STRING', omds_accessor_string)
        line=line.replace('OMDS_QUERY', query)
        line=line.replace('POOL_LOGCONNECT', pool_logconnect)
        line=line.replace('POOL_RECORD', pool_record)
        line=line.replace('POOL_OUTPUT_TAG', tag)
        line=line.replace('POOL_IOV', str(pool_iov))
        py_file.write(line)
    py_file.close()

#
# HCAL conditions have a rigid naming scheme:
# RECORD_VERSION_USE, e.g. HcalChannelQuality_v1.00_mc
# or
# RECORD_UNIT_VERSION_USE, e.g. HcalPedestals_ADC_v2.31_offline
#
def guess_condition_from_tag(tagname):
    guessed_type = tagname[0:tagname.find("_")]
    # FIXME: gak is a temporary debugging case
    if guessed_type == "gak":
        guessed_type = "HcalChannelQuality"
        guessed_query_file_name = base_dir+"/HcalChannelQuality.sql"
        guessed_pool_record = "HcalChannelQualityRcd"

    elif guessed_type == "HcalDcsValues":
        guessed_type = "DcsValues"
        guessed_query_file_name = base_dir+"/HcalDcsValues.sql"
        guessed_pool_record = "HcalDcsRcd"

    elif guessed_type == "HcalChannelQuality":
        guessed_type = "ChannelQuality"
        guessed_query_file_name = base_dir+"/HcalChannelQuality.sql"
        guessed_pool_record = "HcalChannelQualityRcd"

    elif guessed_type == "HcalLutMetadata":
        guessed_type = "LutMetadata"
        guessed_query_file_name = base_dir+"/HcalLutMetadata.sql"
        guessed_pool_record = "HcalLutMetadataRcd"

    elif guessed_type == "HcalRespCorrs":
        guessed_type = "RespCorrs"
        guessed_query_file_name = base_dir+"/HcalRespCorrs.sql"
        guessed_pool_record = "HcalRespCorrsRcd"

    elif guessed_type == "HcalValidationCorrs":
        guessed_type = "ValidationCorrs"
        guessed_query_file_name = base_dir+"/HcalValidationCorrs.sql"
        guessed_pool_record = "HcalValidationCorrsRcd"

    elif guessed_type == "HcalPedestals":
        guessed_type = "Pedestals"
        guessed_query_file_name = base_dir+"/HcalPedestals.sql"
        guessed_pool_record = "HcalPedestalsRcd"

    elif guessed_type == "HcalPedestalWidths":
        guessed_type = "PedestalWidths"
        guessed_query_file_name = base_dir+"/HcalPedestalWidths.sql"
        guessed_pool_record = "HcalPedestalWidthsRcd"

    elif guessed_type == "HcalGains":
        guessed_type = "Gains"
        guessed_query_file_name = base_dir+"/HcalGains.sql"
        guessed_pool_record = "HcalGainsRcd"

    elif guessed_type == "HcalGainWidths":
        guessed_type = "GainWidths"
        guessed_query_file_name = base_dir+"/HcalGainWidths.sql"
        guessed_pool_record = "HcalGainWidthsRcd"

    elif guessed_type == "HcalQIEData":
        guessed_type = "QIEData"
        guessed_query_file_name = base_dir+"/HcalQieData.sql"
        guessed_pool_record = "HcalQIEDataRcd"

    elif guessed_type == "HcalElectronicsMap":
        guessed_type = "ElectronicsMap"
        guessed_query_file_name = base_dir+"/HcalEmap.sql"
        guessed_pool_record = "HcalElectronicsMapRcd"

    elif guessed_type == "HcalZSThresholds":
        guessed_type = "ZSThresholds"
        guessed_query_file_name = base_dir+"/HcalZSThresholds.sql"
        guessed_pool_record = "HcalZSThresholdsRcd"

    elif guessed_type == "HcalL1TriggerObjects":
        guessed_type = "L1TriggerObjects"
        guessed_query_file_name = base_dir+"/HcalL1TriggerObjects.sql"
        guessed_pool_record = "HcalL1TriggerObjectsRcd"

    else:
        print "Cannot guess condition type"

    return {'condition_type':guessed_type,
            'query_file_name':guessed_query_file_name,
            'pool_record':guessed_pool_record}

#_____ get list of IOVs that need updating, from comparison of OMDS and ORCON
def get_tags(tag_list_file_name):
    try:
        tag_list_file = open(tag_list_file_name)
    except:
        print "Cannot open the file with the list of tags, exiting..."
        sys.exit()
    tag_list = []
    for line in tag_list_file:
        tag_list . append(line)
    tag_list_file.close()
    #tags = subprocess.Popen(["cat", tag_list], stdout=subprocess.PIPE).communicate()[0]
    return tag_list

#_____ get list of IOVs that need updating, from comparison of OMDS and ORCON
def get_iovs(tag, input_pool_connect_string, mode):
    result = "fail" # default
    newtag = False  # default
    # nominal mode of operations
    if mode == "online" or mode == "online_dropbox":
        try:
            iovs = subprocess.Popen(["./xmlToolsRun", "--list-iovs-for-o2o", "--tag-name", tag, "--pool-connect-string", input_pool_connect_string, "--pool-auth-path", pool_auth_path], stdout=subprocess.PIPE).communicate()[0]
            iov_list = iovs.splitlines()
            result = "success"
        except:
            print "ERROR: Cannot get the IOV update list for tag", tag+". This tag will not be updated. Now continue to the next tag..."
            iov_list=[]
            result = "fail"

    # script development mode, DB interfaces substituted with dummies
    if mode == "offline_development":
        #iovs = subprocess.Popen(["cat", tag+"_iov_to_update.devel"], stdout=subprocess.PIPE).communicate()[0]
        try:
            iov_list_file = open(base_dir+"/o2o/"+tag+"_iov_to_update.devel")
        except:
            print "ERROR: Cannot open file with the IOV list for tag", tag+". This tag will not be updated. Now continue to the next tag..."
            result = "fail"
        result = "success"
        iov_list = []
        for line in iov_list_file:
            iov_list . append(line.strip())
        iov_list_file.close()
    # now parse iov_list.
    # May contain various important output. Prefix defines the type of instruction.
    # IOVs start with O2O_IOV_LIST:
    # CONNECTION ERROR: indicates problems with connection to Pool and invalidates
    #                   the IOV list
    iovs=[]
    for line in iov_list:
        line_stripped = line.strip()
        if line.strip()[0:13] == "O2O_IOV_LIST:":
           iovs.append(line.lstrip("O2O_IOV_LIST:"))
        if line_stripped[0:line_stripped.find(":")] == "CONNECTION ERROR":
            result = "fail_connect"
        if line_stripped[0:line_stripped.find(":")] == "NEW_POOL_TAG_TRUE":
            newtag = True
    return {'iovs':iovs,
            'result':result,
            'newtag':newtag}

#_____ run PopCon
def run_popcon():
    status = "fail"
    try:
        print "iov=", iov
        if mode == "online" or mode == "online_dropbox":
            subprocess.call(["cmsRun", str(python_popcon_file)])
        else:
            print "In online mode would run Popcon now:", "cmsRun", str(python_popcon_file)
        status = "success"
    except OSError:
        print "Cannot execute cmsRun. Further processing of this tag is stopped, going to the next tag..."
        #break
    except:
        print "Cannot execute cmsRun. Further processing of this tag is stopped, going to the next tag..."
        #break
    
    #
    #_____ copy to the Dropbox area (optional)
    #
    if use_dropbox == "true" or use_dropbox == "True" or use_dropbox == "TRUE":
        try:
            retcall_meta = subprocess.call(['mv', str(output_dir)+'/'+str(dropbox_file_name_prefix)+'.txt', str(dropbox_dir)+'/'])
            retcall_sql    = subprocess.call(['mv', str(output_dir)+'/'+str(dropbox_file_name_prefix)+'.sql', str(dropbox_dir)+'/'])
        except:
            print "ERROR: Cannot copy files to the dropbox area"

    return {'status':status}
#
#_____ end of helper functions __________________________________________


tags = get_tags(base_dir+"/"+o2o_tag_list_file)
for tag_name in tags:
    # FIXME: do we need this?
    tag = tag_name.strip()

    #
    #_____ guess condition from tag name
    #
    guessed_condition = guess_condition_from_tag(tag)
    condition_type    = guessed_condition['condition_type']
    query_file_name   = guessed_condition['query_file_name']
    pool_record       = guessed_condition['pool_record']

    print ""
    print "Processing tag:", tag
    print "Condition type:",condition_type 

    #
    #_____ read SQL query from a file
    #
    query_file = open(query_file_name, "r")
    query = query_file.read()
    query_file.close()
    
    #
    #_____ Popcon Dropbox requirements (optional)
    #
    if use_dropbox == "true" or use_dropbox == "True" or use_dropbox == "TRUE":
        #output_pool_connect_string = "sqlite_file:testDropbox.db"
        dropbox_file_name_prefix = str(output_dir)+"/"+str(tag)
        output_pool_connect_string = 'sqlite_file:'+str(dropbox_file_name_prefix)+'.db'
        dropbox_txt_file_name = str(dropbox_file_name_prefix)+".txt"
        dropbox_txt_file = open(dropbox_txt_file_name, "w")
        dropbox_txt_file.write('destDB '+dropbox_destination_db+'\n')
        dropbox_txt_file.write('inputtag\n')
        dropbox_txt_file.write('tag '+str(tag)+'\n')
        dropbox_txt_file.write('since\n')
        dropbox_txt_file.write('till\n')
        dropbox_txt_file.write('usertext '+str(dropbox_comment)+'\n')
        dropbox_txt_file.close()
    
    #
    #_____ loop over IOV to copy
    #
    #FIXME: move the binary inside the popcon job, and try multiple IOV
    gotten_iovs = get_iovs(tag, input_pool_connect_string, mode)

    # stop processing current tag if IOVs were not obtained
    if (gotten_iovs['result'] != "success"):
        if (gotten_iovs['result'] == "fail_connect"):
            print "Problems connecting to", input_pool_connect_string
            print "Unable to process tag", tag_name, "continuing to the next tag..."
        continue
    
    o2o_iovs = gotten_iovs['iovs']
    isnewtag = gotten_iovs['newtag'] # is this a new POOL tag?
    i = 0
    for line in o2o_iovs:
        i = i+1
        iov = int(line)
        pool_iov = iov
        
        if i==1: # first IOV to update may be a special case
            if isnewtag:
                print "Creating a new offline tag: ", tag_name
                if condition_type == "DcsValues" and iov != 1:
                    print "DCS values: The first IOV in the online tag is ", iov
                    print "DCS values: Adding default DCS set values to the offline"
                    print "DCS values: tag for IOVs 1 - ", iov-1
                    print "DCS values: because first IOV in the offline tag must always be 1."
                    query_save = query
                    query_file_name = query_file_name+".default"
                    query_file = open(query_file_name, "r")
                    query = query_file.read()
                    query_file.close()
                    pool_iov = 1
                    make_popcon_config_file(python_popcon_file)
                    run_result = run_popcon()
                    query = query_save
                    pool_iov = iov
                    if run_result['status'] != "success":
                        break
                else:
                    pool_iov = 1 # force the first IOV in offline tag to be 1 by default
                
        make_popcon_config_file(python_popcon_file)
        run_result = run_popcon()
        if run_result['status'] != "success":
            break

