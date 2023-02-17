# --------------------------------------------------------------------------------
# Name:     anaplanapi.py
# Desc:     Class to perform various Anaplan opeations via the Anapaln Connect (AC)
# commanline (CL) binary. Calling AC CL was done to ensure support from
# Anaplan tech support.
#
# Output:   None 
# Update Notes:
#   2/12/2017 - Initial deployment
# 4/12/2017 - Near final release
#
# --------------------------------------------------------------------------------


import re
import os
from subprocess import PIPE
import subprocess
import logging
import time
import getvar
import automationhelper
from requests.auth import HTTPBasicAuth
import sys


# Set Variables and instantiate external classes
consoleOut = getvar.consoleOut
fileHelper = automationhelper.file_system_operations()
logHelper = automationhelper.communications()

# Setup Logger
localTime = time.strftime("%Y%m%d", time.localtime())
logFile = '%s-MIS.LOG' % localTime
fullPathLogFile = '%s/%s' % (getvar.logFilePath, logFile)
logFileLevel = logging.INFO  # Options: INFO, WARNING, DEBUG, INFO, ERROR, CRITICAL

logging.basicConfig(filename=fullPathLogFile,
                    filemode='a',  # Append to Log
                    format='%(asctime)s  :  %(levelname)s  :  %(message)s',
                    level=logFileLevel)


# Direct integration with Anaplan API via Requests library
class anaplan_api:
    def get_action_name(self, actionId):
        anaplanAuth = HTTPBasicAuth(
            username=getvar.username, password=getvar.password)

        anaplanAPI = '%s/workspaces/%s/models/%s' % (
            getvar.anaplanAPI, getvar.workspaceId, getvar.modelId)


