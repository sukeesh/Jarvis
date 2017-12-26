#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# This script downloads and applies any and all imdb diff files which
# have not already been applied to the lists in the ImdbListsPath folder
#
# NOTE: this is especially useful in Windows environment; you have
# to modify the paths in the 'Script configuration' section below,
# accordingly with your needs.
#
# The script will check the imdb list files (compressed or incompressed)
# in ImdbListsPath and assume that the imdb lists were most recently downloaded
# or updated based on the most recently modified list file in that folder.
#
# In order to run correctly, the configuration section below needs to be
# set to the location of the imdb list files and the commands required to
# unGzip, UnTar, patch and Gzip files.
#
# Optional configuration settings are to set the imdb diff files download and/or
# backup folders. If you do not want to keep or backup the downloaded imdb diff
# files then set keepDiffFiles to False and diffFilesBackupFolder to None.
#
# If RunAfterSuccessfulUpdate is set to a value other than None then the program
# specified will be run after the imdb list files have been successfully updated.
# This enables, for example, the script to automatically run imdbPy to rebuild
# the database once the imdb list files have been updated.
#
# If a specific downloaded imdb diff file cannot be applied correctly then this script
# will fail as gracefully as possible.
#
# Copyright 2013 (C) Roy Stead
# Released under the terms of the GPL license.
#

import os
import sys
import shutil
import subprocess
import re
import datetime
import time
import MySQLdb
import logging

from datetime import timedelta,datetime
from ftplib import FTP
from random import choice

#############################################
#           Script configuration            #
#############################################

# The local folders where imdb list and diffs files are stored
#
# If ImdbDiffsPath is set to None then a working folder, "diffs" will be created as a sub-folder of ImdbListsPath
# and will be cleaned up afterwards if you also set keepDiffFiles to False
ImdbListsPath = "Z:\\MovieDB\\data\\lists"
ImdbDiffsPath = None

# The path to the logfile, if desired
logfile = 'Z:\\MovieDB\\data\\logs\\update.log'

# Define the system commands to unZip, unTar, Patch and Gzip a file
# Values are substituted into these template strings at runtime, in the order indicated
#
# Note that this script REQUIRES that the program used to apply patches MUST return 0 on success and non-zero on failure
#
unGzip="\"C:/Program Files/7-Zip/7z.exe\" e %s -o%s"                                # params = archive, destination folder
unTar=unGzip                                                                        # params = archive, destination folder
applyPatch="\"Z:/MovieDB/Scripts/patch.exe\" --binary --force --silent %s %s"       # params = listfile, diffsfile
progGZip="\"Z:/MovieDB/Scripts/gzip.exe\" %s"                                       # param = file to Gzip

# Specify a program to be run after a successful update of the imdb lists,
# such as a command line to execute imdbPy to rebuild the db from the updated imdb list files
#
# Set to None if no such program should be run
RunAfterSuccessfulUpdate="\"Z:\\MovieDB\\Scripts\\Update db from imdb lists.bat\""

# Folder to copy downloaded imdb diff files to once they have been successfully applied
# Note that ONLY diff files which are successfully applied will be backed up.
#
# Set to None if no such folder
diffFilesBackupFolder=None

# Set keepDiffFiles to false if the script is to delete ImdbDiffsPath and all its files when it's finished
#
# If set to False and diffFilesBackupFolder is not None then diff files will be backed up before being deleted
# (and will not be deleted if there's any problem with backing up the diff files)
keepDiffFiles=True

# Possible FTP servers for downloading imdb diff files and the path to the diff files on each server
ImdbDiffsFtpServers = [ \
    {'url': "ftp.fu-berlin.de", 'path': "/pub/misc/movies/database/diffs"}, \
#    {'url': "ftp.sunet.se", 'path': "/pub/tv+movies/imdb/diffs"}, \                # Swedish server isn't kept up to date
    {'url': "ftp.funet.fi", 'path': "/pub/mirrors/ftp.imdb.com/pub/diffs"} ]        # Finish server tends to be updated first


