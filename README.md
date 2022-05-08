# S3 Object File Scanner

#### Scan the desired history of your S3 Buckets and Objects for sensitive information (like PII and API keys) with Nightfall's data loss prevention (DLP) APIs.

This service uses Nightfall's [data loss prevention (DLP) APIs](https://nightfall.ai/developer-platform) to scan all buckets across your AWS S3 account.

###### How it works
The service will (1) retrieve all s3 buckets that the associated IAM role has access for, (2) send each object in the bucket to Nightfall to be scanned, (3) scan the full object with Nightfall as long as it is in the desired scan date range, (4) retrieves sensitive results back from Nightfall, and (5) sends an email to your desired address with a link to the findings file. This output will provide any findings of sensitive data at-rest in your S3 buckets. 

## Prerequisites

* Nightfall account - [sign up](https://app.nightfall.ai/sign-up) for free if you don't have an account
* AWS Account
* IAM Role for Bucket Access - you'll need access to list/download the bucket objects you wish to scan
* AWS Access Key Id for the above IAM Role
* AWS Secret Access Key for the above IAM Role

## Usage

1. Install dependencies. Add the `-U` flag to ensure you're using the latest versions of these packages.

```bash
pip install -r requirements.txt
```

2. Create a [Detection Rule](https://docs.nightfall.ai/docs/creating-detection-rules) in the Nightfall console. This will define what sensitive data you are looking for. You'll need your detection rule UUID for an upcoming step. You can create and use multiple detection rule UUIDs if you'd like.

3. Get S3 details. You'll need your AWS Access Key ID and Secret Access Key for the next step.

4. Set your environment variables: your Nightfall API key, your Nightfall signing secret, your Nightfall [detection rule UUIDs](https://docs.nightfall.ai/docs/creating-detection-rules) (from earlier step), your webhook server URL from ngrok, and your GitHub or GitLab details (from earlier step).

```bash
export NIGHTFALL_API_KEY=<your key here>
export NIGHTFALL_SIGNING_SECRET=<your secret here>
export NIGHTFALL_DETECTION_RULE_UUIDS=<comma separated list of your detection rule uuids>
export NIGHTFALL_SERVER_URL=https://<your server subdomain>.ngrok.io
export AWS_ACCESS_KEY_ID=<your key id here>
export AWS_SECRET_ACCESS_KEY=<your secret access key here>
export ALERT_EMAIL_ADDRESS=<your desired email address to have alerts sent>
export PAST_DAY_RANGE=<number of days into the past you would like to scan, eg. 7 if the past week is desired>
```

5. In a new process/window, run your scan. Ensure your environment variables are set in this new window as well.

```python
python s3-scanner.py
```

6. Monitor your email. You will see an email for each file that includes a finding. The email will be as follows:

Subject: 🚨 Findings Detected by Nightfall! 🚨
Content: 
"Findings have been detected as part of a recent scan request to Nightfall.

See the attached file for more information."

At attached json file will include a link to a pre-signed s3 URL that can be used to download the findings. The json will also include the filename of the associated findings.

## Summary

###### Solution:

The service works by downloading a temporary local copy of s3 objects in a directory called `s3-objects-temp` in the same directory in which the script is executed. These temporary files are cleaned up at the end of successful execution. If the scan errors midway through execution, these temporary files may not be removed completely. In which case, you can use the `delete_all_repos()` function in `s3-scanner.py` or simply delete the `s3-objects-temp` directory and retry.

---


## License

This code is licensed under the terms of the MIT License. See [here](LICENSE.md) for more information.