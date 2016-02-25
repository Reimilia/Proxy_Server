from utils import api_call,RESERVED_WORD,STATUS_ERROR
from json_parser import json2list,list2json,listequal
import json
from urllib import urlencode
from . import  SERVER_BASE,PRIVACY_BASE
from resource import is_single_resource,is_multi_resource

def get_patient_ID(resource, auth_header):
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
        patient_id = ref.split('/')[1]
    else:
        patient_id = STATUS_ERROR

    return patient_id


def get_policy_data(patient_id, auth_header):
    forwarded_args = {}
    forwarded_args['_format'] = 'json'
    api_endpoint = 'Privacy/%s?%s' % (patient_id, urlencode(forwarded_args, doseq=True))
    resp = api_call(PRIVACY_BASE,api_endpoint, auth_header)
    return resp.json()

def retrieve(policy, raw):
    '''

    :param policy: a list to identify a item of patient's info, the policy[-1] is the attribute of the item
    :param raw: result of json2list()
    :return: return processed patient's info
    '''
    not_found_flag = True
    for item in raw:
        if listequal(policy[:-1],item[:-1]):
            not_found_flag = False
            #policy[-1] = 'Mask'
            return u'Mask',item[-1]

    if not_found_flag:
        #policy[-1] = 'Not_Found'
        return u'Not_Found',0

def cover_protected_data(data_list, resource, privacy_policy, status='full'):
    '''

    :param data_list: what part we want to display, json data
    :param resource: what we get in the proxy forwarding process, json data
    :param patient_ID: Identifer of specific patient
    :param status: Leave to extension
    :return:
    '''

    policy_data = json2list(privacy_policy,RESERVED_WORD)

    if type(data_list) is dict:
        data_list = json2list(data_list, RESERVED_WORD)

    if isinstance(resource['resourceType'], unicode):
        s=resource['resourceType']
    else:
        s=unicode(resource['resourceType'],"utf-8")
    resource_data = json2list(resource,RESERVED_WORD)
    #print json.dumps(resource, indent=4)
    for i in range(len(resource_data)):
        resource_data[i].insert(0,s)

    data = data_list

    for i in range(len(data)):
        data[i].insert(0,s)

    for item in data:
        print item

    #If the query is only part of data,then do the intersection
    for i in range(len(data)):
        if data[i][1] == 'text' or data[i][1] == 'resourceType':
            continue

        tmp = retrieve(data[i],resource_data)
        if tmp[0] == 'Not_Found':
            data[i][-1] = 'Not in the online record'
        else:
            data[i][-1] = tmp[1]

    for i in range(len(data)):
        if data[i][1]=='text' or data[i][1]=='resourceType':
            continue
        tmp =retrieve(data[i],policy_data)
        # Not found or unmasked means we should not change the value
        if tmp[0] == 'Mask':
            #Here we need to filter the policy
            data[i][-1] = 'Protected data due to privacy policy'

    for i in range(len(data)):
        del data[i][0]

    return list2json(data,RESERVED_WORD)

def filter_policy(resource, auth):
    '''
    :param resource: the data send back to client
    :param auth_header: this helps to make a legal http requesr
    :return:
    '''
    wrapped_data = resource
    if is_single_resource(resource):
        #Deal with a single resource
        patient_ID = get_patient_ID(resource, auth)
        privacy_data = get_policy_data(resource, auth)
        wrapped_data=cover_protected_data(resource, resource, privacy_data)
    elif is_multi_resource(resource):
        pass
    else:
        #In this case it is worthless to bundle it
        pass

    return wrapped_data