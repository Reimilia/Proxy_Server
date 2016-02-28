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


def is_single_resource(Dict_Resource):
    #print resource

    for key,value in BUNDLE_SIGNAL.iteritems():
        if key in Dict_Resource and Dict_Resource.get(key, 'Default') != value:
            return True
    return False


def is_multi_resource(Dict_Resource):
    for key,value in BUNDLE_SIGNAL.iteritems():
        if key in Dict_Resource and Dict_Resource.get(key, 'Default') == value:
            return True
    return False