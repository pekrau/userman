"Test user access and authentication."

import pprint
import json
import urllib
import requests

from userman import settings

email = urllib.quote('per.kraulis@gmail.com')

url = settings['BASE_URL'] + 'api/v1/user/' + email
print url
data = dict(service='Charon')
headers = {'X-Userman-API-key': settings['API_KEYS'][0]}
response = requests.post(url, data=json.dumps(data), headers=headers)
print response.status_code
if response.status_code == requests.codes.ok:
    pprint.pprint(response.json())
else:
    print response.reason

url = settings['BASE_URL'] + 'api/v1/auth/' + email
print url
data = dict(password='abc123',
            service='Charon')
headers = {'X-Userman-API-key': settings['API_KEYS'][0]}
response = requests.post(url, data=json.dumps(data), headers=headers)
print response.status_code
if response.status_code == requests.codes.ok:
    pprint.pprint(response.json())
else:
    print response.reason