#############################################
#                Script Code                #
#############################################

logger = None

# Returns the date of the most recent Friday
# The returned datetime object contains ONLY date information, all time data is set to zero
def previousFriday(day):

    friday =  datetime(day.year, day.month, day.day) - timedelta(days=day.weekday()) + timedelta(days=4)

    # Saturday and Sunday are a special case since Python's day of the week numbering starts at Monday = 0
    # Note that if day falls on a Friday then the "previous friday" for that date is the same date
    if day.weekday() <= 4:
        friday -= timedelta(weeks=1)

    return friday

# Delete all files and subfolders in the specified folder as well as the folder itself
def deleteFolder(folder):
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    if os.path.isdir(folder):
        os.rmdir(folder)

# Create folder and as many parent folders are needed to create the full path
# Returns 0 on success or -1 on failure
def mktree(path):
    import os.path as os_path
    paths_to_create = []
    while not os_path.lexists(path):
        paths_to_create.insert(0, path)
        head,tail = os_path.split(path)
        if len(tail.strip())==0: # Just incase path ends with a / or \
            path = head
            head,tail = os_path.split(path)
        path = head

    for path in paths_to_create:
        try:
            os.mkdir(path)
        except Exception, e:
            logger.exception("Error trying to create %p" % path)
            return -1
    return 0

