import requests
#from requests.packages.urllib3.exceptions import InsecureRequestWarning
#requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#from requests.exceptions import ConnectionError
def lambda_handler(event, context):
    print event
    
    api = event["api"]
    print api

    session = requests.Session()

    response = session.get(api, verify=False, timeout=10)
    statuscode = response.status_code
    print statuscode

    if statuscode == 200:
        health_status = "Healthy"
    else:
        health_status = "Unhealthy"

    return {
        "API": api,
        "Status Code": statuscode,
        "Health Status": health_status
    }

