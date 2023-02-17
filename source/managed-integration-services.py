#--------------------------------------------------------------------------------
# Name:     managed-integration-services.py
# Desc:     Main execution file for MIS REST inteface with endpoints to listen for 
#			commands for importing and exporting data into and out of Anapalan
# Output:   None
# Update Notes:
#   2/12/2017 - Initial deployment
#	4/12/2017 - Stable code
#   
#--------------------------------------------------------------------------------


from flask import Flask, jsonify, request, make_response, abort
from functools import wraps
import timeit
import os
import anaplanapi
import getvar
import automationhelper
import time
import logging
from flask_httpauth import HTTPBasicAuth
import sendmail

app = Flask(__name__)
anaplanAPI = anaplanapi.anaplan_actions()
fileHelper = automationhelper.file_system_operations()
auth = HTTPBasicAuth()

# Users
users = {
    "test": "password",
}

# Setup Logger
localTime = time.strftime("%Y%m%d", time.localtime())
logFile = '%s-MIS.LOG' % localTime
fullPathLogFile = '%s/%s' % (getvar.logFilePath, logFile)
logFileLevel = logging.INFO  # Options: INFO, WARNING, DEBUG, INFO, ERROR, CRITICAL

logging.basicConfig(filename=fullPathLogFile,
					filemode='a',  # Append to Log
					format='%(asctime)s  :  %(levelname)s  :  %(message)s',
					level=logFileLevel)


@auth.get_password
def get_pw(username):
	if username in users:
		return users.get(username)
	return None


@auth.error_handler
def auth_error():
	return make_response(jsonify({'error': "invalid login"}), 401)

def create_json(exitCode, **kargs):
	# Populate variables from kargs
	output = ''
	status = ''
	processname = ''
	filename = ''
	numLines = ''
	fileSize = ''
	elapsed = ''
	actionname = ''
	logFileRecords = ''
	if 'output' in kargs: output = kargs.get('output')
	if 'status' in kargs: status = kargs.get('status')
	if 'processname' in kargs: processname = kargs.get('processname')
	if 'actionname' in kargs: actionname = kargs.get('actionname')
	if 'filename' in kargs: filename = kargs.get('filename')
	if 'numLines' in kargs: numLines = kargs.get('numLines')
	if 'fileSize' in kargs: fileSize = kargs.get('fileSize')
	if 'elapsed' in kargs: elapsed = kargs.get('elapsed')
	if 'logFileRecords' in kargs: logFileRecords = kargs.get('logFileRecords')

	if 400 <= exitCode <= 599:
		response = jsonify({'error': output,
							'status': status})

	else:
		response = jsonify({'status': status,
							'processname': processname,
							'actionname' : actionname,
							'filename': filename,
							'records': numLines,
							'filesize': fileSize,
							'runtime': elapsed,
							'anaplanmessage': output,
						   	'errorrecords' : logFileRecords}
						   )
	return response

# ROUTE #1 - REST endpoint to import data from an inbound data paylod (stream) and execute an Anaplan Process
@app.route('/1/0/workspaces/<workspaceid>/models/<modelid>/import/<filename>/<processname>', methods=['POST'])
@auth.login_required
def import_stream(filename, processname, workspaceid, modelid):
	startTime = timeit.default_timer()
	chunkSize = getvar.chunkSize
	printChunks = getvar.printChunks
	firstChunk = True
	dataPayload = ''

	# Check to see if it is an empty POST
	chunk = request.stream.read(chunkSize)
	if len(chunk) == 0:
		# Create custom JSON message based upon exitCode
		customJson = create_json(exitCode=500, output= 'No Data', status="EMPTY POST - DATA REQUIRED")

		# Return JSON in message body
		return make_response(customJson, 500)

	# Start reading data stream and load into variable
	while True:
		# Write the first chunk received
		if firstChunk:
			if printChunks: print(chunk)
			dataPayload += chunk
			firstChunk = False

		# Process next chunk and if size is 0, close the file and exit
		chunk = request.stream.read(chunkSize)
		if len(chunk) == 0:
			# Payload Processor
			dataPayloadObj, payloadSize, numLines = fileHelper.materialize(dataPayload)

			# Execute the Anaplan Load
			exitCode, output, status, logFileRecords = anaplanAPI.anaplan_import(sourceStream=dataPayloadObj,
																 				 targetFile=filename,
																 				 process=processname,
																 				 workspaceId=workspaceid,
																 				 modelId=modelid)

			# Close payload
			if fileHelper.dematerialize(dataPayloadObj):
				elapsed = round(timeit.default_timer() - startTime, 2)

				# Create custom JSON message based upon exitCode
				customJson= create_json(exitCode=exitCode, output=output, status=status,
										processname=processname, filename=filename,
										numLines=numLines, fileSize=payloadSize, elapsed=elapsed, logFileRecords=logFileRecords)

				# Return JSON in message body
				return make_response(customJson, exitCode)

		# If there is a an inbound stream, continue to write
		if printChunks: print(chunk)
		dataPayload += chunk


