#!/usr/bin/env python3

# This script publishes the required tableau artefacts

# First it reads a flag to decide what needs to be published, either:
# 1. Nothing
# 2. Everything from a specific site
# 3. Specific elements (in comma separated list)
# 4. Everything from a specific site EXCEPT for specific elements (in comma separated list)

# All artefacts are found in Git
# Assume Git structure:
# REPO
# |-- README.md
# |-- datasources
# |   |-- Project1
# |   |   |-- DataSource1
# |   |   |-- DataSource2
# |   |-- Project2
# |   |   |-- DataSource1
# |   |   |-- DataSource2
# |-- workbooks
# |   |-- Project1
# |   |   |-- WorkBook1
# |   |   |-- WorkBook2
# |   |-- Project2
# |   |   |-- WorkBook1
# |   |   |-- WorkBook2

# imports
import sys
import os
from os import listdir
import subprocess


# Define a function to read ALL DataSources from Git REPO
# Assume that all artefacts are for the SITE passed in to this python script
# Future enhancement: Site will be the highest level directory within repo
def read_datasources_all(repo_name):
    ds_list = []

    if verbose >= 1:
        print ("repo name = <" + repo_name + ">")
    # Get all Projects
    for proj_ds in listdir(os.path.join(repo_name, 'datasources')):
        if verbose >=1:
            print ("proj = <" + proj_ds + ">")
        for ds in listdir(os.path.join(repo_name, 'datasources', proj_ds)):
            if verbose >= 3:
                print ("ds = <" + ds + ">")
            full_ds = []
            full_ds.append(site)
            full_ds.append(proj_ds)
            full_ds.append(ds)
            ds_list.append(full_ds)
    if verbose >= 2:
        print ds_list
    return ds_list

# Define a function to read ALL WorkBooks from Git REPO
# Assume that all artefacts are for the SITE passed in to this python script
# Future enhancement: Site will be the highest level directory within repo
def read_workbooks_all(repo_name):
    wb_list = []

    if verbose >= 1:
        print ("repo name = <" + repo_name + ">")
    # Get all Projects
    for proj_wb in listdir(os.path.join(repo_name, 'workbooks')):
        if verbose >=1:
            print ("proj = <" + proj_wb + ">")
        for wb in listdir(os.path.join(repo_name, 'workbooks', proj_wb)):
            if verbose >= 3:
                print ("wb = <" + wb + ">")
            full_wb = []
            full_wb.append(site)
            full_wb.append(proj_wb)
            full_wb.append(wb)
            wb_list.append(full_wb)
    if verbose >= 2:
        print wb_list
    return wb_list

# Define a function to read Specific DataSources from environment variable
def read_datasources_specific(repo_name, ds_list_string):
    ds_list = []

    if verbose >= 2:
        print ("repo name = <" + repo_name + ">")

    if verbose >= 2:
        print "ds_list_string = <" + ds_list_string + ">"

    for full_ds in ds_list_string.split(','):
        if verbose >= 3:
            print "full_ds = <" + full_ds + ">"
        ds_elems = full_ds.split('/')
        if verbose >= 3:
            print "ds_elems = <"
            print ds_elems
            print ">"
        ds_list.append(ds_elems)

    if verbose >= 2:
        print ds_list
    return ds_list

# Define a function to read Specific WorkBooks from environment variable
def read_workbooks_specific(repo_name, wb_list_string):
    wb_list = []

    if verbose >= 1:
        print ("repo name = <" + repo_name + ">")

    if verbose >= 2:
        print "wb_list_string = <" + wb_list_string + ">"

    for full_wb in wb_list_string.split(','):
        if verbose >= 3:
            print "full_wb = <" + full_wb + ">"
        wb_elems = full_wb.split('/')
        if verbose >= 3:
            print "wb_elems = <"
            print wb_elems
            print ">"
        wb_list.append(wb_elems)

    if verbose >= 2:
        print wb_list
    return wb_list



