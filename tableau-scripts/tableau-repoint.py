#!/usr/bin/env python3

# repoints server connections in the folder 'path' (arg1)
# to 'NEW_DBNAME'
# processes twb, twbx, tds, tdsx files
# new files end up in a subfolder 'repointed' of 'path'

import argparse
import logging
import os
import sys
import zipfile
from lxml import etree


def usage():
    """
    # Usage - supply source directory and new DB name
    """
    print("Usage:", sys.argv[0], "[SOURCE DIR] [NEW DB NAME]")
    print("    where:")
    print("        [SOURCE DIR]  - Directory containing Tableau files to be"
          + "repointed")
    print("                      - e.g. $HOME/tableau-internal/DQDashboards/"
          + "datasources/Admin")
    print("        [NEW DB NAME] - Name of database to be used in this "
          + "environment")
    print("                      - e.g. postgres-internal-tableau-apps-notprod"
          + "-dq.cool-random-string.eu-west-2.rds.amazonaws.com")
    sys.exit(1)


def create_subdirectory(path, new_dir_name):
    """
    # Function to create a subdirectory (if not already present)
    # Args: path         - the directory to change
    #       new_dir_name - the subdirectory name
    """
    new_full_path = os.path.join(path, new_dir_name)
    if not os.path.exists(new_full_path):
        logging.debug(">> Creating " + new_dir_name + " subdirectory")
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
    logging.debug(">> Opening compressed tableau file " + zip_filename)
    zread = zipfile.ZipFile(os.path.join(from_path, zip_filename), 'r')
    zwrite = zipfile.ZipFile(os.path.join(to_path, zip_filename), 'w')

    # loop through files in zip archive
    for item in zread.infolist():
        stream_in = zread.read(item.filename)
        # if tableau file, repoint it, else re-write it unchanged
        if item.filename[-4:] == '.twb' or item.filename[-4:] == '.tds':
            logging.info("> Processing " + item.filename)
            TEMP_DIR = create_subdirectory(to_path, 'temp')
            original_full_file = os.path.join(TEMP_DIR, item.filename)
            original_file = open(original_full_file, "wb")
            original_file.write(stream_in)
            original_file.close()
            xml_doc_tree_original = etree.parse(original_full_file)
            xml_doc_tree_repointed = server_rename_doc_tree(xml_doc_tree_original,
                                                            new_dbname)
            # xml_doc_tree_original = etree.parse(item.filename)
            # xml_doc_tree_repointed = server_rename_doc_tree(xml_doc_tree_original,
            #                                                 NEW_DBNAME)
            # zwrite.writestr(item.filename, xml_doc_tree_repointed.write())
            # xml_doc_original = etree.fromstring(stream_in.decode())
            # print("Now it is:", etree.tostring(xml_doc_original))
            # xml_doc_repointed = server_rename_doc(xml_doc_original,
            #                                       NEW_DBNAME)
            zwrite.writestr(item.filename, etree.tostring(xml_doc_tree_repointed))
        else:
            zwrite.writestr(item, stream_in)
    zread.close()
    zwrite.close()


def main():
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

    TAB_FILES_PATH = args.path
    if not os.path.isdir(TAB_FILES_PATH):
        print("Cannot find source directory (" + TAB_FILES_PATH + ")")
        print("Please provide full path to source directory containing",
              "Tableau files to be repointed.")
        usage()
    NEW_DBNAME = args.database
    OUTPUT_UNCOMPRESSED_FILES = args.output_uncompressed_files

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    logging.debug("Starting...")

    # create new subdirectory for repointed tableau files
    REPOINTED_DIR = create_subdirectory(TAB_FILES_PATH, 'repointed')

    # loop through files. if .t**x file, unzip first, else just replace strings
    for filename in os.listdir(TAB_FILES_PATH):
        logging.info("> Processing " + filename)
        if filename[-5:] == '.twbx' or filename[-5:] == '.tdsx':
            rewritezip(TAB_FILES_PATH, REPOINTED_DIR, filename, NEW_DBNAME)
        elif filename[-4:] == '.twb' or filename[-4:] == '.tds':
            full_file = os.path.join(TAB_FILES_PATH, filename)
            xml_doc_tree_old = etree.parse(full_file)
            xml_doc_tree_new = server_rename_doc_tree(xml_doc_tree_old,
                                                      NEW_DBNAME)

            tab_out = open(os.path.join(REPOINTED_DIR, filename), 'wb')
            xml_doc_tree_new.write(tab_out)
            tab_out.close()

    logging.debug("Finished.")


if __name__ == '__main__':
    main()
