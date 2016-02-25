# This part is designed for parsing the resource_type
'''
    Simply, server will send back to either:
        redirect template
        one_single_type_resource
        bundle_type
        Error template
'''

BUNDLE_SIGNAL = {'type' : 'searchset',
                 'resourceType' : 'Bundle'
                 }

SINGLE_SIGNAL = {'type' : 'searchset',
                 'resourceType' : 'Bundle'
                }

def is_single_resource(resource):
    for key,value in BUNDLE_SIGNAL:
        if resource.has_key(key) and resource[key] != value:
            return True
    return False


def is_multi_resource(resource):
    for key,value in BUNDLE_SIGNAL:
        if resource.has_key(key) and resource[key] == value :
            return True
    return False