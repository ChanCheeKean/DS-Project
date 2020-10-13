from flask import request
import requests
import pandas as pd
import json
from datetime import datetime


def getToken_app_credential(tenant = 'omnetric'):
    '''
	Input: tenant name, either 'omnetric' or 'embm2dev'
	Output: token in json format
	'''
    url = 'https://gateway.eu1.mindsphere.io/api/technicaltokenmanager/v3/oauth/token'
    if tenant == 'omnetric':
        headers = {
        'content-type': 'application/json',
        'X-SPACE-AUTH-KEY': 'Basic <b21uZXRyaWMtZW5leGlzdHJhZm8tMS4wLjA6NUJyaUZzMU1keWNQWTdKQzNma01xeFNXUlFZRFF6a3RySHJ6YmRNSExhTA=>'
        }
        json = {
          "appName": "enexistrafo",
          "appVersion": "1.0.0",
          "hostTenant": "omnetric",
          "userTenant": "omnetric"
        }
        
    elif tenant == 'embm2dev':
        headers = {
            'content-type': 'application/json',
            'X-SPACE-AUTH-KEY': 'Basic <ZW1ibTJkZXYtYmFzZXRpbWVzZXJpZXNhcHAtMC4wLjE6QXZqZW9EbkhnTTNPMGRVRlBIVllLTWRsY2ZTNHlVRG9vZ09GZFM4dDMzOA=>'
        }
        json = {
          "appName": "basetimeseriesapp",
          "appVersion": "0.0.1",
          "hostTenant": "embm2dev",
          "userTenant": "embm2dev"
        }
        
    response = requests.post(url, headers=headers, json=json)
    token = response.json()   
    return token


def get_token2_service_credential():
    '''
    Description: Requesting for token using service Credential. Only Applicable for Omnetric Tenant.
	Output: token in json format
	'''

    url = 'https://omnetric.piam.eu1.mindsphere.io/oauth/token'
    #credentials = { 'client_id': 'EnergyIPApp', 'client_secret': 'eygYuu3RxTxfVQcqw6oNqDsczNv3LXjm',}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic RW5lcmd5SVBBcHA6ZXlnWXV1M1J4VHhmVlFjcXc2b05xRHNjek52M0xYam0=',
        }
    data = {
            'grant_type' :'client_credentials'
            }
    response = requests.post(url, headers=headers, data = data)
    token = response.json()  
    return token


def get_url(request_entity = 'assets', asset = None, aspect = None, start = None, end = None):
    '''
    Description: To get proper url routing for specific asset, aspect and queries
	Output: Specific Url
	'''
    
    if request_entity == 'assets':
        return 'https://gateway.eu1.mindsphere.io/api/assetmanagement/v3/assets?includeShared=true'
    elif request_entity == 'aspects':
        return f'https://gateway.eu1.mindsphere.io/api/assetmanagement/v3/assets/{asset}/aspects?includeShared=true'
    elif request_entity == 'variables':
        return f'https://gateway.eu1.mindsphere.io/api/iottimeseries/v3/timeseries/{asset}/{aspect}'
    else:
#        str_time = datetime.strptime(start, '%Y%m%d').strftime("%Y-%m-%dT%H:%M:%SZ")
#        end_time = datetime.strptime(end, '%Y%m%d').strftime("%Y-%m-%dT%H:%M:%SZ")  
        query = '?from={}&to={}'.format(start, end)
        return f'https://gateway.eu1.mindsphere.io/api/iottimeseries/v3/timeseries/{asset}/{aspect}?{query}'


def get_api_json(url, required = False, token = None):
    '''
    Description: To get api data in json format,
    Input: 
            url: specific routing for asset/aspect/variable
            required: boolean. Yes if requesting data locally
            token: Only applicable if required = True
	Output: data in json format
	'''
    if required:
        headers = {'Authorization': 'Bearer ' + token['access_token']}
    else:
        headers = {'Authorization': request.headers.get('Authorization')} 
        
    JSONContent = requests.get(url, headers = headers)
    data = JSONContent.json()
    return data


#tokenTime = currentToken = ''
#if (tokenTime == '') or (datetime.now() > tokenTime + timedelta(minutes = 25)):        
#    #check expiry
#    currentToken = getToken_app_credential(tenant = 'omnetric')
#    tokenTime = datetime.fromtimestamp(currentToken['expires_at'])
#    headers = {'Authorization': 'Bearer ' + currentToken['access_token']}
#else:
#    headers ={'Authorization': 'Bearer ' + currentToken['access_token']}

def read_files(assetId, resample_int = None):   
    '''
    Description: To process json file in DataFrame format
	Output: DataFrame Object.
	'''
    
    df = pd.read_csv(f'./data/{assetId}_MeasuredValueFields.csv')
    df.set_index('_time', inplace = True)
    df.index = pd.to_datetime(df.index)
    df = df.drop(columns = 'Value_qc')
    if resample_int != None:
        df = df.resample(resample_int).mean()
    else:
        pass
    return df