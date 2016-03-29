from utils import api_call,RESERVED_WORD,STATUS_ERROR
from json_parser import json2list,list2json,listequal,json_reduce_structure
import json
from urllib import urlencode
from . import SERVER_BASE,PRIVACY_BASE
from resource import is_single_resource,is_multi_resource


def get_seq_id(dict_resource):
    if dict_resource['resourceType'] != 'Sequence':
        return 0
    try:
        return dict_resource
    except:
        return 0

def get_patient_ID(dict_resource, auth_header):
    #resource is a dict data
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
    '''if 'reference' in dict_resource:
        for ref in dict_resource['reference']:
            if ref.has_key('subject') and ref['subject'] == 'Patient':
		        patient_id = ref['text']
    elif 'id' in dict_resource and 'resourceType' in dict_resource and dict_resource['resourceType']=='Patient':
        patient_id = dict_resource['id']
    elif 'Identifier' in dict_resource and 'resourceType' in dict_resource and dict_resource['resourceType']=='Patient':
        patient_id = dict_resource['Identifer']
    else:
        if 'patient' in dict_resource:
            patient_id = dict_resource['patient']['reference'].split('/')[1]
        elif 'subject' in dict_resource:
            patient_id = dict_resource['subject']['reference'].split('/')[1]
        else:
            patient_id = get_seq_id(dict_resource)'''
    #print dict_resource
    if 'id' in dict_resource:
        patient_id = dict_resource['id']
    elif 'Identifier' in dict_resource:
        patient_id = dict_resource['Identifier']['value']
    elif 'variationID' in dict_resource:
        try:
            patient_id = dict_resource['variationID']['coding'][0]['code']
        except:
            patient_id = dict_resource['variationID']['coding']['code']
    else:
        patient_id = 'Nope'
    return patient_id


def get_policy_data(patient_id, auth_header):
    forwarded_args = {}
    forwarded_args['_format'] = 'json'
    api_endpoint = 'Privacy/%s?%s' % (patient_id, urlencode(forwarded_args, doseq=True))
    resp = api_call(PRIVACY_BASE,api_endpoint, auth_header)
    #print patient_id,resp._content
    try:
        return resp.json()['Resource']
    except:
        # Did not find Privacy Resource
        return 'Nope'

def retrieve(policy, raw):
    '''
    :param policy: a list to identify a item of patient's info, the policy[-1] is the attribute of the item
    :param raw: result of json2list()
    :return: return processed patient's info
    '''
    not_found_flag = True
    for item in raw:
        for x in range(2,len(item)):
            #print policy[:-(x+1)]
            #print policy[0:x]
            #print item[0:x]
            #print '\n'
            if listequal(policy[0:x],item[0:x]):
                not_found_flag = False
                #policy[-1] = 'Mask'
                return u'Mask',item[-1],x+1

    if not_found_flag:
        #policy[-1] = 'Not_Found'
        return u'Not_Found',0,0


def cover_protected_data(dict_list, resource, privacy_policy, status='all'):
    '''
    This is where we wrap up json data with privacy_policy
    :param dict_list: something the response contained
    :param resource: something we get from data_server
    :param privacy_policy: what we get from privacy_server
    :param status: hide_status
    :return: parsered json data of dict_list after filtering
    '''
    json_reduce_structure(privacy_policy)
    policy_data = json2list(privacy_policy,RESERVED_WORD)
    #json_reduce_structure(policy_data)

    json_reduce_structure(dict_list)
    data_list = json2list(dict_list, RESERVED_WORD)


    if isinstance(resource['resourceType'], unicode):
        s=resource['resourceType']
    else:
        s=unicode(resource['resourceType'],"utf-8")

    json_reduce_structure(resource)
    resource_data = json2list(resource,RESERVED_WORD)


    for i in range(len(resource_data)):
        resource_data[i].insert(0,s)

    data = data_list

    for i in range(len(data)):
        data[i].insert(0,s)
    #print resource
    #print data
    #print policy_data
    #If the query is only part of data,then do the intersection
    #for i in range(len(data)):
    #    if data[i][1] == 'text' or data[i][1] == 'resourceType':
    #        continue

    #    tmp = retrieve(data[i],resource_data)
    #    if tmp[0] == 'Not_Found':
    #        data[i][-1] = 'Not in the online record'
    #    else:
    #        data[i][-1] = tmp[1]
    #print data
    #print policy_data
    #print '\n'


    for i in range(len(data)):
        if data[i][1]=='text' or data[i][1]=='resourceType':
            continue
        tmp = retrieve(data[i],policy_data)
        #print tmp
        #print data[i]
        # Not found or unmasked means we should not change the value
        if tmp[0] == 'Mask':
            # Here we need to filter the policy
            keyword = data[i][-1]
            #print keyword
            #data[i][-1] = 'Protected data to %s User' % status
            for j in range(len(data)):
                # This deals with a wrapped_up data that might potentially display at other locations
                if data[j][-1].find(keyword) != -1 and data[j][-1].find('http') == -1:
                    data[j][-1]="Hide due to sensitive information (concerning with patient's policy)"
            #print data[i]
            data[i]= data[i][0:tmp[2]]
            #print data[i]
            #print '\n'
            data[i][-1]= 'Protected data to %s User' % status

    for i in range(len(data)):
        del data[i][0]
    new_data = []
    for dat in data:
        if dat not in new_data:
            new_data.append(dat)
    result =list2json(new_data,RESERVED_WORD)

    print result
    #if(result['id']=='ob-genetics-2'):
    #    print result
    return result


def filter_policy(resource, auth):
    '''
    Judge the type of response and deal with data_wrapper
    :param resource: the data send back to client
    :param auth_header: this helps to make a legal http request
    :return:
    '''
    wrapped_data = resource
    dict_resource = json.loads(resource)
    #print dict_resource
    # Judge type of bundled resource
    if is_single_resource(dict_resource):
        #Deal with a single resource
        patient_ID = get_patient_ID(dict_resource, auth)
        #print patient_ID
        privacy_data = get_policy_data(patient_ID, auth)
        #print privacy_data
        if type(privacy_data)==str and privacy_data=='Nope':
            pass
        else:
            resp = dict_resource
            for key, v in privacy_data.items():
                # to match up , we need to formalize the format of policy_data
                canonical_format = {v['Policy_ResourceType'] : v['Policy']}
                #print v
                print canonical_format
                stat = v['Scope']
                resp=cover_protected_data(resp, resp, canonical_format, status= stat)
            wrapped_data= json.dumps(resp)
    elif is_multi_resource(dict_resource):
        #Deal with bundled resource
        #print "here\n\n"
        #print len(dict_resource['entry'])
        for i in range(len(dict_resource['entry'])):
            #print i
            patient_ID = get_patient_ID(dict_resource['entry'][i]['resource'], auth)
            privacy_data = get_policy_data(patient_ID, auth)
            #print patient_ID,privacy_data
            #print "\n"
            if type(privacy_data)==str and privacy_data=='Nope':
                pass
            else:
                resp = dict_resource['entry'][i]['resource']
                #print type(privacy_data)
                for key, v in privacy_data.items():
                    # to match up , we need to formalize the format of policy_data
                    canonical_format = {v['Policy_ResourceType'] : v['Policy']}
                    stat = v['Scope']
                    resp=cover_protected_data(resp, resp, canonical_format, status= stat)
                    print resp
                dict_resource['entry'][i]['resource'] = resp
            #print dict_resource['entry'][i]['resource']
        wrapped_data= json.dumps(dict_resource)
    else:
        #In this case it is worthless to bundle it
        pass

    return wrapped_data

