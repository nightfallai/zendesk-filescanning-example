import os
from nightfall import Confidence, DetectionRule, Detector, RedactionConfig, MaskConfig, AlertConfig, WebhookAlert, SlackAlert, EmailAlert, Nightfall
from os import mkdir, walk
import json
import requests
import shutil
import time
from datetime import datetime, date, timedelta

zendesk_user = os.environ.get('ZENDESK_USER')
zendesk_api_key = os.environ.get('ZENDESK_API_KEY')
nightfall_api_key = os.environ.get('NIGHTFALL_API_KEY')
policy_uuid = os.environ.get('NIGHTFALL_POLICY_UUID')
date_range = os.environ.get('PAST_DAY_RANGE')
zendesk_auth = (f"{zendesk_user}/token",zendesk_api_key)
zendesk_org = os.environ.get('ZENDESK_ORG')

zendesk_base_url = f"https://{zendesk_org}.zendesk.com/api/v2/"

#start_date = datetime.fromisocalendar(str(date.today() - timedelta(days=int(date_range))))
start_date = (datetime.now() - timedelta(days=int(date_range))).strftime(f"%Y-%m-%dT%H:%M:%SZ")
start_datetime = datetime.strptime(start_date, f"%Y-%m-%dT%H:%M:%SZ")


# iterate through all tickets, retrieve ticket comment bodies and download each attachment in the desired time frame to scan with Nightfall detection rules
def get_tickets(dir):
	try:
		os.mkdir(dir)
	except:
		pass

	zendesk_auth = (f"{zendesk_user}/token",zendesk_api_key)

	zendesk_response = requests.get(
		url = f"{zendesk_base_url}tickets.json?sort_by=created_at&sort_order=desc", 
		auth = zendesk_auth
	)

	tickets = json.loads(zendesk_response.text)['tickets']

	for ticket in tickets:
		ticket_id = ticket['id']
		# use the created_at field to gauge creation time - result in format "2009-07-20T22:55:29Z"

		
		ticket_creationtime = datetime.strptime(ticket['created_at'], f"%Y-%m-%dT%H:%M:%SZ")	

		if(ticket_creationtime > start_datetime):	
			print(f"Ticket {ticket_id} created at: {ticket_creationtime} is being scanned.")
			ticket_response = requests.get(
			url = f"{zendesk_base_url}tickets/{ticket_id}/comments.json",
			auth = zendesk_auth
			)

			comments = json.loads(ticket_response.text)['comments']

			for comment in comments:
				#commentbody = comment['plain_body']
				#print(comment['body'])
				comment_id = comment['id']
				scan_comment(comment['body'], ticket_id, comment_id) 
				attachments = comment['attachments']
				for attachment in attachments:
					#print(f"Attachment: {attachment}")
					resp = requests.get(attachment['content_url'])
					filepath = f"{dir}/{attachment['file_name']}"
					open(filepath, "wb").write(resp.content)
					scan_attachment(filepath, ticket_id, attachment['id'], attachment['file_name'])
					os.remove(filepath)

# send ticket comments to text scanning endpoint to be scanned
def scan_comment(payload, ticket_id, comment_id):
	nightfall = Nightfall() # reads API key from NIGHTFALL_API_KEY environment variable by default

	try:
		filepath = f"{dir}/ticket{ticket_id}comment{comment_id}.txt"
		open(filepath, "w").write(payload)
		metadata = { "filepath": filepath, "ticket_id": ticket_id, "comment_id": comment_id}
		metadata = json.dumps(metadata)
		# scan with Nightfall
		print(f"\tScanning text of comment {comment_id} for Zendesk ticket {ticket_id}: {filepath}")
		scan_id, message = nightfall.scan_file(
			filepath, 
			policy_uuid=policy_uuid,
			request_metadata=metadata)
		print("\t\t", scan_id, message)
		os.remove(filepath)

		time.sleep(5) # This may need to be edited depending on rate limiting and available API requests
	except Exception as err:
		print(err)

# send ticket attachment to Nightfall file scanning endpoint to be scanned
def scan_attachment(filepath, ticket_id, attachment_id, file_name):
	nightfall = Nightfall() # reads API key from NIGHTFALL_API_KEY environment variable by default
	detection_rule_uuids = os.getenv('NIGHTFALL_DETECTION_RULE_UUIDS') # takes in comma separated list of Detection Rule UUIDs
	detection_rule_uuids = [ str.strip() for str in detection_rule_uuids.split(",") ]

	try:
		print(f"\tScanning an attachment file on ticket {ticket_id}: {filepath}")
		metadata = { "filepath": filepath, "ticket_id": ticket_id, "attachment_id": attachment_id, "file_name": file_name}
		metadata = json.dumps(metadata)
		# scan with Nightfall
		scan_id, message = nightfall.scan_file(
			filepath, 
			policy_uuid=policy_uuid,
			request_metadata=metadata)
		print("\t\t", scan_id, message)
		time.sleep(5) # This may need to be edited depending on rate limiting and available API requests
	except Exception as err:
		print(err)

# clean up all downloaded s3 objects
def delete_all_tickets(dir):
	print("Cleaning up")
	shutil.rmtree(dir)

dir = 'zendesk-tickets-temp'
get_tickets(dir)
delete_all_tickets(dir)