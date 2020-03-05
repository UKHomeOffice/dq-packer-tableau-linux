#!/usr/bin/env python3
"""
This script publishes the required tableau artefacts

 First it reads a flag to decide what needs to be published, either:
 1. Nothing
 2. Everything from a specific site
 3. Specific elements (in comma separated list)
 4. Everything from a specific site EXCEPT for specific elements
    (in comma separated list)

 All artefacts are found in Git
 Assume Git structure:
 REPO
 |-- README.md
 |-- SITE
 |   |-- datasources
 |   |   |-- Project1
 |   |   |   |-- DataSource1
 |   |   |   |-- DataSource2
 |   |   |-- Project2
 |   |   |   |-- DataSource1
 |   |   |   |-- DataSource2
 |   |-- workbooks
 |   |   |-- Project1
 |   |   |   |-- WorkBook1
 |   |   |   |-- WorkBook2
 |   |   |-- Project2
 |   |   |   |-- WorkBook1
 |   |   |   |-- WorkBook2

 # TODO: Add options based on whole projects
"""

import glob
import os
from os import listdir
import subprocess
import sys

# Global vars
HOME_DIR = os.environ['HOME']
VERBOSE = 1


def read_datasources_all(repo_name, site_name):
    """
    Define a function to read ALL DataSources from Git REPO
    """
    ds_list = []

    if VERBOSE >= 1:
        print("repo name = <" + repo_name + ">")
        print("site name = <" + site_name + ">")
    # Get all Projects
    ds_path = os.path.join(repo_name, site_name, 'datasources')
    for proj_ds in listdir(ds_path):
        if proj_ds != "README.md":
            if VERBOSE >= 1:
                print("proj = <" + proj_ds + ">")
            proj_ds_path = os.path.join(ds_path, proj_ds)
            listing = glob.glob(proj_ds_path + os.path.sep + '*.tdsx')
            for data_source in listing:
                data_source_name = os.path.basename(data_source)
                if VERBOSE >= 3:
                    print("data_source_name = <" + data_source_name + ">")
                full_ds = []
                full_ds.append(site_name)
                full_ds.append(proj_ds)
                full_ds.append(data_source_name)
                ds_list.append(full_ds)
    if VERBOSE >= 2:
        print(ds_list)
    return ds_list


def read_workbooks_all(repo_name, site_name):
    """
    Define a function to read ALL WorkBooks from Git REPO
    """
    wb_list = []

    if VERBOSE >= 1:
        print("repo name = <" + repo_name + ">")
        print("site name = <" + site_name + ">")
    # Get all Projects
    wb_path = os.path.join(repo_name, site_name, 'workbooks')
    for proj_wb in listdir(wb_path):
        if proj_wb != "README.md":
            if VERBOSE >= 1:
                print("proj = <" + proj_wb + ">")
            proj_wb_path = os.path.join(wb_path, proj_wb)
            listing = glob.glob(proj_wb_path + os.path.sep + '*.twbx')
            for workbook in listing:
                workbook_name = os.path.basename(workbook)
                if VERBOSE >= 3:
                    print("workbook_name = <" + workbook_name + ">")
                full_wb = []
                full_wb.append(site_name)
                full_wb.append(proj_wb)
                full_wb.append(workbook_name)
                wb_list.append(full_wb)
    if VERBOSE >= 2:
        print(wb_list)
    return wb_list


def read_datasources_specific(repo_name, site_name, ds_list_string):
    """
    Define a function to read Specific DataSources from environment variable
    """
    ds_list = []

    if VERBOSE >= 2:
        print("repo name = <" + repo_name + ">")
        print("site name = <" + site_name + ">")

    if VERBOSE >= 2:
        print("ds_list_string = <" + ds_list_string + ">")

    for full_ds in ds_list_string.split(','):
        if VERBOSE >= 3:
            print("full_ds = <" + full_ds + ">")
        ds_elems = full_ds.split('/')
        if VERBOSE >= 3:
            print("ds_elems = <")
            print(ds_elems)
            print(">")
        ds_list.append(ds_elems)

    if VERBOSE >= 2:
        print(ds_list)
    return ds_list


def read_workbooks_specific(repo_name, site_name, wb_list_string):
    """
    Define a function to read Specific WorkBooks from environment variable
    """
    wb_list = []

    if VERBOSE >= 1:
        print("repo name = <" + repo_name + ">")
        print("site name = <" + site_name + ">")

    if VERBOSE >= 2:
        print("wb_list_string = <" + wb_list_string + ">")

    for full_wb in wb_list_string.split(','):
        if VERBOSE >= 3:
            print("full_wb = <" + full_wb + ">")
        wb_elems = full_wb.split('/')
        if VERBOSE >= 3:
            print("wb_elems = <")
            print(wb_elems)
            print(">")
        wb_list.append(wb_elems)

    if VERBOSE >= 2:
        print(wb_list)
    return wb_list


