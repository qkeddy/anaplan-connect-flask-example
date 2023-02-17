#--------------------------------------------------------------------------------
# Name:     automationhelper.py
# Desc:     Helper class to for outputting standard console out and logging
# 			
# Output:   None
# Update Notes:
#   2/12/2017 - Initial deployment
#	4/12/2017 - Near final release
#   
#--------------------------------------------------------------------------------


import os
import logging
import time
import shutil
import getvar
import glob
import string
from random import *

import automationhelper


# Setup Logger
localTime = time.strftime("%Y%m%d", time.localtime())
logFile = '%s-MIS.LOG' % localTime
fullPathLogFile = '%s/%s' % (getvar.logFilePath, logFile)
logFileLevel = logging.INFO  # Options: INFO, WARNING, DEBUG, INFO, ERROR, CRITICAL

logging.basicConfig(filename=fullPathLogFile,
					filemode='a',  # Append to Log
					format='%(asctime)s  :  %(levelname)s  :  %(message)s',
					level=logFileLevel)


class communications:

	# Send a dictionary via **kargs and based upon the values write to a log file
	def log_initiating_anaplan_connect(self, **kargs):
		logging.info('******************************************************************')
		logging.info('  INITIATING ANAPLAN ACTIVITY WITH THE FOLLOWING PARAMETERS')
		logging.info('******************************************************************')
		if 'environment' in kargs: logging.info('Environment: %s' % kargs.get('environment'))
		if 'workspaceId' in kargs: logging.info('Workspace ID: %s' % kargs.get('workspaceId'))
		if 'modelId' in kargs: logging.info('Model ID: %s' % kargs.get('modelId'))
		if 'user' in kargs: logging.info('User: %s' % kargs.get('user').split(':')[0])
		if 'sourceFile' in kargs: logging.info('Source file: %s' % kargs.get('sourceFile'))
		if 'targetFile' in kargs: logging.info('Target file: %s' % kargs.get('targetFile'))
		if 'importAction' in kargs: logging.info('Import Action: %s' % kargs.get('importAction'))
		if 'importActionLog' in kargs: logging.info('Import Action log: %s' % kargs.get('importActionLog'))
		if 'process' in kargs: logging.info('Process: %s' % kargs.get('process'))
		if 'processLogDir' in kargs: logging.info('Process log directory: %s' % kargs.get('processLogDir'))
		if 'export' in kargs: logging.info('Export file: %s' % kargs.get('export'))

	# Send a dictionary via **kargs and based upon the values create the appropriate message in the console
	def conosole_initiating_anaplan_connect(self, **kargs):
		currTime = time.strftime("%Y-%m-%d %H:%M", time.localtime())
		print '******************************************************************'
		print '  INITIATING ANAPLAN ACTIVITY WITH THE FOLLOWING PARAMETERS'
		print '******************************************************************'
		print 'Date and Time: %s' % currTime
		if 'environment' in kargs: print 'Environment: %s' % kargs.get('environment')
		if 'workspaceId' in kargs: print 'Workspace ID: %s' % kargs.get('workspaceId')
		if 'modelId' in kargs: print 'Model ID: %s' % kargs.get('modelId')
		if 'user' in kargs: print 'User: %s' % kargs.get('user').split(':')[0]
		if 'sourceFile' in kargs: print 'Source file: %s' % kargs.get('sourceFile')
		if 'targetFile' in kargs: print 'Target file: %s' % kargs.get('targetFile')
		if 'importAction' in kargs: print 'Import Action: %s' % kargs.get('importAction')
		if 'importActionLog' in kargs: print 'Import Action log: %s' % kargs.get('importActionLog')
		if 'process' in kargs: print 'Process: %s' % kargs.get('process')
		if 'processLogDir' in kargs: print 'Process log directory: %s' % kargs.get('processLogDir')
		if 'export' in kargs: print 'Export file: %s' % kargs.get('export')
		print ''

	# Write command runner to a log file
	def log_command_runner(self, **kargs):
		logging.info('************************ Command Runner **************************')
		if 'commandRunner' in kargs: logging.info(kargs.get('commandRunner'))
		logging.info('******************************************************************')

	# Print command runner to console out
	def console_command_runner(self, **kargs):
		print '************************ Command Runner **************************'
		if 'commandRunner' in kargs: print kargs.get('commandRunner')
		print '******************************************************************'
		print ''

	# Write Retry to log file
	def log_retry_count(self, **kargs):
		currTime = time.strftime("%Y-%m-%d %H:%M", time.localtime())
		retryCount = kargs.get('retryCount')
		if retryCount > 1:
			logging.info('***************** Retry#: %s - %s  ******************' % (retryCount , currTime))

	# Print command runner to console out
	def console_retry_count(self, **kargs):
		currTime = time.strftime("%Y-%m-%d %H:%M", time.localtime())
		retryCount = kargs.get('retryCount')
		if retryCount > 1:
			print '***************** Retry#: %s - %s  ******************' % (retryCount , currTime)

	# Communicate Error level  based upon various conditions
	def communicate_error_level(self, exitCode, exceptionCalled, commandOutput, **kargs):
		fileHelper = automationhelper.file_system_operations()
		logFileRecords = ''

		# Set exit code if Exception occurred
		if exceptionCalled:
			print 'ERROR : GENERAL EXCEPTION OCCURRED'
			print commandOutput
			print ''
			logging.ERROR('ERROR : GENERAL EXCEPTION OCCURRED')
			exitCode = 500

		# Warn if the data load generated a collection of Process log files and override the exit code
		processLogDir = str(kargs.get('processLogDir'))
		if len(glob.glob('%s/%s' % (processLogDir, '*'))) > 0:
			print 'WARNING : THE LOAD GENERATED A LOG FILE(S)'
			print ''
			logging.warning('THE LOAD GENERATED A LOG FILE(S)')
			logFileRecords = fileHelper.read_logs_in_dir(processLogDir, 5)
			#exitCode = 299

		# Warn if the data load generated a log file and override the exit code
		logFile = str(kargs.get('logFile'))
		if os.path.isfile(logFile):
			print 'WARNING : THE LOAD GENERATED A LOG FILE'
			print ''
			logging.warning('THE LOAD GENERATED A LOG FILE')
			logFileRecords = fileHelper.read_logs(logFile, 5)
			#exitCode = 299


		# Based upon the exit code, communicate status of the process
		if exitCode == 0:
			status = 'PROCESS COMPLETE'
			# Set exitCode to be 200
			exitCode = 200
		elif 201 <= exitCode <= 299:
			status = 'PROCESS COMPLETED WITH WARNINGS'
		elif 400 <= exitCode <= 599:
			status = 'PROCESS COMPLETED WITH ERRORS'
		else:
			status = 'OUTSIDE OF RANGE'

		return exitCode, status, logFileRecords

	# Test fucnction
	def console_test(self, status, output, exitCode):
		print 'Status: %s' % status
		print 'Output:'
		print output
		print 'Exit Code: %s' % exitCode


