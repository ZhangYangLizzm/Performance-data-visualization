import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# 读取key_test_t文件
def read_key_test_t(filepath):
    key_test_t=pd.read_csv(filepath,on_bad_lines='skip',engine='python').iloc[:,1:]
    key_test_t=key_test_t[["id","results_key","results","scenes_id","dimension","report_id","modified"]]
    return key_test_t

# 寻找所有key值
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

def find_results_value(results,le,value_list):
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

#返回特定工具名称项
def find_specify_tool(key_test_t,specify_tool_name):
    index=[]
    for i in range(len(key_test_t)):
        dimension=key_test_t["dimension"][i]
        try:
            parse_dimension=json.loads(dimension)
            if(parse_dimension["tool_name"]==specify_tool_name):            
                index.append(i)
        except:
            continue
    return key_test_t.iloc[index,:].drop_duplicates(subset=["report_id","dimension","results_key"]).reset_index(drop=True)

# 直接从toolname中返回并去重
def find_by_toolname_and_dropduplicates(key_test_t,specify_tool_name):
    index=[]
    for i in range(len(key_test_t)):
        dimension=key_test_t["dimension"][i]
        try:
            parse_dimension=json.loads(dimension)
            if(parse_dimension["tool_name"]==specify_tool_name):            
                index.append(i)
        except:
            continue
    # report_id、dimension、results_key相同时为重复数据，保留最后一项即可
    return key_test_t.iloc[index,:].drop_duplicates(subset=["report_id","dimension","results_key"],keep='last').reset_index(drop=True)
# 从testname中返回并去重
def find_by_testname_and_dropduplicates(key_test_t,specify_test_name):
    index=[]
    for i in range(len(key_test_t)):
        dimension=key_test_t["dimension"][i]
        # 使用try-catch防止解析过程遇到异常值发生错误，避免异常值
        try:
            parse_dimension=json.loads(dimension)
            if(parse_dimension["test_name"]==specify_test_name):            
                index.append(i)
        except:
            continue
    # report_id、dimension、results_key相同时为重复数据，保留最后一项即可
    return key_test_t.iloc[index,:].drop_duplicates(subset=["report_id","dimension","results_key"],keep='last').reset_index(drop=True)


#返回因变量y
def get_yfinal(df):
    results_keyset=find_all_keys(df["results"])
    results_list=sorted(list(results_keyset))
    le=LabelEncoder()
    results_le=le.fit(results_list)
    yfinal=find_results_value(df["results"],results_le,results_list)
    yfinal_df=pd.DataFrame(data=yfinal[1:],columns=yfinal[0])
    return yfinal_df
    
#返回自变量X
def get_Xfinal_df(filepath,df_dimension,df_results_key):
    key_name=pd.read_csv(filepath,names=["type","name"])
    key_name.dropna(inplace=True)
    key_name.reset_index(drop=True,inplace=True)
    key_name_dict={}
    for i in range(len(key_name)):
        key_name_dict[key_name["name"][i][1:-1]]=key_name["type"][i][1:-1]

    dimension_keyset=find_all_keys(df_dimension)
    dimension_list=list(dimension_keyset)
    for index in range(len(dimension_keyset)):
        key=dimension_list[index]
        if(key in key_name_dict):
            dimension_list[index]=key_name_dict[key]
    # 去重并重新排序
    dimension_list=sorted(list(set(dimension_list)))
    # 编码
    le=LabelEncoder()
    dimension_le=le.fit(dimension_list)
    dimension_value=find_dimension_value(df_dimension,dimension_le,dimension_list,key_name_dict)
    dimension_df=pd.DataFrame(data=dimension_value[1:],columns=dimension_value[0])
    #列替换
    dimension_df["host_cpu_isolation:host:dpdk"].fillna(dimension_df["host_cpu_isolation:host:name_8"],inplace=True)
    dimension_df["host_cpu_isolation:dpdk"].fillna(dimension_df["host_cpu_isolation:name_8"],inplace=True)
    dimension_df.drop(["host_cpu_isolation:name_8","host_cpu_isolation:host:name_8"],inplace=True,axis=1)
   
    results_key=df_results_key
    results_key.reset_index(drop=True,inplace=True)
    X_final=pd.concat([dimension_df,results_key],axis=1)
    return X_final
