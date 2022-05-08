import os
from tracemalloc import start
from nightfall import Confidence, DetectionRule, Detector, RedactionConfig, MaskConfig, AlertConfig, WebhookAlert, SlackAlert, EmailAlert, Nightfall
from os import mkdir, walk
import json
import shutil
import time
import boto3
from datetime import datetime, date, timedelta

#aws_session_token = os.environ.get('AWS_SESSION_TOKEN')
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
email_address = os.environ.get('ALERT_EMAIL_ADDRESS')
date_range = os.environ.get('PAST_DAY_RANGE')

start_date = datetime.fromisoformat(str(date.today() - timedelta(days=int(date_range))))

# iterate through all buckets, download each object in the desired time frame and scan with Nightfall detection rules
def download_all_objects(dir):
	try:
		os.mkdir(dir)
	except:
		pass

	my_session = boto3.session.Session(
		aws_access_key_id = aws_access_key_id,
		aws_secret_access_key = aws_secret_access_key
	)

	s3 = my_session.resource('s3')

	for bucket in s3.buckets.all():
		for obj in bucket.objects.all():
			if obj.key[-1] == "/": # This will filter out folder names that come in form <foldername>/ in the S3 response
				os.mkdir(dir + '/' + obj.key) # This will create the temporary dirctory for files in subfolders
				continue
			else:
				print('Checking Last Modified Time for ', obj.key)
				print('Last Modified Time: ', obj.last_modified)
				if(obj.last_modified.replace(tzinfo = None) > start_date):
					filepath = dir + '/' + obj.key
					print(filepath)
					bucket.download_file(obj.key, filepath)
					scan_object(filepath)

# send s3 object to Nightfall to be scanned
def scan_object(filepath):
	nightfall = Nightfall() # reads API key from NIGHTFALL_API_KEY environment variable by default
	detection_rule_uuids = os.getenv('NIGHTFALL_DETECTION_RULE_UUIDS') # takes in comma separated list of Detection Rule UUIDs
	detection_rule_uuids = [ str.strip() for str in detection_rule_uuids.split(",") ]

	try:
		print(f"\tScanning object: {filepath}")
		metadata = { "filepath": filepath}
		metadata = json.dumps(metadata)
		# scan with Nightfall
		scan_id, message = nightfall.scan_file(filepath, 
			alert_config=AlertConfig(email=EmailAlert(email_address)),
			detection_rule_uuids=detection_rule_uuids, 
			request_metadata=metadata)
		print("\t\t", scan_id, message)
		time.sleep(5) # This may need to be edited depending on rate limiting and available API requests
	except Exception as err:
		print(err)

# clean up all downloaded s3 objects
def delete_all_objects(dir):
	print("Cleaning up")
	shutil.rmtree(dir)

dir = 's3-objects-temp'
download_all_objects(dir)
delete_all_objects(dir)