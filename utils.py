import json
import numpy as np
def find_all_keys(data):
    key_set=set()
    def traversal(itemvalue,name):       
        if(type(itemvalue)==dict):
            for key in itemvalue.keys():
                traversal(itemvalue[key],name+":"+key)
        else:
            key_set.add(name)

    for i in data:
        parse_data=json.loads(i)
        for key in parse_data.keys():
            traversal(parse_data[key],key)
    
    return key_set

def find_all_value(results,le,value_list):
    y_final=[value_list]
    length=len(value_list)
    def traversal_y(itemvalue,name):       
        if(type(itemvalue)==dict):
            for key in itemvalue.keys():
                traversal_y(itemvalue[key],name+":"+key)
        else:
            if(name in value_list):
                index=le.transform([name])[0]
                append_item[index]=itemvalue

    for result in results:
        append_item=[np.nan]*length
        parse_data=json.loads(result)
        for key in parse_data.keys():
            traversal_y(parse_data[key],key)
        y_final.append(append_item)
    return y_final


def find_dimension_value(dimensions,le,value_list,key_name_dict):
    X_final=[value_list]
    length=len(value_list)

    def traversal_x(itemvalue,name):       
        if(type(itemvalue)==dict):
            for key in itemvalue.keys():
                traversal_x(itemvalue[key],name+":"+key)
        else:
            if(name in key_name_dict):
                name=key_name_dict[name]
            index=le.transform([name])[0]
            append_item[index]=itemvalue

    for dimension in dimensions:
        append_item=[np.nan]*length
        parse_data=json.loads(dimension)
        for key in parse_data.keys():
            traversal_x(parse_data[key],key)
        X_final.append(append_item)
    return X_final






# def test():
#     dimension_key=list(dimension_key_set)
#     for index in range(len(dimension_key)):
#         key=dimension_key[index]
#         if(key in result):
#             dimension_key[index]=result[key]
#     set(dimension_key)