# Downloads and applies all imdb diff files which have not yet been applied to the current imdb lists
def applyDiffs():

    global keepDiffFiles, ImdbListsPath, ImdbDiffsPath, diffFilesBackupFolder
    global unGzip, unTar, applyPatch, progGZip, RunAfterSuccessfulUpdate, ImdbDiffsFtpServers

    if not os.path.exists(ImdbListsPath):
        logger.critical("Please edit this script file and set ImdbListsPath to the current location of your imdb list files")
        return

    # If no ImdbDiffsPath is specified, create a working folder for the diffs file as a sub-folder of the imdb lists repository
    if ImdbDiffsPath is None:
        ImdbDiffsPath = os.path.join(ImdbListsPath,"diffs")

    # Get the date of the most recent Friday (i.e. the most recently released imdb diffs)
    # Note Saturday and Sunday are a special case since Python's day of the week numbering starts at Monday = 0
    day = datetime.now()
    mostrecentfriday =  previousFriday(day)

    # Now get the date when the imdb list files in ImdbListsPath were most recently updated.
    #
    # At the end of this loop, day will contain the most recent date that a list file was
    # modified (Note: modified, not created, since Windows changes the creation date on file copies)
    #
    # This approach assumes that since the imdb list files were last downloaded or updated nobody has
    # unzipped a compressed list file and then re-zipped it again without updating all of the imdb
    # list files at that time (and also that nobody has manualy changed the file last modified dates).
    # Which seem like reasonable assumptions.
    #
    # An even more robust approach would be to look inside each zipfile and read the date/time stamp
    # from the first line of the imdb list file itself but that seems like overkill to me.
    day = None;
    for f in os.listdir(ImdbListsPath):
        if re.match(".*\.list\.gz",f) or re.match(".*\.list",f):
            try:
                t = os.path.getmtime(os.path.join(ImdbListsPath,f))
                d = datetime.fromtimestamp(t)

                if day == None:
                    day = d
                elif d > day:
                    day = d
            except Exception, e:
                logger.exception("Unable to read last modified date for file %s" % f)

    if day is None:

        # No diff files found and unable to read imdb list files
        logger.critical("Problem: Unable to check imdb lists in folder %s" % ImdbListsPath)
        logger.critical("Solutions: Download imdb lists, change ImdbListsPath value in this script or change access settings for that folder.")
        return

    # Last update date for imdb list files is the Friday before they were downloaded
    imdbListsDate =  previousFriday(day)

    logger.debug("imdb lists updated up to %s" % imdbListsDate)

    if imdbListsDate >= mostrecentfriday:
        logger.info("imdb database is already up to date")
        return

    # Create diffs file folder if it does not already exist
    if not os.path.isdir(ImdbDiffsPath):
        try:
            os.mkdir(ImdbDiffsPath)
        except Exception, e:
            logger.exception("Unable to create folder for imdb diff files (%s)" % ImdbDiffsPath)
            return

    # Next we check for the imdb diff files and download any which we need to apply but which are not already downloaded
    diffFileDate = imdbListsDate
    haveFTPConnection = False
    while 1:

        if diffFileDate >= mostrecentfriday:
            break;

        diff = "diffs-%s.tar.gz" % diffFileDate.strftime("%y%m%d")
        diffFilePath = os.path.join(ImdbDiffsPath, diff)

        logger.debug("Need diff file %s" % diff)

        if not os.path.isfile(diffFilePath):
            
            # diff file is missing so we need to download it so first make sure we have an FTP connection
            if not haveFTPConnection:
                try:
                    # Choose a random ftp server from which to download the imdb diff file(s)
                    ImdbDiffsFtpServer = choice(ImdbDiffsFtpServers)
                    ImdbDiffsFtp = ImdbDiffsFtpServer['url']
                    ImdbDiffsFtpPath = ImdbDiffsFtpServer['path']

                    # Connect to chosen imdb FTP server
                    ftp = FTP(ImdbDiffsFtp)
                    ftp.login()

                    # Change to the diffs folder on the imdb files server
                    ftp.cwd(ImdbDiffsFtpPath)

                    haveFTPConnection = True
                except Exception, e:
                    logger.exception("Unable to connect to FTP server %s" % ImdbDiffsFtp)
                    return

            # Now download the diffs file
            logger.info("Downloading ftp://%s%s/%s" % ( ImdbDiffsFtp, ImdbDiffsFtpPath, diff ))
            diffFile = open(diffFilePath, 'wb');
            try:
                ftp.retrbinary("RETR " + diff, diffFile.write)
                diffFile.close()
            except Exception, e:

                # Unable to download diff file. This may be because it's not yet available but is due for release today
                code, message = e.message.split(' ', 1)
                if code == '550' and diffFileDate == imdbListsDate:
                    logger.info("Diff file %s not yet available on the imdb diffs server: try again later" % diff)
                else:
                    logger.exception("Unable to download %s" % diff)

                # Delete the diffs file placeholder since the file did not download
                diffFile.close()
                os.remove(diffFilePath)
                if os.path.isdir(ImdbDiffsPath) and not keepDiffFiles:
                    os.rmdir(ImdbDiffsPath)

                return

            logger.info("Successfully downloaded %s" % diffFilePath)

        # Check for the following week's diff file
        diffFileDate += timedelta(weeks=1)

    # Close FTP connection if we used one
    if haveFTPConnection:
        ftp.close()


    # At this point, we know we need to apply one or more diff files and we
    # also know that we have all of the diff files which need to be applied
    # so next step is to uncompress our existing list files to a folder so
    # we can apply diffs to them.
    #
    # Note that the script will ONLY apply diffs if ALL of the diff files
    # needed to bring the imdb lists up to date are available. It will, however,
    # partially-update the imdb list files if one of the later files could not
    # be applied for any reason but earlier ones were applied ok (see below).
    tmpListsPath = os.path.join(ImdbDiffsPath,"lists")
    deleteFolder(tmpListsPath)
    try:
        os.mkdir(tmpListsPath)
    except Exception, e:
        logger.exception("Unable to create temporary folder for imdb lists")
        return

    logger.info("Uncompressing imdb list files")

    # Uncompress list files in ImdbListsPath to our temporary folder tmpListsPath
    numListFiles = 0;
    for f in os.listdir(ImdbListsPath):
        if re.match(".*\.list\.gz",f):
            try:
                cmdUnGzip = unGzip % (os.path.join(ImdbListsPath,f), tmpListsPath)
                subprocess.call(cmdUnGzip , shell=True)
            except Exception, e:
                logger.exception("Unable to uncompress imdb list file using: %s" % cmdUnGzip)
            numListFiles += 1

    if numListFiles == 0:
        # Somebody has deleted or moved the list files since we checked their datetime stamps earlier(!)
        logger.critical("No imdb list files found in %s." % ImdbListsPath)
        return


    # Now we loop through the diff files and apply each one in turn to the uncompressed list files
    patchedOKWith = None
    while 1:

        if imdbListsDate >= mostrecentfriday:
            break;

        diff = "diffs-%s.tar.gz" % imdbListsDate.strftime("%y%m%d")
        diffFilePath = os.path.join(ImdbDiffsPath, diff)

        logger.info("Applying imdb diff file %s" % diff)

        # First uncompress the diffs file to a subdirectory.
        #
        # If that subdirectory already exists, delete any files from it
        # in case they are stale and replace them with files from the
        # newly-downloaded imdb diff file
        tmpDiffsPath = os.path.join(ImdbDiffsPath,"diffs")
        deleteFolder(tmpDiffsPath)
        os.mkdir(tmpDiffsPath)

        # unZip the diffs file to create a file diffs.tar
        try:
            cmdUnGzip = unGzip % (diffFilePath, tmpDiffsPath)
            subprocess.call(cmdUnGzip, shell=True)
        except Exception, e:
            logger.exception("Unable to unzip imdb diffs file using: %s" % cmdUnGzip)
            return

        # unTar the file diffs.tar
        tarFile = os.path.join(tmpDiffsPath,"diffs.tar")
        patchStatus = 0
        if os.path.isfile(tarFile):
            try:
                cmdUnTar = unTar % (tarFile, tmpDiffsPath)
                subprocess.call(cmdUnTar, shell=True)
            except Exception, e:
                logger.exception("Unable to untar imdb diffs file using: %s" % cmdUnTar)
                return

            # Clean up tar file and the sub-folder which 7z may have (weirdly) created while unTarring it
            os.remove(tarFile);
            if os.path.exists(os.path.join(tmpDiffsPath,"diffs")):
                os.rmdir(os.path.join(tmpDiffsPath,"diffs"));

            # Apply all the patch files to the list files in tmpListsPath
            isFirstPatchFile = True
            for f in os.listdir(tmpDiffsPath):
                if re.match(".*\.list",f):
                    logger.info("Patching imdb list file %s" % f)
                    try:
                        cmdApplyPatch = applyPatch % (os.path.join(tmpListsPath,f), os.path.join(tmpDiffsPath,f))
                        patchStatus = subprocess.call(cmdApplyPatch, shell=True)
                    except Exception, e:
                        logger.exception("Unable to patch imdb list file using: %s" % cmdApplyPatch)
                        patchStatus=-1

                    if patchStatus <> 0:

                        # Patch failed so...
                        logger.critical("Patch status %s: Wrong diff file for these imdb lists (%s)" % (patchStatus, diff))

                        # Delete the erroneous imdb diff file
                        os.remove(diffFilePath)

                        # Clean up temporary diff files
                        deleteFolder(tmpDiffsPath)

                        if patchedOKWith <> None and isFirstPatchFile:

                            # The previous imdb diffs file succeeded and the current diffs file failed with the
                            # first attempted patch, so we can keep our updated list files up to this point
                            logger.warning("Patched OK up to and including imdb diff file %s ONLY" % patchedOKWith)
                            break

                        else:
                            # We've not managed to successfully apply any imdb diff files and this was not the
                            # first patch attempt from a diff file from this imdb diffs file so we cannot rely
                            # on the updated imdb lists being accurate, in which case delete them and abandon
                            logger.critical("Abandoning update: original imdb lists are unchanged")
                            deleteFolder(tmpListsPath)
                            return

                    # Reset isFirstPatchFile flag since we have successfully
                    # applied at least one patch file from this imdb diffs file
                    isFirstPatchFile = False

        # Clean up the imdb diff files and their temporary folder
        deleteFolder(tmpDiffsPath)

        # Note the imdb patch file which was successfully applied, if any
        if patchStatus == 0:
            patchedOKWith = diff

            # Backup successfully-applied diff file if required
            if diffFilesBackupFolder is not None:

                # Create diff files backup folder if it does not already exist
                if not os.path.isdir(diffFilesBackupFolder):
                    if mktree(diffFilesBackupFolder) == -1:
                        if not keepDiffFiles:
                            keepDiffFiles = True
                            logger.warning("diff files will NOT be deleted but may be backed up manually")

                # Backup this imdb diff file to the backup folder if that folder exists and this diff file doesn't already exist there
                if os.path.isdir(diffFilesBackupFolder):
                    if not os.path.isfile(os.path.join(diffFilesBackupFolder,diff)):
                        try:
                            shutil.copy(diffFilePath,diffFilesBackupFolder)
                        except Exception, e:
                            logger.exception("Unable to copy %s to backup folder %s" % (diffFilePath, diffFilesBackupFolder))
                            if not keepDiffFiles:
                                keepDiffFiles = True
                                logger.warning("diff files will NOT be deleted but may be backed up manually")

            # Clean up imdb diff file if required
            if not keepDiffFiles:
                if os.path.isfile(diffFilePath):
                    os.remove(diffFilePath)

        # Next we apply the following week's imdb diff files
        imdbListsDate += timedelta(weeks=1)

    # List files are all updated so re-Gzip them up and delete the old list files
    for f in os.listdir(tmpListsPath):
        if re.match(".*\.list",f):
            try:
                cmdGZip = progGZip % os.path.join(tmpListsPath,f)
                subprocess.call(cmdGZip, shell=True)
            except Exception, e:
                logger.exception("Unable to Gzip imdb list file using: %s" % cmdGZip)
                break
            if os.path.isfile(os.path.join(tmpListsPath,f)):
                os.remove(os.path.join(tmpListsPath,f))

    # Now move the updated and compressed lists to the main lists folder, replacing the old list files
    for f in os.listdir(tmpListsPath):
        if re.match(".*\.list.gz",f):
            # Delete the original compressed list file from ImdbListsPath if it exists 
            if os.path.isfile(os.path.join(ImdbListsPath,f)):
                os.remove(os.path.join(ImdbListsPath,f))

            # Move the updated compressed list file to ImdbListsPath
            os.rename(os.path.join(tmpListsPath,f),os.path.join(ImdbListsPath,f))

    # Clean up the now-empty tmpListsPath temporary folder and anything left inside it
    deleteFolder(tmpListsPath)

    # Clean up imdb diff files if required
    # Note that this rmdir call will delete the folder only if it is empty. So if that folder was created, used and all
    # diff files deleted (possibly after being backed up) above then it should now be empty and will be removed.
    #
    # However, if the folder previously existed and contained some old diff files then those diff files will not be deleted.
    # To delete the folder and ALL of its contents regardless, replace os.rmdir() with a deleteFolder() call
    if not keepDiffFiles:
        os.rmdir(ImdbDiffsPath)
#        deleteFolder(ImdbDiffsPath)

    # If the imdb lists were successfully updated, even partially, then run my
    # DOS batch file "Update db from imdb lists.bat" to rebuild the imdbPy database
    # and relink and reintegrate my shadow tables data into it
    if patchedOKWith <> None:
        logger.info("imdb lists are updated up to imdb diffs file %s" % patchedOKWith)
        if RunAfterSuccessfulUpdate <> None:
            logger.info("Now running %s" % RunAfterSuccessfulUpdate)
            subprocess.call(RunAfterSuccessfulUpdate, shell=True)


# Set up logging
def initLogging(loggerName, logfilename):

    global logger

    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)

    # Logger for file, if logfilename supplied
    if logfilename is not None:
        fh = logging.FileHandler(logfilename)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter('%(name)s %(levelname)s %(asctime)s %(message)s\t\t\t[%(module)s line %(lineno)d: %(funcName)s%(args)s]', datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(fh)

    # Logger for stdout
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(ch)

initLogging('__applydiffs__', logfile)

applyDiffs()