# Execute various Anaplan Actions (from the CL)
class anaplan_actions:

    def anaplan_import(self, sourceStream, targetFile, process, workspaceId, modelId):

        # Note that the Anaplan log files will be generic because a Process is being executed vs. an Action
        processLogDir = '%s/%s_process_logs' % (getvar.logFilePath, process)
        fileHelper.delete_dir_if_exists(
            dirToDelete=processLogDir, msg='', msgToConsole=False, msgToLog=False)
        if fileHelper.deleteDir:
            print 'Process logs deleted: %s' % processLogDir
        else:
            print 'Process logs NOT deleted: %s' % processLogDir
        print ''

        # Construct Anaplan Connect Operation string
        operation = (' -file "%s"' % targetFile +
                     ' -put "%s"' % sourceStream +
                     ' -process "%s"' % process +
                     ' -execute' +
                     ' -output "%s"' % processLogDir
                     )

        # Communicate initiating Anaplan Connect based upon operation to the console and log file
        logHelper.log_initiating_anaplan_connect(
            environment=getvar.environment,
            workspaceId=workspaceId, modelId=modelId,
            sourceFile=sourceStream, targetFile=targetFile, process=process,
            processLogDir=processLogDir)
        logHelper.conosole_initiating_anaplan_connect(
            environment=getvar.environment,
            workspaceId=workspaceId, modelId=modelId,
            sourceFile=sourceStream, targetFile=targetFile, process=process,
            processLogDir=processLogDir)

        for _ in range(getvar.retryCnt):
            # Communicate retry count
            logHelper.log_retry_count(retryCount=(_ + 1))
            logHelper.console_retry_count(retryCount=(_ + 1))

            # Execute Anaplan Connect Script
            exitCode, output, commandOutput, exceptionCalled = self.shell_anaplan_connect(operation=operation,
                                                                                          workspaceId=workspaceId,
                                                                                          modelId=modelId,
                                                                                          captureOutput=False)

        # Determine error level and return exitCode and status based upon criteria in this function call.
        exitCode, status, logFileRecords = logHelper.communicate_error_level(exitCode=exitCode,
                                                                             exceptionCalled=exceptionCalled,
                                                                             commandOutput=commandOutput,
                                                                             processLogDir=processLogDir)

        # Return results to calling program
        return exitCode, output, status, logFileRecords

    def anaplan_upload(self, sourceStream, targetFile, workspaceId, modelId):

        # Construct Anaplan Connect Operation string
        operation = (' -file "%s"' % targetFile +
                     ' -put "%s"' % sourceStream
                     )

        # Communicate initiating Anaplan Connect based upon operation to the console and log file
        logHelper.log_initiating_anaplan_connect(
            environment=getvar.environment,
            workspaceId=workspaceId, modelId=modelId,
            sourceFile=sourceStream, targetFile=targetFile)
        logHelper.conosole_initiating_anaplan_connect(
            environment=getvar.environment,
            workspaceId=workspaceId, modelId=modelId,
            sourceFile=sourceStream, targetFile=targetFile)

        for _ in range(getvar.retryCnt):
            # Communicate retry count
            logHelper.log_retry_count(retryCount=(_ + 1))
            logHelper.console_retry_count(retryCount=(_ + 1))

            # Execute Anaplan Connect Script
            exitCode, output, commandOutput, exceptionCalled = self.shell_anaplan_connect(operation=operation,
                                                                                          workspaceId=workspaceId,
                                                                                          modelId=modelId,
                                                                                          captureOutput=False)

        # Determine error level and return exitCode and status based upon criteria in this function call.
        exitCode, status, logFileRecords = logHelper.communicate_error_level(exitCode=exitCode,
                                                                             exceptionCalled=exceptionCalled,
                                                                             commandOutput=commandOutput)

        # Return results to calling program
        return exitCode, output, status

    def anaplan_action(self, action, workspaceId, modelId):
        # Create log file and location
        logFile = '%s/%s.log' % (getvar.logFilePath, action)
        fileHelper.dematerialize(logFile)

        # Construct Anaplan Connect Operation string
        operation = (' -import "%s"' % action +
                     ' -execute' +
                     ' -output "%s"' % logFile
                     )

        # Communicate initiating Anaplan Connect based upon operation to the console and log file
        logHelper.log_initiating_anaplan_connect(
            environment=getvar.environment,
            workspaceId=workspaceId, modelId=modelId,
            importAction=action, importActionLog=logFile)
        logHelper.conosole_initiating_anaplan_connect(
            environment=getvar.environment,
            workspaceId=workspaceId, modelId=modelId,
            importAction=action, importActionLog=logFile)

        for _ in range(getvar.retryCnt):
            # Communicate retry count
            logHelper.log_retry_count(retryCount=(_ + 1))
            logHelper.console_retry_count(retryCount=(_ + 1))

            # Execute Anaplan Connect Script
            exitCode, output, commandOutput, exceptionCalled = self.shell_anaplan_connect(
                operation=operation,
                workspaceId=workspaceId,
                modelId=modelId,
                captureOutput=False)

        # Determine error level and return exitCode and status based upon criteria in this function call.
        exitCode, status, logFileRecords = logHelper.communicate_error_level(exitCode=exitCode,
                                                                             exceptionCalled=exceptionCalled,
                                                                             commandOutput=commandOutput,
                                                                             logFile=logFile)

        # Return results to calling program
        return exitCode, output, status, logFileRecords

    def anaplan_process(self, process, workspaceId, modelId):

        # Note that the Anaplan log files will be generic because a Process is being executed vs. an Action
        processLogDir = '%s/%s_process_logs' % (getvar.logFilePath, process)

        fileHelper.delete_dir_if_exists(
            dirToDelete=processLogDir, msg='', msgToConsole=False, msgToLog=False)
        if fileHelper.deleteDir:
            print 'Process logs deleted: %s' % processLogDir
        else:
            print 'Process logs NOT deleted: %s' % processLogDir
        print ''

        # Construct Anaplan Connect Operation string
        operation = (' -process "%s"' % process +
                     ' -execute' +
                     ' -output "%s"' % processLogDir
                     )

        # Communicate initiating Anaplan Connect based upon operation to the console and log file
        logHelper.log_initiating_anaplan_connect(
            environment=getvar.environment,
            workspaceId=workspaceId, modelId=modelId,
            process=process, processLogDir=processLogDir)
        logHelper.conosole_initiating_anaplan_connect(
            environment=getvar.environment,
            workspaceId=workspaceId, modelId=modelId,
            process=process, processLogDir=processLogDir)

        for _ in range(getvar.retryCnt):
            # Communicate retry count
            logHelper.log_retry_count(retryCount=(_ + 1))
            logHelper.console_retry_count(retryCount=(_ + 1))

            # Execute Anaplan Connect Script
            exitCode, output, commandOutput, exceptionCalled = self.shell_anaplan_connect(operation=operation,
                                                                                          workspaceId=workspaceId,
                                                                                          modelId=modelId,
                                                                                          captureOutput=False)

        # Determine error level and return exitCode and status based upon criteria in this function call.
        exitCode, status, logFileRecords = logHelper.communicate_error_level(exitCode=exitCode,
                                                                             exceptionCalled=exceptionCalled,
                                                                             commandOutput=commandOutput,
                                                                             processLogDir=processLogDir)

        # Return results to calling program
        return exitCode, output, status, logFileRecords

    def anaplan_export(self, export, workspaceId, modelId):

        # Construct Anaplan Connect Operation string
        # Note that this operation streams the output to a object
        operation = (' -export "%s"' % export +
                     ' -execute' +
                     ' -gets'
                     )

        # Communicate initiating Anaplan Connect based upon operation to the console and log file
        logHelper.log_initiating_anaplan_connect(
            environment=getvar.environment, workspaceId=workspaceId, modelId=modelId, export=export)
        logHelper.conosole_initiating_anaplan_connect(
            environment=getvar.environment, workspaceId=workspaceId, modelId=modelId, export=export)

        for _ in range(getvar.retryCnt):
            # Communicate retry count
            logHelper.log_retry_count(retryCount=(_ + 1))
            logHelper.console_retry_count(retryCount=(_ + 1))

            # Execute Anaplan Connect Script
            exitCode, output, commandOutput, exceptionCalled = self.shell_anaplan_connect(operation=operation,
                                                                                          workspaceId=workspaceId,
                                                                                          modelId=modelId,
                                                                                          captureOutput=True)

        # Determine error level and return exitCode and status based upon criteria in this function call.
        exitCode, status, logFileRecords = logHelper.communicate_error_level(exitCode=exitCode,
                                                                             exceptionCalled=exceptionCalled,
                                                                             commandOutput=commandOutput)

        # Return results to calling program
        return exitCode, output, status

    def anaplan_export_file(self, export, workspaceId, modelId):

        # Construct Anaplan Connect Operation string
        # Note that this operation just drops the file into a location based upon the name of the file
        operation = (' -export "%s"' % export +
                     ' -execute' +
                     ' -get "%s/%s"' % (getvar.fileInbox, export)
                     )

        # Communicate initiating Anaplan Connect based upon operation to the console and log file
        logHelper.log_initiating_anaplan_connect(
            environment=getvar.environment,
            workspaceId=workspaceId, modelId=modelId,
            export=export)
        logHelper.conosole_initiating_anaplan_connect(
            environment=getvar.environment,
            workspaceId=workspaceId, modelId=modelId,
            export=export)

        for _ in range(getvar.retryCnt):
            # Communicate retry count
            logHelper.log_retry_count(retryCount=(_ + 1))
            logHelper.console_retry_count(retryCount=(_ + 1))

            # Execute Anaplan Connect Script
            exitCode, output, commandOutput, exceptionCalled = self.shell_anaplan_connect(operation=operation,
                                                                                          workspaceId=workspaceId,
                                                                                          modelId=modelId,
                                                                                          captureOutput=True)

        # Determine error level and return exitCode and status based upon criteria in this function call.
        exitCode, status, logFileRecords = logHelper.communicate_error_level(exitCode=exitCode,
                                                                             exceptionCalled=exceptionCalled,
                                                                             commandOutput=commandOutput)

        # Return results to calling program
        return exitCode, output, status

    # Primary method to shell to the CL via Python's subprocess.  Note that the entire string gets created
    # and executed from the method

    def shell_anaplan_connect(self, operation, workspaceId, modelId, captureOutput):

        # Initialize variables
        exitCode = 0
        output = ''
        exceptionCalled = False
        commandOutput = None

        # Added dynamic WorkspaceID and ModelID
        commandLine = (getvar.anaplanConnectPath +
                       ' -certificate "%s"' % getvar.certificate +
                       ' -workspace "%s"' % workspaceId +
                       ' -model "%s"' % modelId +
                       operation
                       )

        # Communicate the full Anaplan Connect string to the console and log file if debugOut is True
        if getvar.debugOut:
            logHelper.log_command_runner(commandRunner=commandLine)
            logHelper.console_command_runner(commandRunner=commandLine)

        # Try/Except block to subprocess to an Anaplan Connect script. The catch block will capture
        # issues with running the AC script
        try:
            # Execute Anaplan Connect
            process = subprocess.Popen(
                commandLine, shell=True, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()

            # Capture output (skip first line) and write to Log file & console
            # for line in commandOutput.splitlines()[0:]:
            if captureOutput:
                # Read Data Stream and skip first 3 lines to remove message returned from server
                for line in stdout.split(os.linesep)[3:]:
                    output += line + '\n'

            else:
                for line in stdout.splitlines()[1:]:
                    # Read list and find matches for specific Anaplan Connect Output
                    # Add your own strings as required.
                    if re.match('.+', line):
                        # Search Anaplan Connect for any of the following criteria
                        # SAMPLE: Item not located in Product list: 2971
                        p = re.search(r'.*Item not located.*', line)
                        if p:
                            exitCode = 227

                        p = re.search(r'.*Invalid name.*', line)
                        if p:
                            exitCode = 228

                        p = re.search(
                            r'.*Expected separator in date/period.*', line)
                        if p:
                            exitCode = 229

                        p = re.search(r'.*rows has warnings.*', line)
                        if p:
                            exitCode = 230

                        p = re.search(
                            r'The file .* has been uploaded as.*', line)
                        q = re.search(r'Dump file written to.*', line)
                        if not (p or q):
                            print line
                            logging.info(line)
                            output += line + '\n'

            # Capture output (skip first line) and write to Log file & console
            # for line in commandOutput.splitlines()[0:]:
            for line in stderr.splitlines()[0:]:

                # Read list and find matches for specific Anaplan Connect Output
                # Add your own strings as required.
                if re.match('.*', line):
                    # SAMPLE: Command Output:  Anaplan API: The credentials supplied were invalid.
                    p = re.search(r'.*Anaplan API.*', line)
                    if p:
                        logging.error(line)
                        output += line + '\n'
                        exitCode = 501
                        break

                    p = re.search(
                        r'.*does not exist or is not available to this user.*', line)
                    if p:
                        logging.error(line)
                        output += line + '\n'
                        exitCode = 502
                        break

                    p = re.search(r'.*not found in workspace.*', line)
                    if p:
                        logging.error(line)
                        output += line + '\n'
                        exitCode = 503
                        break

        # Catch exceptions and output
        except subprocess.CalledProcessError as exitObject:
            # Get the exit code from Anaplan Connect
            exceptionCalled = True
            exitCode = exitObject.returncode
            # command = exitObject.cmd
            commandOutput = exitObject.output

        return exitCode, output, commandOutput, exceptionCalled

    def anaplan_result_conversion(self, searchText):
        # Parse everything after the colon until the new line character

        # Take substring and split by successful, warning and ignored
        start = searchText.find(':') + 2
        end = searchText.find('\n', start)
        searchText = searchText[start:end]
        searchText = searchText.split(',')
        successRecords = searchText[0][0:searchText[0].find('(')].strip()
        warningRecords = searchText[1][0:searchText[1].find('(')].strip()
        ignoredRecords = searchText[2][0:searchText[2].find('i')].strip()

        # Return counts for successful, warning and ignored
        return successRecords, warningRecords, ignoredRecords


if __name__ == '__main__':
    print ''
    print '*********************'
    print 'Running independently'
    print '*********************'
    print ''
    # Instantiate Class
    anaplanAPI = anaplan_actions()
    logHelper = automationhelper.communications()
    fileHelper = automationhelper.file_system_operations()
    anaplanREST = anaplan_api()

    exitCode = 0

    x = 'Locations: 5947 (5947/0) rows successful, 0 ignored'

    successRecords, warningRecords, ignoredRecords = anaplanAPI.anaplan_result_conversion(
        x)

    print successRecords
    print warningRecords
    print ignoredRecords

    sys.exit()

    # Run Load Anaplan
    exitCode, output, status, logFileRecords = anaplanAPI.anaplan_import(
        sourceStream="/Users/user/Dropbox/dev/anaplan-connect-1-3-3-3/TestData/FACT2.TXT",
        targetFile="testAnaplanload.txt",
        process="sample_import_process",
        workspaceId=getvar.workspaceId,
        modelId=getvar.modelId)
    logHelper.console_test(status, output, exitCode)

    exitCode, output, status = anaplanAPI.anaplan_upload(
        sourceStream="/Users/user/Dropbox/dev/anaplan-connect-1-3-3-3/TestData/FACT2.TXT",
        targetFile="testAnaplanload.txt",
        workspaceId=getvar.workspaceId,
        modelId=getvar.modelId)
    logHelper.console_test(status, output, exitCode)

    exitCode, output, status, logFileRecords = anaplanAPI.anaplan_process(
        process="sample_import_process",
        workspaceId=getvar.workspaceId,
        modelId=getvar.modelId)
    logHelper.console_test(status, output, exitCode)

    exitCode, output, status, logFileRecords = anaplanAPI.anaplan_action(
        action="BaseData from FACT.TXT",
        workspaceId=getvar.workspaceId,
        modelId=getvar.modelId)
    logHelper.console_test(status, output, exitCode)

    exitCode, output, status = anaplanAPI.anaplan_export(
        export="BaseData.csv",
        workspaceId=getvar.workspaceId,
        modelId=getvar.modelId)
    logHelper.console_test(status, output, exitCode)
