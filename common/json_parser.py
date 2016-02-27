import json
import copy




formtable = {"name":[u'name'],
             "gender":[u'gender'],
             "contact":[u'contact'],
             "address":[u'address']}

def is_reserved_layer(dict,reserved_word):
    for key in dict:
        if len(reserved_word)<=len(key) and reserved_word == key[:len(reserved_word)]:
            return True
    return False

def json_reduce_layer(source,reserved_word):
    if type(source)==list:
        if is_reserved_layer(source[0],reserved_word):

            for i in range(len(source)):
                temp_dict = source.pop(0);

                for temp_key in temp_dict:

                    source.append(temp_dict[temp_key][0])


            json_reduce_layer(source,reserved_word)
        else:
            for item in source:
                json_reduce_layer(item,reserved_word)
    elif type(source)==dict:
        for key in source:
            #print source[key]
            json_reduce_layer(source[key],reserved_word)

'''
def json_reduce_layer(source, reserved_word):
    if type(source)==dict:
        for key in source:
            if(type(source[key])==list and len(source[key])==1):
                if(type(source[key][0])==dict and is_reserved_layer(source[key][0],reserved_word)):
                    temp_dict = source[key].pop()
                    for temp_key in temp_dict:
                        source[key].append(temp_dict[temp_key])
                    for item in source[key]:
                        json_reduce_layer(item, reserved_word)
    elif type(source)==list:
        for item in source:
            if(type(item)==dict):
                if is_reserved_layer(item,reserved_word):
                    #this item is a reserved_layer
                    temp_dict = source.pop(obj=list[0])
                    for key in temp_dict:
                        source.append(temp_dict[key])
        for item in source:
            json_reduce_layer(item, reserved_word)
'''


def json_reduce_structure(source):
    if type(source)==dict:
        for key in source:
            if(type(source[key])==list and len(source[key])==1):
                source[key] = source[key][0]
                json_reduce_structure(source[key])
    elif type(source)==list:
        for item in source:
            if(type(item)==dict):
                json_reduce_structure(item)

def json_write(source,list,reserved_word):
    if(len(source)==1):
        #if the source is the list item in the source list, append it to the dest list
        list.append(source[0])
    else:
        if(len(list)==0):
            #the list is empty, append a new dict to it
            dict = {}
            dict[source[0]] = []
            list.append(dict)
        else:
            #there already have a dict in the list: list[0]
            if not list[0].has_key(source[0]):
                #add key source[0] in the dict
                list[0][source[0]] = []
        json_write(source[1:],list[0][source[0]],reserved_word)

def list2json(source,reserved_word):
    '''
    :param source: a list of list
    :return: a dict which can be converted into json str use json.dumps()
    '''


    dest = json_gene(source,reserved_word)

    json_reduce_layer(dest,reserved_word)
    json_reduce_structure(dest)

    return dest

def json_gene(list,reserved_word):
    proto = {}
    for item in list:
        if not proto.has_key(item[0]):
            proto[item[0]] = []
        json_write(item[1:],proto[item[0]],reserved_word)
    return proto

def listequal(list1,list2):
    '''
    compare the elements in these two list
    :param list1:
    :param list2:
    :return: Ture if two list are equal
    '''
    if len(list1)!=len(list2):
        return False
    else:
        for i in range(len(list1)):
            if list1[i]!=list2[i]:
                return False
    return True

def extend(prefix, extendlist, raw):
    '''
    :param prefix: list of key, there maybe more than one item  corresponding to it
    :param extendlist:extended item will append to this list
    :param raw:patient's info comeform
    :return:
    '''
    for item in raw:
        if listequal(prefix, item[:len(prefix)]):
            extendlist.append(item)

def form2list(form,formtable,raw):
    extendlist = [];

    for item in form:
        extend(formtable[item],extendlist,raw)

    return extendlist