class file_system_operations:

	# If a directory exists delete it and provide a message
	def delete_dir_if_exists(self, dirToDelete, msg, msgToConsole, msgToLog):
		self.deleteDir = True
		fileDir = glob.glob(dirToDelete)
		if fileDir:
			try:
				shutil.rmtree (dirToDelete)
				if msgToConsole: print msg
				if msgToLog: logging.info(msg)

			except:
				self.deleteDir = False
				if msgToConsole: print 'FAILED: %s' % msg
				if msgToLog: logging.error('FAILED: %s' % msg)
				pass
		else:
			print 'FAILED - Not a Directory: %s' % dirToDelete
			logging.error('FAILED - Not a Directory: %s' % dirToDelete)
			self.deleteDir = False


	# Read a log file and return the top # of records
	def read_logs(self, logFile, readCount):
		logFileRecords = ''
		i = 0
		# Open Log File
		logFileObj = open(logFile, 'r')

		for line in logFileObj:
			if i > readCount:
				break
			logFileRecords += line
			i += 1

		print 'ERROR RECORDS'
		print '*************'
		print logFileRecords
		return logFileRecords


	# Read a log file in a particular directory and return the top # of records
	def read_logs_in_dir(self, processLogDir, readCount):
		logFileRecords = ''
		i = 0

		# Get List of Log Files
		fileList = glob.glob('%s/%s' % (processLogDir, '*'))
		for file in fileList:

			# Add an entry for the log
			fileRoot, fileExt = os.path.split('%s' % file)
			logFileRecords += 'Log File %s' % fileExt

			# Open Log File
			logFileObj = open(file, 'r')
			for line in logFileObj:
				if i > readCount:
					break
				logFileRecords += line
				i += 1

		print 'ERROR RECORDS'
		print '*************'
		print logFileRecords
		return logFileRecords


	# Create a temporary object
	def materialize(self, dataPayload):

		# Get Number of records and size of the data payload
		payloadSize = len(dataPayload)
		numLines = len(dataPayload.splitlines()) - 1

		# Materialize Object
		allChar = string.ascii_letters + string.digits
		ephemeral = "".join(choice(allChar) for x in range(randint(32, 32)))
		ephemeral = '%s/%s' % (getvar.tempDir, ephemeral)
		ephemeralObj = open(ephemeral, 'w')

		for line in dataPayload:
			ephemeralObj.write(line)

		ephemeralObj.close()

		return ephemeral, payloadSize, numLines


	# Remove a temporary object
	def dematerialize(self, ephemeral):
		try:
			os.remove(ephemeral)
			return True

		except:
			return False