def create_datasource_list(repo_name, site_name):
    """
    Create an array of DataSources
    Read OS Env var to determine operation
    """
    ds_to_pub = os.environ["DATASOURCES_TO_PUBLISH"]

    ds_list = []
    ds_not_list = []

    if ds_to_pub == '' or ds_to_pub.upper() == 'NONE':
        pass
    elif ds_to_pub.upper() == 'ALL':
        ds_list = read_datasources_all(repo_name, site_name)
    elif ds_to_pub.split(None, 1)[0].upper() == 'NOT':
        not_operator, not_operand = ds_to_pub.split(None, 1)  # pylint: disable=unused-variable
        ds_not_list = read_datasources_specific(repo_name, site_name, not_operand)
        ds_list = read_datasources_all(repo_name, site_name)
    else:
        ds_list = read_datasources_specific(repo_name, site_name, ds_to_pub)

    return ds_list, ds_not_list


def create_workbook_list(repo_name, site_name):
    """
    Create an array of WorkBooks
    Read OS Env var to determine operation
    """
    wb_to_pub = os.environ["WORKBOOKS_TO_PUBLISH"]

    wb_list = []
    wb_not_list = []

    if wb_to_pub == '' or wb_to_pub.upper() == 'NONE':
        pass
    elif wb_to_pub.upper() == 'ALL':
        wb_list = read_workbooks_all(repo_name, site_name)
    elif wb_to_pub.split(None, 1)[0].upper() == 'NOT':
        not_operator, not_operand = wb_to_pub.split(None, 1)  # pylint: disable=unused-variable
        wb_not_list = read_workbooks_specific(repo_name, site_name, not_operand)
        wb_list = read_workbooks_all(repo_name, site_name)
    else:
        wb_list = read_workbooks_specific(repo_name, site_name, wb_to_pub)

    return wb_list, wb_not_list


def publish_datasources(repo_name, site_name, ds_list_to_pub, ds_excl_list):
    """
    Define a function to publish all of the artefacts read previously
    """
    for ds_to_pub in ds_list_to_pub:
        if ds_to_pub in ds_excl_list:
            if VERBOSE >= 1:
                print("NOT publishing <", ds_to_pub,
                      "> - it is in the exclusion list")
                continue
        if VERBOSE >= 2:
            print("ds_to_pub = <", ds_to_pub, ">")
        project = ds_to_pub[1]
        ds_file = os.path.join(repo_name, site_name, 'datasources', project, ds_to_pub[2])
        if VERBOSE >= 2:
            print("Calling tableau-pub-ds.sh with args " + project + ds_file)
        return_code = subprocess.call([os.path.join(HOME_DIR, "scripts",
                                                    "tableau-pub-ds.sh"),
                                       project, ds_file])
        if return_code != 0:
            print("Error calling:", os.path.join(HOME_DIR, "scripts",
                                                 "tableau-pub-ds.sh"),
                  project, ds_file)
            sys.exit(return_code)


def publish_workbooks(repo_name, site_name, wb_list_to_pub, wb_excl_list=None):
    """
    Define a function to publish all of the artefacts read previously
    """
    for wb_to_pub in wb_list_to_pub:
        if wb_to_pub in wb_excl_list:
            if VERBOSE >= 1:
                print("NOT publishing <", wb_to_pub,
                      "> - it is in the exclusion list")
                continue
        if VERBOSE >= 2:
            print("wb_to_pub = <")
            print(wb_to_pub)
            print(">")
        project = wb_to_pub[1]
        wb_file = os.path.join(repo_name, site_name, 'workbooks', project, wb_to_pub[2])
        if VERBOSE >= 2:
            print("Calling tableau-pub-wb.sh with args", project + wb_file)
        return_code = subprocess.call([os.path.join(HOME_DIR, "scripts",
                                                    "tableau-pub-wb.sh"),
                                       project, wb_file])
        if return_code != 0:
            print("Error calling: " + os.path.join(HOME_DIR, "scripts",
                                                   "tableau-pub-wb.sh"),
                  project, wb_file)
            sys.exit(return_code)


def usage():
    """
    Define usage function
    Future enhancement: Site will be the highest level directory within repo
                     - so, not passed in
    """
    print("Usage:", sys.argv[0], "[REPO] [SITE]")
    sys.exit(1)


def main():
    """
    ##############
    # START HERE #
    ##############
    """
    # USAGE
    if len(sys.argv) == 3:
        repo = sys.argv[1]
        if not os.path.isdir(repo):
            print("Cannot find repository (" + repo + ")")
            print("Please provide full path to repository directory.")
            usage()
        site = sys.argv[2]
        if not os.path.isdir(os.path.join(repo, site)):
            print("Cannot find site '" + site + "' in repository '" + repo + "'")
            print("Please provide valid site in repository.")
            usage()
    else:
        usage()

    ds_list, ds_not_list = create_datasource_list(repo, site)

    wb_list, wb_not_list = create_workbook_list(repo, site)

    if not ds_list and not wb_list:
        if VERBOSE >= 1:
            print("Nothing to publish.")
            print("Exiting")
            sys.exit(0)

    # Log in to Tableau Server (with helper script)
    return_code = subprocess.call([os.path.join(HOME_DIR, "scripts",
                                                "tableau-login.sh"), site])
    print(return_code)
    if return_code != 0:
        print("Error calling: " + os.path.join(HOME_DIR, "scripts",
                                               "tableau-login.sh"), site)
        sys.exit(return_code)

    # Call function to publish each DataSource
    if ds_list:
        publish_datasources(repo, site, ds_list, ds_not_list)

    # Call function to publish each WorkBook
    if wb_list:
        publish_workbooks(repo, site, wb_list, wb_not_list)


if __name__ == "__main__":
    main()
    print("We're done here.")
