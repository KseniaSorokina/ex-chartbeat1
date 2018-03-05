import requests
import json
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import sys
import keboola
from keboola import docker

cfg = docker.Config('/data/')
payload = cfg.get_parameters()


def requests_retry_session(
    retries=5,   # repeats 5 times
    backoff_factor=0.5,  # time between calls start with 5 seconds, time increases after next call 
    status_forcelist=(500, 502, 503, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# first API call

first_api_call = requests.get('http://api.chartbeat.com/query/v2/submit/page/?', params=payload)
status_code = first_api_call.status_code
if status_code != 200:
    print('Error, status code of first call: ' + str(status_code))

# generate query_id as a result of first API call
result_of_first_api_call = first_api_call.json()
query_id = str(result_of_first_api_call['query_id'])

# second API call, repeats every 5 min (300 vtr)
pa1= {'host': payload['host'], 'apikey': payload['#apikey'], 'query_id': query_id}

t0 = time.time()
try:
    second_api_call = requests_retry_session().get(
    'http://api.chartbeat.com/query/v2/fetch/?', params=pa1,  
    timeout=300
    )
except Exception as x:
    print('It failed 😞', x.__class__.__name__)
    sys.exit()
else:
    print('It eventually worked', second_api_call.status_code)
finally:
    t1 = time.time()
    print('Took', t1 - t0, 'seconds')

# if last retry failed - exit the program	
status_code = second_api_call.status_code
if status_code != 200:
	print('Error, second response failed. Status code: ' + str(status_code))
	sys.exit()

# result of second API call as text object 
result_of_second_api_call = second_api_call.text


# result of second API call as CSV 
file = open('/data/out/tables/ex_chartbeat.csv','w')  
file.write(result_of_second_api_call)
file.close()
