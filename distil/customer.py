import sys
import os
import re
from urllib import urlencode
from operator import itemgetter
from itertools import chain
import json
# dateutil is a useful helper library, you may need to install the
# `python-dateutil` package especially
from dateutil.parser import *
from dateutil.tz import *
# Fuck urllib2, that's effort. You may need to `pip install requests`.
# http://docs.python-requests.org/en/latest/index.html
import requests

class MissingAuth(Exception): pass

def get_contacts(contact_list):
    # Prepare auth
    auth_user = os.environ.get('API_AUTH_USER')
    auth_pass = os.environ.get('API_AUTH_PASS')
    if not auth_user or not auth_pass:
        raise MissingAuth("You must provide Anchor API credentials, please set API_AUTH_USER and API_AUTH_PASS")

    # Prep URL and headers for requests
    headers = {}
    headers['Accept'] = 'application/json'

    for contact in contact_list:
        print contact
        customer_response = requests.get(contact, auth=(auth_user,auth_pass), verify=True, headers=headers)
        try:
            customer_response.raise_for_status()
        except:
            raise FailedToRetrieveCustomer("Couldn't get customer from API, HTTP error %s, probably not allowed to view customer" % customer_response.status_code)




def blobify(url):
    # Note to self: yield'ing is cool. Either yield, return None, or raise
    # an exception. The latter is some other poor schmuck's problem.

        # Prepare auth
    auth_user = os.environ.get('API_AUTH_USER')
    auth_pass = os.environ.get('API_AUTH_PASS')
    if not auth_user or not auth_pass:
        raise MissingAuth("You must provide Anchor API credentials, please set API_AUTH_USER and API_AUTH_PASS")

    # Prep URL and headers for requests
    headers = {}
    headers['Accept'] = 'application/json'

    customer_response = requests.get(url, auth=(auth_user,auth_pass), verify=True, headers=headers)
    try:
        customer_response.raise_for_status()
    except:
        raise FailedToRetrieveCustomer("Couldn't get customer from API, HTTP error %s, probably not allowed to view customer" % customer_response.status_code)

    # Mangle customer until no good
    customer_json_blob = customer_response.content # FIXME: add error-checking
    customer = json.loads(customer_json_blob)

    customer_url         = url
    customer_number      = customer['_id']
    primary_contacts     = get_contacts(customer['primary_contact_url_list'])
    billing_contacts     = get_contacts(customer['billing_contact_url_list'])
    alternative_contacts = get_contacts(customer['alternative_contact_url_list'])

        # Put together our response. We have:
    # - customer_url (string)
    # - customer_subject (string)
    # - customer_status (string)
    # - customer_queue (string)
    # - customer_category (string or None)
    # - customer_priority (int)
    # - messages (iterable of dicts)
    # - public_messages (iterable of dicts)
    # - public_customer_excerpt (string)

    blob = " ".join([
        customer_number.encode('utf8'),
        customer_subject.encode('utf8'),
        ' '.join(realnames).encode('utf8'),
        ' '.join(emails).encode('utf8'),
        ' '.join(all_message_lines).encode('utf8'),
        ])

    customerblob = {
        'url':              customer_url,
        'blob':             blob,
        'local_id':         customer_number,
        'title':            customer_subject, # printable as a document title
        'excerpt':          customer_excerpt,
        'subject':          customer_subject,
        'status':           customer_status,
        'queue':            customer_queue,
        'priority':         customer_priority,
        'realname':         realnames,
        'email':            emails,
        'last_updated':     customer_lastupdated,
        'customer_visible': customer_visible,
        }

    # Only set category if it's meaningful
    if customer_category:
        customerblob['category'] = customer_category

    # Only set public_blob if we've got it
    if public_blob:
        customerblob['public_blob'] = public_blob

    # Only set last_contact if it has meaning
    if contact_timestamps:
        customerblob['last_contact'] = max(contact_timestamps).astimezone(tzutc())

    # Only set customer details if we have that metadata
    if customer_id:
        customerblob['customer_id'] = customer_id

    if customer_name:
        customerblob['customer_name'] = customer_name

    if customer_url:
        customerblob['customer_url'] = customer_url

    maybe_customer_details = ' '.join(  [ x for x in (customer_name,customer_id) if x is not None ]  )
    if maybe_customer_details:
        customerblob['customer'] = maybe_customer_details

    yield customerblob
