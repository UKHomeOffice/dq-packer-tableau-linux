#!/usr/bin/env python3
"""
Repoints server connections in the folder 'path' (arg1)
 to 'new_dbname'
 processes twb, twbx, tds, tdsx files
 new files end up in a subfolder 'repointed' of 'path'

# TODO: When working fully, it should replace the values "in place" because
this will be called on files in git repo (on a temporary "deploy" branch).
Should take an option to save a copy of the original.
"""

import argparse
import logging
import os
import sys
import zipfile
from lxml import etree


def usage():
    """
    Usage - supply source directory and new DB name
    """
    print("Usage:", sys.argv[0], "[SOURCE DIR] [NEW DB NAME]")
    print("    where:")
    print("        [SOURCE DIR]  - Directory containing Tableau files to be repointed")
    print("                      - e.g. $HOME/tableau-internal/DQDashboards/datasources/Admin")
    print("        [NEW DB NAME] - Name of database to be used in this environment")
    #  I don't want to split the following line it hinders readability
    print("                      - e.g. postgres-internal-tableau-apps-notprod-dq.cool-random-string.eu-west-2.rds.amazonaws.com") # pylint: disable=C0301
    sys.exit(1)


def create_subdirectory(path, new_dir_name):
    """
    # Function to create a subdirectory (if not already present)
    # Args: path         - the directory to change
    #       new_dir_name - the subdirectory name
    """
    new_full_path = os.path.join(path, new_dir_name)
    if not os.path.exists(new_full_path):
        logging.debug(">> Creating %s subdirectory", new_dir_name)
        os.makedirs(new_full_path)
    return new_full_path


def server_rename_doc_tree(tab_doc_tree, new_dbname):
    """
    Function to find server connections and replace the DB name
      - takes an lxml document tree
      - returns an lxml document tree
    """
    doc_tree = tab_doc_tree
    root = doc_tree.getroot()
    conn_elem = root.find('connection/named-connections/named-connection/connection')
    if conn_elem is not None:
        print("connection element =", etree.tostring(conn_elem))
        if conn_elem.attrib['server'] != new_dbname:
            conn_elem.attrib['server'] = new_dbname
        print("connection element =", etree.tostring(conn_elem))
    else:
        logging.info("No connections found in this file")

    return doc_tree


def server_rename_doc(tab_doc, new_dbname):
    """
    Function to find server connections and replace the DB name
      - takes an lxml document
      - returns an lxml document
    """
    root = tab_doc
    conn_elem = root.find('connection/named-connections/named-connection/connection')
    print("connection element =", etree.tostring(conn_elem))
    if conn_elem.attrib['server'] != new_dbname:
        conn_elem.attrib['server'] = new_dbname
    print("connection element =", etree.tostring(conn_elem))

    return root


def rewritezip(from_path, to_path, zip_filename, new_dbname):
    """
    Function to open and re-write the zipfile
    """
    logging.debug(">> Opening compressed tableau file %s", zip_filename)
    zread = zipfile.ZipFile(os.path.join(from_path, zip_filename), 'r')
    zwrite = zipfile.ZipFile(os.path.join(to_path, zip_filename), 'w')

    # loop through files in zip archive
    for item in zread.infolist():
        stream_in = zread.read(item.filename)
        # if tableau file, repoint it, else re-write it unchanged
        if item.filename[-4:] == '.twb' or item.filename[-4:] == '.tds':
            logging.info("> Processing %s", item.filename)
            temp_dir = create_subdirectory(to_path, 'temp')
            original_full_file = os.path.join(temp_dir, item.filename)
            original_file = open(original_full_file, "wb")
            original_file.write(stream_in)
            original_file.close()
            xml_doc_tree_original = etree.parse(original_full_file)
            xml_doc_tree_repointed = server_rename_doc_tree(xml_doc_tree_original,
                                                            new_dbname)
            zwrite.writestr(item.filename, etree.tostring(xml_doc_tree_repointed))
        else:
            zwrite.writestr(item, stream_in)
    zread.close()
    zwrite.close()


def main():
    """
    START HERE
    """
    parser = argparse.ArgumentParser(description='repoints server connections')
    parser.add_argument('--path', '-p', required=True,
                        help='Path to Tableau resourses to be repointed')
    parser.add_argument('--database', '-d', required=True,
                        help='Name of database to be used in this environment')
    parser.add_argument('--output_uncompressed_files', '-o', default=True,
                        help='Script to output uncompressed Tableau files')

    parser.add_argument('--logging-level', '-l',
                        choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    args = parser.parse_args()

    tab_files_path = args.path
    if not os.path.isdir(tab_files_path):
        print("Cannot find source directory (" + tab_files_path + ")")
        print("Please provide full path to source directory containing",
              "Tableau files to be repointed.")
        usage()
    new_dbname = args.database
    # NYI
    #output_incompressed_files = args.output_uncompressed_files

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    logging.debug("Starting...")

    # create new subdirectory for repointed tableau files
    repointed_dir = create_subdirectory(tab_files_path, 'repointed')

    # loop through files. if .t**x file, unzip first, else just replace strings
    for filename in os.listdir(tab_files_path):
        logging.info("> Processing %s", filename)
        if filename[-5:] == '.twbx' or filename[-5:] == '.tdsx':
            rewritezip(tab_files_path, repointed_dir, filename, new_dbname)
        elif filename[-4:] == '.twb' or filename[-4:] == '.tds':
            full_file = os.path.join(tab_files_path, filename)
            xml_doc_tree_old = etree.parse(full_file)
            xml_doc_tree_new = server_rename_doc_tree(xml_doc_tree_old,
                                                      new_dbname)

            tab_out = open(os.path.join(repointed_dir, filename), 'wb')
            xml_doc_tree_new.write(tab_out)
            tab_out.close()

    logging.debug("Finished.")


if __name__ == '__main__':
    main()
