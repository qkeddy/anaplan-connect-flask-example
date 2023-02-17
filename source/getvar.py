#--------------------------------------------------------------------------------
# Name:     get.py
# Desc:     Helper class to centrally store variables. Variables are also set based
#			based upon ENV settings.
# Output:   None
# Update Notes:
#   2/12/2017 - Initial deployment
#	4/12/2017 - Near final release
#   
#--------------------------------------------------------------------------------

import os
import glob

def set_vars(environment):
	if (environment == 'PROD' or environment == 'DEV'):
		certificate = glob.glob('/certificates/*.cer')
		anaplanConnectPath = '/anaplanconnect/AnaplanClient.sh'
		logFilePath = '/logs'
	elif environment == 'DEV2':
		certificate = glob.glob('/Users/user/dev/customers/google/certificates/dev2/*.cer')
		anaplanConnectPath = '/Users/user/Dropbox/dev/anaplan-connect-1-3-3-3/AnaplanClient.sh'
		logFilePath = '/Users/user/dev/customers/google/logs'
	return certificate[0], anaplanConnectPath, logFilePath

########### Variable Definitions ###########
retryCnt = 1  # Retry count upon Error
chunkSize = 4096
printChunks = False
consoleOut = True
debugOut = True
environment = os.environ['ENV']

anaplanAPI = 'https://api.anaplan.com/1/3'
tempDir = '/tmp'

certificate =  set_vars(environment)[0]
anaplanConnectPath = set_vars(environment)[1]
logFilePath = set_vars(environment)[2]