def retrieve(policy, raw):
    '''
    :param policy: a list to identify a item of patient's info, the policy[-1] is the attribute of the item
    :param raw: result of json2list()
    :return: return processed patient's info
    '''
    newlist = policy
    not_found_flag = True

    for item in raw:
        if listequal(policy[:-1],item[:-1]):
            not_found_flag = False
            newlist[-1] = 'Mask'
            return newlist, item[:-1]

    if not_found_flag:
        newlist[-1]= 'Not Found'
        return newlist, 0


def conver(item, templist, result,reserved_word):
    '''
    :param item: list or dict to be convert
    :param templist: a temp list
    :param result: every item in result is a convert result
    :return:
    '''
    if type(item)==dict:
        for key in item:
            templist.append(key)
            conver(item[key], templist, result,reserved_word)
            templist.pop()
    elif type(item) == list:
        for i in range(len(item)):
            tempkey = reserved_word+str(i)
            templist.append(tempkey)
            conver(item[i],templist,result,reserved_word)
            templist.pop()
        #for arg in item:
            #conver(arg, templist, result)
    elif type(item) == unicode:
        templist.append(item)
        resultitem = copy.deepcopy(templist)
        result.append(resultitem)
        #print item
        templist.pop()

def json2list(jsonfile,reserved_word):
    '''
    :param jsonfile: dict come from json.dumps
    :return:a list, every item in this list is a list [key1,key2,...,keyn,value],
            it show the position of value in original json file
    '''
    result = []
    templist = []
    conver(jsonfile,templist,result,reserved_word)
    return result


def simplejsontest():
    reserved_word = 'PRIVACY_POLICY_JSON_PARSOR_LAYER_MARK'

    s = json.loads(
        '''
{
    "resourceType": "Patient",
    "text": {
        "status": "generated",
        "div": "<div><p>Freda Penn</p ></div>"
    },
    "name": {
        "text": "Protected data due to privacy policy"
    },
    "gender": "female"
}
        '''
    )

    newlist = json2list(s,reserved_word)

    for item in newlist:
        print item

    thelist = [[u'Patient', 'PRIVACY_POLICY_JSON_PARSOR_LAYER_MARK0', 'PRIVACY_POLICY_JSON_PARSOR_LAYER_MARK0', u'name'], [u'Patient', 'PRIVACY_POLICY_JSON_PARSOR_LAYER_MARK0', 'PRIVACY_POLICY_JSON_PARSOR_LAYER_MARK2', u'text'], [u'Patient', 'PRIVACY_POLICY_JSON_PARSOR_LAYER_MARK0', 'PRIVACY_POLICY_JSON_PARSOR_LAYER_MARK3', u'Freda Penn'], [u'Patient', 'PRIVACY_POLICY_JSON_PARSOR_LAYER_MARK1', 'PRIVACY_POLICY_JSON_PARSOR_LAYER_MARK0', u'gender'], [u'Patient', 'PRIVACY_POLICY_JSON_PARSOR_LAYER_MARK1', 'PRIVACY_POLICY_JSON_PARSOR_LAYER_MARK1', u'female']]
    testlist = []
    testlist.append([u'name', 'parallel_dict0', u'use', u'official'])
    testlist.append([u'name', 'parallel_dict0', u'given', 'parallel_dict0', u'Peter'])
    testlist.append([u'name', 'parallel_dict0', u'given', 'parallel_dict1', u'James'])
    testlist.append([u'name', 'parallel_dict0', u'fhir_comments', 'parallel_dict0', u" Peter James Chalmers, but called 'Jim' "])
    testlist.append([u'name', 'parallel_dict0', u'family', 'parallel_dict0', u'Chalmers'])
    testlist.append([u'name', 'parallel_dict1', u'use', u'usual'])
    testlist.append([u'name', 'parallel_dict1', u'given', 'parallel_dict0', u'Jim'])




    result = list2json(newlist,reserved_word)

    print result


    print json.dumps(result,indent=4)












if __name__ == '__main__':
    #test()
    #jsontest()
    simplejsontest()