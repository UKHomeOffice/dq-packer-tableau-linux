#!/usr/bin/env python3

# repoints server connections in the folder 'path'
# from 'old_dbname' to 'new_dbname'
# processes twb, twbx, tds, tdsx files
# new files end up in a subfolder 'repointed' of 'path'

import os
import re
import sys
import zipfile


# change the below to reflect the required path and server names
VERBOSE = 1
OUTPUT_UNCOMPRESSED_FILES = True
# OLD_DBNAME="postgres-internal-tableau-apps-notprod-dq.cjwr8jp0ndrs.eu-west-2.rds.amazonaws.com"
# OLD_DBNAME = "postgres-internal-tableau-apps-notprod-dq.\S*?.eu-west-2.rds.amazonaws.com"
# Matches:  [dev-|qa-|uat-]?                : any one of these prefixes
#           postgres-                       : literal string
#           [internal|external]?            : internal or external
#           -tableau-apps-                  : literal string
#           [not]?prod                      : notprod or prod
#           -dq.                            : literal string
#           \S*?                            : any number of character (not greedy),  e.g. cjwr8jp0ndrs
#           .eu-west-2.rds.amazonaws.com    : literal string
#
# old_dbname = "[dev-|qa-|uat-]?postgres-[internal|external]-tableau-apps-[not]?prod-dq.\S*?.eu-west-2.rds.amazonaws.com"
# old_dbname = "[dev-|qa-|uat-]{0,1}postgres-[internal|external]+-tableau-apps-notprod-dq.\S*?.eu-west-2.rds.amazonaws.com"
old_dbname = "dev-postgres-[internal|external]+-tableau-apps-notprod-dq.\S*?.eu-west-2.rds.amazonaws.com"
# new_dbname = "postgres-internal-tableau-apps-notprod-dq.cool-random-string.eu-west-2.rds.amazonaws.com"


def usage():
    """
    # Usage - supply source directory and new DB name
    # TODO: Need to work out a way of handling NotProd/Prod
    # TODO: Need to work out a way of handling old DB name
    """
    print("Usage:", sys.argv[0], "[SOURCE DIR] [NEW DB NAME]")
    print("    where:")
    print("        [SOURCE DIR]  - Directory containing Tableau files to be repointed")
    print("                      - e.g. $HOME/tableau-internal/DQDashboards/datasources/Admin")
    print("        [NEW DB NAME] - Name of database to be used in this environment")
    print("                      - e.g. postgres-internal-tableau-apps-notprod-dq.cool-random-string.eu-west-2.rds.amazonaws.com")
    sys.exit(1)


def create_subdirectory(path, new_dir_name):
    """
    # Function to create a subdirectory (if not already present)
    # Args: path         - the directory to change
    #       new_dir_name - the subdirectory name
    """
    new_full_path = os.path.join(path, new_dir_name)
    if not os.path.exists(new_full_path):
        if VERBOSE >= 2:
            print(">> Creating", new_dir_name, "subdirectory")
        os.makedirs(new_full_path)
    return new_full_path


def server_rename(buffer, olddbname, newdbname):
    """
    # Function to rename the (database) server within a (tableau) file
    """
    tab_text = buffer.decode('utf-8')

    # # replaces every instance of the olddbname with the newdbname
    (tab_text, num_subs_1) = re.subn("http://" + old_dbname, "http://" + new_dbname, tab_text)
    (tab_text, num_subs_2) = re.subn("server=\'" + old_dbname, "server=\'" + new_dbname, tab_text)
    (tab_text, num_subs_3) = re.subn("server=\'" + old_dbname.upper(),
                                  "server=\'" + new_dbname.upper(), tab_text)
    (tab_text, num_subs_4) = re.subn("server=&apos;" + old_dbname,
                                  "server=&apos;" + new_dbname, tab_text)

    # Report how many changes were made
    if VERBOSE >= 1:
        if tab_text == buffer:
            print("> No changes were made")
        else:
            print("> Made", num_subs_1 + num_subs_2 + num_subs_3 + num_subs_4, "changes to DB server name")
            # print("> Made", 0, "changes to DB server name")

    return bytes(tab_text, 'utf-8')


def rewritezip(path, filename):
    """
    # Function to open and re-write the zipfile
    # Optionally, the Tableau DataSource and Workbook files can be written (outside of the compressed file)
    """
    if VERBOSE >= 2:
        print(">> Opening compressed tableau file", filename)
    zread = zipfile.ZipFile(os.path.join(path, filename), 'r')
    zwrite = zipfile.ZipFile(os.path.join(repointed_dir, filename), 'w')

    # loop through files in zip archive
    for item in zread.infolist():
        tab_in = zread.read(item.filename)
        # if tableau file, repoint it, else re-write it unchanged
        if item.filename[-4:] == '.twb' or item.filename[-4:] == '.tds':
            if OUTPUT_UNCOMPRESSED_FILES:
                # write a copy of the original tableau file, outside of `.t**x`
                if VERBOSE >= 2:
                    print(">> Writing a copy of the original file", item.filename, "to", uncompressed_dir)
                original_file = open(os.path.join(uncompressed_dir, item.filename), "wb")
                original_file.write(tab_in)
                original_file.close()
            if VERBOSE >= 1:
                print("> Processing", item.filename)
            repointed = server_rename(tab_in, old_dbname, new_dbname)
            zwrite.writestr(item.filename, repointed)
            if OUTPUT_UNCOMPRESSED_FILES:
                # write a copy of the repointed file, outside of `.t**x`
                if VERBOSE >= 2:
                    print(">> Writing a copy of the repointed file", item.filename, "to", uncompressed_repointed_dir)
                repointed_file = open(os.path.join(uncompressed_repointed_dir, item.filename), "wb")
                repointed_file.write(repointed)
                repointed_file.close()
        else:
            zwrite.writestr(item, tab_in)
    zread.close()
    zwrite.close()


#########
# START #
#########
# Usage
if len(sys.argv) == 3:
    tab_files_path = sys.argv[1]
    if not os.path.isdir(tab_files_path):
        print("Cannot find source directory (" + tab_files_path + ")")
        print("Please provide full path to source directory containing Tableau files to be repointed.")
        usage()
    new_dbname = sys.argv[2]
else:
    usage()

print("Starting...")
# create new subdirectory for extracted tableau files
uncompressed_dir = create_subdirectory(tab_files_path, 'uncompressed')

# create new subdirectory for repointed tableau files
repointed_dir = create_subdirectory(tab_files_path, 'repointed')

# create new subdirectory for extracted repointed tableau files
uncompressed_repointed_dir = create_subdirectory(repointed_dir, 'uncompressed')


# loop through files. if .t**x file, unzip first, else just replace strings
for filename in os.listdir(tab_files_path):
    if VERBOSE >= 1:
        print("> Processing", filename)
    if filename[-5:] == '.twbx' or filename[-5:] == '.tdsx':
        rewritezip(tab_files_path, filename)
    elif filename[-4:] == '.twb' or filename[-4:] == '.tds':
        full_file = os.path.join(tab_files_path, filename)
        tab_file = open(full_file, 'rb')
        tab_in = tab_file.read()
        repointed = server_rename(tab_in, old_dbname, new_dbname)
        tab_out = open(os.path.join(repointed_dir, filename), 'wb')
        tab_out.write(repointed)
        tab_out.close()
        tab_file.close()

print("Finished.")