# Define a function to publish all of the artefacts read previously
def publish_datasources(repo_name, ds_list_to_pub, ds_excl_list = []):
    for ds_to_pub in ds_list_to_pub:
        if ds_to_pub in ds_excl_list:
            if verbose >= 1:
                print "NOT publishing <", ds_to_pub, "> - it is in the exclusion list"
                continue
        if verbose >= 2:
            print "ds_to_pub = <", ds_to_pub, ">"
        project = ds_to_pub[1]
        ds_file = os.path.join(repo_name, 'datasources', project, ds_to_pub[2])
        if verbose >= 2:
            print "Calling tableau-pub-ds.sh with args " + project + ds_file
        return_code = subprocess.call([os.path.join(home_dir, "scripts", "tableau-pub-ds.sh"), project, ds_file])
        if return_code != 0:
            print "Error calling: " + os.path.join(home_dir, "scripts", "tableau-pub-ds.sh") + " " + project + " " + ds_file
            sys.exit(return_code)

# Define a function to publish all of the artefacts read previously
def publish_workbooks(repo_name, wb_list_to_pub, wb_excl_list = []):
    for wb_to_pub in wb_list_to_pub:
        if wb_to_pub in wb_excl_list:
            if verbose >= 1:
                print "NOT publishing <", wb_to_pub, "> - it is in the exclusion list"
                continue
        if verbose >= 2:
            print "wb_to_pub = <"
            print wb_to_pub
            print ">"
        project = wb_to_pub[1]
        wb_file = os.path.join(repo_name, 'workbooks', project, wb_to_pub[2])
        if verbose >= 2:
            print "Calling tableau-pub-wb.sh with args " + project + wb_file
        return_code = subprocess.call([os.path.join(home_dir, "scripts", "tableau-pub-wb.sh"), project, wb_file])
        if return_code != 0:
            print "Error calling: " + os.path.join(home_dir, "scripts", "tableau-pub-wb.sh") + " " + project + " " + wb_file
            sys.exit(return_code)

# Define usage function
# Future enhancement: Site will be the highest level directory within repo - so, not passed in
def usage():
    print "Usage: " + sys.argv[0] + " [REPO] [SITE]"
    sys.exit(1)

##################
### START HERE ###
##################
# Global vars
home_dir = os.environ['HOME']
verbose = 1
# USAGE
if len(sys.argv) == 3:
    repo = sys.argv[1]
    if not os.path.isdir(repo):
        print "Cannot find repository (" + repo + ")"
        print "Please provide full path to repository directory."
        usage()
    site = sys.argv[2]
else:
    usage()


# Create an array of DataSources
# Read OS Env var to determine operation
ds_to_pub = os.environ["DATASOURCES_TO_PUBLISH"]
wb_to_pub = os.environ["WORKBOOKS_TO_PUBLISH"]

ds_list = []
ds_not_list = []

if ds_to_pub == '' or ds_to_pub.upper() == 'NONE':
    pass
elif ds_to_pub.upper() == 'ALL':
    ds_list = read_datasources_all(repo)
elif ds_to_pub.split(None, 1)[0].upper() == 'NOT':
    not_operator, not_operand = ds_to_pub.split(None, 1)
    ds_not_list = read_datasources_specific(repo, not_operand)
    ds_list = read_datasources_all(repo)
else:
    ds_list = read_datasources_specific(repo, ds_to_pub)

wb_list = []
wb_not_list = []

if wb_to_pub == '' or wb_to_pub.upper() == 'NONE':
    pass
elif wb_to_pub.upper() == 'ALL':
    wb_list = read_workbooks_all(repo)
elif wb_to_pub.split(None, 1)[0].upper() == 'NOT':
    not_operator, not_operand = wb_to_pub.split(None, 1)
    wb_not_list = read_workbooks_specific(repo, not_operand)
    wb_list = read_workbooks_all(repo)
else:
    wb_list = read_workbooks_specific(repo, wb_to_pub)

if len(ds_list) == 0 and len(wb_list) == 0:
    if verbose >= 1:
        print "Nothing to publish."
        print "Exiting"
        sys.exit(0)

# Log in to Tableau Server (with helper script)
return_code = subprocess.call([os.path.join(home_dir, "scripts", "tableau-login.sh"), site])
if return_code != 0:
    print "Error calling: " + os.path.join(home_dir, "scripts", "tableau-login.sh") + " " + site
    sys.exit(return_code)

# Call function to publish each DataSource
if len(ds_list) > 0:
    publish_datasources(repo, ds_list, ds_not_list)

# Call function to publish each WorkBook
if len(wb_list) > 0:
    publish_workbooks(repo, wb_list, wb_not_list)
