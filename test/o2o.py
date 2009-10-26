#!/usr/bin/env python

import os
import sys
import subprocess

_n_argv = len(sys.argv)
if _n_argv == 2:
    tag_name = sys.argv[1]
    print "Using tag name: "+tag_name
else:
    print "No tag name specified, exiting..."
    sys.exit(-1)

# FIXME: transfer parameters via command line
# FIXME: output_dir should probably be a temp dir
#
#_____ parameters __________________________________________
#
input_pool_connect_string = "sqlite:test_o2o.db"
pool_logconnect = "sqlite:log.db"
omds_accessor_string = "occi://CMS_HCL_APPUSER_R@anyhost/cms_omds_lb?PASSWORD=HCAL_Reader_44"
base_dir = "."
output_dir = "."
dropbox_dir = "./dropbox"
python_popcon_template_file = "dbwrite_o2o_template.py"
python_popcon_file = "dbwrite_o2o.py"
destination_db = 'oracle://cms_orcon_prod/CMS_COND_31X_HCAL'
dropbox_comment = 'generated by CaloOnlineTools/HcalOnlineDb/test/o2o.py script'
#
#____________________________________________________________

# FIXME: do we need this?
tag = tag_name

#
#_____ define helper functions
#
def make_popcon_config_file(filename):
    py_templ_file = open(base_dir+"/"+python_popcon_template_file)
    py_file = open(str(filename), "w")
    for line in py_templ_file:
        line=line.replace('CONNECT_STRING', output_pool_connect_string)
        line=line.replace('CONDITION_TYPE', condition_type)
        line=line.replace('OMDS_CONDITION_TAG', tag)
        line=line.replace('OMDS_IOV', str(iov))
        line=line.replace('OMDS_ACCESSOR_STRING', omds_accessor_string)
        line=line.replace('OMDS_QUERY', query)
        line=line.replace('POOL_LOGCONNECT', pool_logconnect)
        line=line.replace('POOL_RECORD', pool_record)
        line=line.replace('POOL_OUTPUT_TAG', tag)
        line=line.replace('POOL_IOV', str(iov))
        py_file.write(line)
    py_file.close()

def guess_condition_from_tag(tagname):
    guessed_type = tagname[0:tagname.find("_")]
    # FIXME: gak is a temporary debugging case
    if guessed_type == "gak":
        guessed_type = "HcalChannelQuality"

    if guessed_type == "HcalChannelQuality":
        guessed_type = "ChannelQuality"
        guessed_query_file_name = base_dir+"/HcalChannelQuality.sql"
        guessed_pool_record = "HcalChannelQualityRcd"

    return {'condition_type':guessed_type,
            'query_file_name':guessed_query_file_name,
            'pool_record':guessed_pool_record}

#
#_____ guess condition from tag name
#
guessed_condition = guess_condition_from_tag(tag)
condition_type    = guessed_condition['condition_type']
query_file_name   = guessed_condition['query_file_name']
pool_record       = guessed_condition['pool_record']

#
#_____ read SQL query from a file
#
query_file = open(query_file_name, "r")
query = query_file.read()
query_file.close()

#
#_____ Popcon Dropbox requirements
#
#output_pool_connect_string = "sqlite:testDropbox.db"
dropbox_file_name_prefix = str(output_dir)+"/"+str(tag)
output_pool_connect_string = 'sqlite:'+str(dropbox_file_name_prefix)+'.db'
dropbox_txt_file_name = str(dropbox_file_name_prefix)+".txt"
dropbox_txt_file = open(dropbox_txt_file_name, "w")
dropbox_txt_file.write('destDB '+destination_db+'\n')
dropbox_txt_file.write('inputtag\n')
dropbox_txt_file.write('tag '+str(tag)+'\n')
dropbox_txt_file.write('since\n')
dropbox_txt_file.write('till\n')
dropbox_txt_file.write('usertext '+str(dropbox_comment)+'\n')
dropbox_txt_file.close()

#
#_____ loop over IOV to copy
#
o2o_iovs = subprocess.Popen(["./xmlToolsRun", "--list-iovs-for-o2o", "--tag-name", tag, "--pool-connect-string", input_pool_connect_string], stdout=subprocess.PIPE).communicate()[0]
i = 0
for line in o2o_iovs.splitlines():
    i = i+1
    iov = int(line)
    make_popcon_config_file(python_popcon_file)
    os.system("cmsRun "+str(python_popcon_file))

#
#_____ copy to the Dropbox area
#
os.system('mv '+str(output_dir)+'/'+str(dropbox_file_name_prefix)+'.* '+str(dropbox_dir)+'/')