# ROUTE #2 - REST endpoint to import data from an inbound data paylod (file) and execute an Anaplan Process
@app.route('/1/0/workspaces/<workspaceid>/models/<modelid>/import_file/<filename>/<processname>', methods=['POST'])
@auth.login_required
def import_file(filename, processname, workspaceid, modelid):
	startTime = timeit.default_timer()
	loadFile = '%s/%s' % (getvar.fileInbox, filename)
	chunkSize = getvar.chunkSize
	printChunks = getvar.printChunks
	firstChunk = True

	# Check to see if it is an empty POST
	chunk = request.stream.read(chunkSize)
	if len(chunk) == 0:
		# Create custom JSON message based upon exitCode
		customJson = create_json(exitCode=500, output= 'No Data', status="EMPTY POST - DATA REQUIRED")

		# Return JSON in message body
		return make_response(customJson, 500)

	# Open file for writing
	with open(loadFile, 'w') as f:
		while True:
			# Write the first chunk received
			if firstChunk:
				if printChunks: print(chunk)
				f.write(chunk)
				firstChunk = False

			# Process next chunk and if size is 0, close the file and exit
			chunk = request.stream.read(chunkSize)
			if len(chunk) == 0:
				# Close file for writing
				f.close()
				fileSize = os.path.getsize(loadFile)
				numLines = sum(1 for line in open(loadFile)) - 1

				# Execute the Anaplan Load
				exitCode, output, status, logFileRecords = anaplanAPI.anaplan_import(sourceStream=loadFile,
																	 				 targetFile=filename,
																	 				 process=processname,
																	 				 workspaceId=workspaceid,
																	 				 modelId=modelid)

				elapsed = round(timeit.default_timer() - startTime, 2)

				# Create custom JSON message based upon exitCode
				customJson= create_json(exitCode=exitCode, output=output, status=status,
										processname=processname, filename=filename,
										numLines=numLines, fileSize=fileSize, elapsed=elapsed, logFileRecords=logFileRecords)

				# Return JSON in message body
				return make_response(customJson, exitCode)

			# If there is a an inbound stream, continue to write
			if printChunks: print(chunk)
			f.write(chunk)

# ROUTE #3 - REST endpoint to import data from an inbound data paylod (stream).
@app.route('/1/0/workspaces/<workspaceid>/models/<modelid>/upload/<filename>', methods=['POST'])
@auth.login_required
def upload_stream(filename, workspaceid, modelid):
	startTime = timeit.default_timer()
	chunkSize = getvar.chunkSize
	printChunks = getvar.printChunks
	firstChunk = True
	dataPayload = ''

	# Check to see if it is an empty POST
	chunk = request.stream.read(chunkSize)
	if len(chunk) == 0:
		# Create custom JSON message based upon exitCode
		customJson = create_json(exitCode=500, output= 'No Data', status="EMPTY POST - DATA REQUIRED")

		# Return JSON in message body
		return make_response(customJson, 500)

	# Start reading data stream and load into variable
	while True:
		# Write the first chunk received
		if firstChunk:
			if printChunks: print(chunk)
			dataPayload += chunk
			firstChunk = False

		# Process next chunk and if size is 0, close the file and exit
		chunk = request.stream.read(chunkSize)
		if len(chunk) == 0:
			# Payload Processor
			dataPayloadObj, payloadSize, numLines = fileHelper.materialize(dataPayload)

			# Execute the Anaplan Load
			exitCode, output, status = anaplanAPI.anaplan_upload(sourceStream=dataPayloadObj,
																 targetFile=filename,
																 workspaceId=workspaceid,
																 modelId=modelid)
			# Close payload
			if fileHelper.dematerialize(dataPayloadObj):

				elapsed = round(timeit.default_timer() - startTime, 2)

				# Create custom JSON message based upon exitCode
				customJson = create_json(exitCode=exitCode, output='N/A', status=status,
										 processname='N/A', filename=filename,
										 numLines=numLines, fileSize=payloadSize, elapsed=elapsed)

				# Return JSON in message body
				return make_response(customJson, exitCode)

		# If there is a an inbound stream, continue to write
		if printChunks: print(chunk)
		dataPayload += chunk

