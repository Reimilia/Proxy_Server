#Author:  Panzer_wy
#Last updated: 2016/02/09


from flask import request
from urllib import urlencode
import re
import requests

STATUS_OK = "OK"
STATUS_ERROR = "ERROR"
STATUS_UNKNOWN = "UNKNOWN"
STATUS_UNRELATED = "UNRELATED"
RESERVED_WORD = 'PRIVACY_POLICY_JSON_PARSOR_LAYER_MARK'


def Catch_dataError():
    with open('../error.txt', 'wt') as f:
        f.write("Data Error!")
        f.close()

def api_call(base,api_endpoint,auth):
    '''
    API_call auxillary function
    :param base: base_url
    :param api_endpoint: redirect_path and parsed args
    :param auth: http header
    :return: Response
    '''
    return requests.get('%s/%s'% (base, api_endpoint), headers=auth)


def get_resource_identifier(url,bundle):
    # get unique identifier from url
    # Transferred data might not have key identifier, although this is quite strange
    if 'Identifier' in bundle:
        return bundle['Identifier']['value']
    else:
        pattern = re.compile(r'(?<=\/)[0-9A-Za-z-]*(?=\?)')
        identifier = pattern.search(url+'?').group()
        # TO-DO: Here pattern.search(url+'?') might get a value of None
        # then there will be a problem for none has no attribute 'group
        return identifier


'''
    Note: The official way to resolve this problem is to use
    search parameters: _include & _revinclude
    TO DO: Finish and apply this method to avoid redundant query
'''
def get_resource_refpatientID(resource):
    #resource is a json data
    '''
    This program intends to get resource's
        subject reference of Patient.
    It may involve serveral Patient or has no conncection with a patient.
    So this function return a list of value of patient_id
    '''
    '''
    Usage of _revinclude
    identifer = resource['Identifer']['value']
    forward_args = request.args.to_dict(flat=False)
    forward_args['_format'] = 'json'
    forwarded_url = resource['resourceType']+ '/'+ identifer
    api_url = '/%s?%s'% (forwarded_url, '_revinclude')
    api_resp = extend_api.api_call(api_url)

    if api_resp.status_code != '403':
        response=api_resp.json()
    else:
        return "Http_403_error"
    '''
    # In this demo, however, we simplify this process by assuming certain scenario
    if resource.has_key('reference'):
        for ref in resource['reference']:
            if ref.has_key('subject') and ref['subject']=='Patient':
		        patient_id = ref['text']
    elif resource.has_key('patient'):
        ref=resource['patient']['reference']
        patient_id = ref.split('/')[-1]
    else:
        patient_id = STATUS_ERROR

    return patient_id


def search_request_patient(patient_id):
    # locate specific patient on remote server
    forward_args = request.args.to_dict(flat=False)
    forward_args['_format'] = 'json'
    forwarded_url = 'Patient/' + patient_id
    api_url = '/%s?%s'% (forwarded_url, urlencode(forward_args, doseq=True))
    api_resp = api_call(api_url)
    if api_resp.status_code != '403':
        return api_resp.json()
    else:
        raise Catch_dataError()

