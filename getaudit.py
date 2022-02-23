import requests 
import argparse
import json
import sys
#import urllib.parse
import datetime
import base64
import email.utils
import hashlib
import time

#
# (c) Inge Os 2020
#
# Last modified 3/7-2020
# 
# Usage: --configfile ocireport.json --report all|storage|compute|compartments|dbcs --usage all|inuse|stopped
#
# Compiled for Python 2.7.x
#
# pip install httpsig_cffi requests six
import httpsig_cffi.sign
import six

#
#  Calls oracle OCI with plain REST
#
# define globals
blocksize=0
bootsize=0
#
#  Json holds config data, sould be local
configData={}

# Version 1.0.1
progVersion="2230222"

class SignedRequestAuth(requests.auth.AuthBase):
	"""A requests auth instance that can be reused across requests"""
	generic_headers = [
		"date",
		"(request-target)",
		"host"
	]
	body_headers = [
		"content-length",
		"content-type",
		"x-content-sha256",
	]
	required_headers = {
		"get": generic_headers,
		"head": generic_headers,
		"delete": generic_headers,
		"put": generic_headers + body_headers,
		"post": generic_headers + body_headers
	}

	def __init__(self, key_id, private_key):
		# Build a httpsig_cffi.requests_auth.HTTPSignatureAuth for each
		# HTTP method's required headers
		self.signers = {}
		for method, headers in six.iteritems(self.required_headers):
			signer = httpsig_cffi.sign.HeaderSigner(
				key_id=key_id, secret=private_key,
				algorithm="rsa-sha256", headers=headers[:])
			use_host = "host" in headers
			self.signers[method] = (signer, use_host)

	def inject_missing_headers(self, request, sign_body):
		# Inject date, content-type, and host if missing
		request.headers.setdefault(
			"date", email.utils.formatdate(usegmt=True))
		request.headers.setdefault("content-type", "application/json")
		request.headers.setdefault(
			"host", six.moves.urllib.parse.urlparse(request.url).netloc)

		# Requests with a body need to send content-type,
		# content-length, and x-content-sha256
		if sign_body:
			body = request.body or ""
			if "x-content-sha256" not in request.headers:
				m = hashlib.sha256(body.encode("utf-8"))
				base64digest = base64.b64encode(m.digest())
				base64string = base64digest.decode("utf-8")
				request.headers["x-content-sha256"] = base64string
			request.headers.setdefault("content-length", len(body))

	def __call__(self, request):
		verb = request.method.lower()
		# nothing to sign for options
		if verb == "options":
			return request
		signer, use_host = self.signers.get(verb, (None, None))
		if signer is None:
			raise ValueError(
				"Don't know how to sign request verb {}".format(verb))

		# Inject body headers for put/post requests, date for all requests
		sign_body = verb in ["put", "post"]
		self.inject_missing_headers(request, sign_body=sign_body)

		if use_host:
			host = six.moves.urllib.parse.urlparse(request.url).netloc
		else:
			host = None

		signed_headers = signer.sign(
			request.headers, host=host,
			method=request.method, path=request.path_url)
		request.headers.update(signed_headers)
		return request


# 
#  get audit for a given time
# uri endpoint for compartments starts with identity not iaas as the main uri
#
# Example
# main URI
#	https://iaas.eu-frankfurt-1.oraclecloud.com
# compartmen URI
#	https://identity.eu-frankfurt-1.oraclecloud.com
#
def getAudit(configData,auth,etime,stime,jsonfile):
	global httpStatusCode
	#
	# create headers
	#
	headers = {
	"content-type": "application/json",
	"date": email.utils.formatdate(usegmt=True),
	}

	apiUri=configData['iaasAPIUri'].replace('iaas','audit')
	compartmentEndPoint='/20190901/auditEvents'
	rootCompartmentId=configData['tenantOCID']
	cId=rootCompartmentId.replace(":", "%3A")
	uri = apiUri+compartmentEndPoint+"?compartmentId={compartmentId}"
	uri = uri.format(compartmentId=cId)
	uri=uri+"&endTime="+etime+"&startTime="+stime
	print("URL: "+uri)
	response = requests.get(uri, auth=auth, headers=headers)
	httpStatusCode=response.status_code
	if  httpStatusCode> 300:
		print("Status code: "+str(httpStatusCode))
		print(response)
		return(False)
	else:
		f = open(jsonfile, "w")
		f.write(response.text)
		f.close()	
		return(True)


#
#  getSessionAuth
#	generates authorization token for the sessions
# Retutn token
# 	flow:
# 		retrieve private key
#		generate API key
#		build the authorization token
#

def getSessionAuth(sessionConfig):
	#
	# Get your private key that matches public ke on API key
	#
	with open(sessionConfig['privateKeyFile']) as f:
		private_key = f.read().strip()
	#
	# Assembly the API Key
	#
	api_key = "/".join([
		sessionConfig['tenantOCID'],
 		sessionConfig['userOCID'],
 		sessionConfig['fingerPrint']
 	])
	#
	# Build the authorisation token
	#
	return(SignedRequestAuth(api_key, private_key))

#
#  Inge Os 1/6-2021
#  Parse arguments, load configfile
#  Arguments: --configfile  json formatted file containint, OCI URL, tennantOCID, API KEy File, userOCID, key fingerPrint
#
# 	
def main():	
	#
	#
	global configData
	CDATE='`date -u "+%a, %d %h %Y %H:%M:%S GMT"`'
	#
	# Parse Arguments
	#
	now=time.time()
	stime=time.strftime('%Y-%m-%dT%H:%M:%S',time.gmtime(now-3600))
	etime=time.strftime('%Y-%m-%dT%H:%M:%S',time.gmtime(now))
	argsParser=argparse.ArgumentParser(description='OCI Usage report')
	argsParser.add_argument("--configfile",default="ocireport.json",type=str,help="Filename of JSON config file")
	argsParser.add_argument("--starttime",default=stime,type=str,help="Start time in format like 2022-15-05T07:00:00")
	argsParser.add_argument("--endtime",default=etime,type=str,help="Start time in format like 2022-15-05T09:00:00")
	argsParser.add_argument("--outfile",default="ociaudit.json",type=str,help="Start time in format like 2022-15-05T09:00:00")
	args=argsParser.parse_args()
	configFile=args.configfile
	#
	# Welcome Message
	#
	print("\nOCI audit exploration tool")
	print("Version: "+progVersion+" (c) Inge Os 2022")	
	#
	# Open Configfile and check for valid config parameters
	#
	configItem={"iaasAPIUri","tenantOCID","userOCID","fingerPrint","privateKeyFile"}
	#
	# Load config data from config file
	#
	with open(configFile, 'r') as file: 
		configData = json.loads(file.read().replace('\n', ''))
	#	
	# Iterate through and verify consistency
	#
	for cname in list(configItem):
		if cname not in configData:
			print(cname+" not found in config file: "+configFile)
			exit(1)
	# 
	# Perform onetime authentication for usage of OCI get session token
	#
	authToken=getSessionAuth(configData)

	#
	# Use rest to lookup the audit for teh given period
	#

	result=getAudit(configData,authToken,args.endtime,args.starttime,args.outfile)
	if result:
		print("audit trail stroed in: "+args.outfile)
	else:
		print("Fecth of Audit failed :-(")


if __name__ == '__main__':
	main()