# ROUTE #4 - REST endpoint to import data from an inbound data paylod (file)
@app.route('/1/0/workspaces/<workspaceid>/models/<modelid>/upload_file/<filename>', methods=['POST'])
@auth.login_required
def upload_file(filename, workspaceid, modelid):
	#print('Received file {0}:'.format(sourcefile))
	startTime = timeit.default_timer()
	loadFile = '%s/%s' % (getvar.fileInbox, filename)
	chunkSize = getvar.chunkSize
	printChunks = getvar.printChunks
	firstChunk = True

	# Check to see if it is an empty POST
	chunk = request.stream.read(chunkSize)
	if len(chunk) == 0:
		# Create custom JSON message based upon exitCode
		customJson = create_json(exitCode=500, output= 'No Data', status="EMPTY POST - DATA REQUIRED")

		# Return JSON in message body
		return make_response(customJson, 500)

	# Open file for writing
	with open(loadFile, 'w') as f:
		while True:
			# Write the first chunk received
			if firstChunk:
				if printChunks: print(chunk)
				f.write(chunk)
				firstChunk = False

			# Process next chunk and if size is 0, close the file and exit
			chunk = request.stream.read(chunkSize)
			if len(chunk) == 0:
				# Close file for writing
				f.close()
				fileSize = os.path.getsize(loadFile)
				numLines = sum(1 for line in open(loadFile)) - 1

				# Execute the Anaplan Load
				exitCode, output, status = anaplanAPI.anaplan_upload(sourceStream=loadFile,
																	 targetFile=filename,
																	 workspaceId=workspaceid,
																	 modelId=modelid)

				elapsed = round(timeit.default_timer() - startTime, 2)

				# Create custom JSON message based upon exitCode
				customJson= create_json(exitCode=exitCode, output='N/A', status=status,
										processname='N/A', filename=filename,
										numLines=numLines, fileSize=fileSize, elapsed=elapsed)

				# Return JSON in message body
				return make_response(customJson, exitCode)

			# If there is a an inbound stream, continue to write
			if printChunks: print(chunk)
			f.write(chunk)

# ROUTE #5 - REST endpoint to execute an Anaplan Process
@app.route('/1/0/workspaces/<workspaceid>/models/<modelid>/process/<processname>', methods=['POST'])
@auth.login_required
def exec_process (processname, workspaceid, modelid):
	#print('Received file {0}:'.format(sourcefile))
	startTime = timeit.default_timer()

	# Execute the Anaplan Load
	exitCode, output, status, logFileRecords = anaplanAPI.anaplan_process(process=processname,
														  workspaceId=workspaceid,
														  modelId=modelid)

	elapsed = round(timeit.default_timer() - startTime, 2)

	# Create custom JSON message based upon exitCode
	customJson = create_json(exitCode=exitCode, output=output, status=status,
							 processname=processname, filename='N/A',
							 numLines='N/A', fileSize='N/A', elapsed=elapsed, logFileRecords=logFileRecords)

	# Return JSON in message body
	return make_response(customJson, exitCode)

# ROUTE #6 - REST endpoint to execute an Anaplan Import Action
@app.route('/1/0/workspaces/<workspaceid>/models/<modelid>/action/<actionname>', methods=['POST'])
@auth.login_required
def exec_action (actionname, workspaceid, modelid):
	#print('Received file {0}:'.format(sourcefile))
	startTime = timeit.default_timer()

	# Execute the Anaplan Load
	exitCode, output, status, logFileRecords = anaplanAPI.anaplan_action(action=actionname,
																		 workspaceId=workspaceid,
																		 modelId=modelid)

	elapsed = round(timeit.default_timer() - startTime, 2)

	# Create custom JSON message based upon exitCode
	customJson = create_json(exitCode=exitCode, output=output, status=status,
							 actionname=actionname, processname='N/A', filename='N/A',
							 numLines='N/A', fileSize='N/A', elapsed=elapsed, logFileRecords=logFileRecords)

	# Return JSON in message body
	return make_response(customJson, exitCode)

# ROUTE #7 - REST endpoint to execute an Anaplan Export Action and deliver a datapayload in the response body
@app.route('/1/0/workspaces/<workspaceid>/models/<modelid>/export/<exportname>', methods=['POST', 'GET'])
@auth.login_required
def export_data(exportname, workspaceid, modelid):
	# Execute Anaplan Action and wait for the data payload is ready (completion of the Export Action)
	# Get Anaplan Server File which is the same name (AND ID) as the Export Action
	# Receive the payload

	startTime = timeit.default_timer()

	exitCode, output, status = anaplanAPI.anaplan_export(exportname, workspaceid, modelid)

	elapsed = round(timeit.default_timer() - startTime, 2)

	# Create custom JSON message based upon exitCode
	if 400 <= exitCode <= 599:
		# Create custom JSON message based upon exitCode
		customJson = create_json(exitCode=exitCode, output=output, status=status)

		# Return JSON in message body
		return make_response(customJson, exitCode)

	else:
		return output

@app.route('/1/0/workspaces/<workspaceid>/models/<modelid>/email/<emailaddress>/<firstname>/<lastname>/<company>', methods=['POST', 'GET'])
@auth.login_required
def email(emailaddress, firstname, lastname, company, workspaceid, modelid):

	print '***************************'
	print workspaceid
	print modelid
	print emailaddress
	print '%s %s' % (firstname,lastname)
	print company

	try:
		sendmail.send_thankyou(email=emailaddress, firstName=firstname, lastName=lastname, company=company)
		return make_response(jsonify({'firstname': firstname,
									  'lastname': lastname,
									  'company': company,
									  'Your Email': emailaddress}), 200)
	except:
		abort(406)



@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': error.description}), 404)


@app.errorhandler(406)
def not_found(error):
	return make_response(jsonify({'error': 'unspecified failure'}), 406)


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5001, debug=True)



