# Zendesk Ticket Scanner

#### Scan the desired history of your Zendesk tickets for sensitive information (like PII and API keys) with Nightfall's data loss prevention (DLP) APIs.

This service uses Nightfall's [data loss prevention (DLP) APIs](https://nightfall.ai/developer-platform) to scan all tickets across your Zendesk account.

###### How it works
The service will (1) retrieve all Zendesk tickets (comments and attachment files) from the day range that you set, (2) send each ticket to Nightfall to be scanned, (3) scan the full ticket body and file attachments with Nightfall as long as it is in the desired scan date range, (4) retrieves sensitive results back from Nightfall, and (5) sends an alert to your alert destination of choice (email/Slack/webhook) that will contain a link to download the findings.

## Prerequisites

* Nightfall account - [sign up](https://app.nightfall.ai/sign-up) for free if you don't have an account
* Zendesk Admin User account
* Zendesk API Key

## Usage

1. Install dependencies. Add the `-U` flag to ensure you're using the latest versions of these packages.

```bash
pip install -r requirements.txt
```

2. Create a Developer Platform Policy (https://docs.nightfall.ai/docs/creating-policies) in the Nightfall console. This will define which detection rule and sensitive data you are looking for, as well as the alert destination of choice. You can select either a Webhook endpoint, an email address, or a Slack channel.

You'll need the Policy UUID for an upcoming step. 

Note: If selecting a Slack channel, you will first have to make sure that you have our Slack alerting app installed in your environment. This can be seen from the Nightfall console, by going to Settings -> Alert Platforms, and selecting Install for Slack. Once this has been installed, you can create a new channel for your Zendesk alerts, call it '#nightfall-zendesk-alerts' (the name can be anything). You will have to make sure that the 'Nightfall Alerts' app is also in this channel, and once it has been added, then you can add the channel name in your Nightfall API Policy in the console.

3. Get Zendesk details. You'll need your Zendesk User, Zendesk API Key, and Zendesk subdomain for the next step.

4. Set your environment variables: your Nightfall API key, your Nightfall API Policy UUID (from earlier step), and your desired scanning range. (by # of days)

```bash
export NIGHTFALL_API_KEY=<your Nightfall key here>
export NIGHTFALL_POLICY_UUID=<UUID of your Policy from the Nightfall console>
export ZENDESK_USER=<your Zendesk Admin account user here>
export ZENDESK_API_KEY=<your Zendesk API Key here>
export ZENDESK_ORG=<your Zendesk subdomain>
export PAST_DAY_RANGE=<number of days into the past you would like to scan, eg. 7 if the past week is desired>
```

5. In a new process/window, run your scan. Ensure your environment variables are set in this new window as well.

```python
python zendesk-scanner.py
```

6. Monitor your alert platforms. You will see an email/Slack alert/webhook event for each file that includes a finding. 

You will see a link to the findings for you to download and review. You will also see relevant metadata for any files that have triggered: Ticket ID, Comment ID, Attachment ID, Attachment File Name

## Summary

###### Solution:

The service works by downloading a temporary local copy of tickets in a directory called `zendesk-tickets-temp` in the same directory in which the script is executed. These temporary files are removed as soon as they are scanned, as well a the full directory at the end of successful execution. If the scan errors midway through execution, these temporary files may not be removed completely. In which case, you can use the `delete_all_repos()` function in `zendesk-scanner.py` or simply delete the `zendesk-tickets-temp` directory and retry.

---


## License

This code is licensed under the terms of the MIT License. See [here](LICENSE.md) for more information.