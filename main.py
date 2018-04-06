import requests
import json
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import keboola
from keboola import docker
import datetime

cfg = docker.Config('/data/')
configuration = cfg.get_parameters()
name = configuration['table_name']
outFullName = '/data/out/tables/' + name + '.csv'
outDestination = 'ex_chartbeat'


start = int(configuration['start'])
today = datetime.datetime.now()
DD_start = datetime.timedelta(days=start)
earlier_start = today + DD_start
earlier_str_start = earlier_start.strftime("%Y-%m-%d")


end = int(configuration['end'])
DD_end = datetime.timedelta(days=end)
earlier_end = today + DD_end
earlier_str_end = earlier_end.strftime("%Y-%m-%d")

payload = {
    'host': configuration['host'],
    'apikey': configuration['#apikey'],
    'user_id': configuration['user_id'],
    'limit': configuration['limit'],
    'start': earlier_str_start,
    'end': earlier_str_end,
    'metrics': configuration['metrics'],
    'subdomain': configuration['subdomain'],
    'dimensions': configuration['dimensions'],
    'tz': configuration['tz'],
    'sort_column': configuration['sort_column'],
    'sort_order': configuration['sort_order'],
    'primary_key': configuration['primary_key']
}

'''
from datetime import datetime, timedelta
start = payload['start']

date_N_days_ago = datetime.now() - timedelta(days=start)
'''

pk = payload['primary_key']
cfg.write_table_manifest(outFullName, destination=outDestination, primary_key=pk, incremental=True)

def requests_retry_session(
    retries=100,   # repeats times
    backoff_factor=0.1,  # time between calls, increases after next call 
    status_forcelist=(400, 402, 403, 404, 405, 500, 502, 503, 504, 598),
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
# read in/state.json and try to get query_id
#if query id is empty then continue
# else skip to second api call
# first API call, repeates every 180 sec
t0 = time.time()
try:
    first_api_call = requests_retry_session().get(
    'http://api.chartbeat.com/query/v2/submit/page/?', params=payload,
    timeout=180
    )
    print(first_api_call )
except Exception as x:
    print('It failed 😞 (first_api_call)', x.__class__.__name__)
else:
    print('It eventually worked (first_api_call)', first_api_call .status_code)
finally:
    t1 = time.time()
    print('Took', t1 - t0, 'seconds')

# if last retry failed - exit the program	
if not first_api_call :
    print('all retries failed (first_api_call). Exiting the program')
    exit(2)

status_code = first_api_call.status_code
print(status_code)

# generate query_id as a result of first API call
result_of_first_api_call = first_api_call.json()
query_id = str(result_of_first_api_call['query_id'])
print("query_id: ",  query_id)

# else part starts here
# second API call, repeats every 180 sec
pa1= {'host': payload['host'], 'apikey': payload['apikey'], 'query_id': query_id}

t0 = time.time()
try:
    second_api_call = requests_retry_session().get(
    'http://api.chartbeat.com/query/v2/fetch/?', params=pa1,  
    timeout=180
    )
    print(second_api_call)
    
except Exception as x:
    print('It failed 😞 (second_api_call)', x.__class__.__name__)
else:
    print('It eventually worked (second_api_call)', second_api_call.status_code)
finally:
    t1 = time.time()
    print('Took', t1 - t0, 'seconds')

# if last retry failed - exit the program	
if not second_api_call:
    print('all retries failed (second_api_call). Exiting the program')
    exit(2)

status_code = second_api_call.status_code
print(status_code)

# result of second API call as text object 
result_of_second_api_call = second_api_call.text


# result of second API call as CSV 
#save query_id to data/out/state.json {'query_id': query_id}
file = open(outFullName,'w')  
file.write(result_of_second_api_call)
file.close()