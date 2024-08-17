"""
根据机构消歧结果，构建机构之间的关联关系，即organization_linkage表。
由于同一机构在affiliation和manufacturer中的表达可能不同，我们采用相似度的方式，计算相同机构
表的字段包括：id, affilation_id, applicant_id, manufacrurer_id
"""

import pandas as pd
from fuzzywuzzy import fuzz

path_affiliation = r'C:\Users\yang\Desktop\drugbank数据集论文\drug_bank_数据处理\机构消歧\new_affiliation.xlsx'
path_applicant = r'C:\Users\yang\Desktop\drugbank数据集论文\drug_bank_数据处理\机构消歧\new_entity_technology.xlsx'
path_manufacture = r'C:\Users\yang\Desktop\drugbank数据集论文\drug_bank_数据处理\机构消歧\new_manufacturer.xlsx'

# 加载数据
df_affiliation = pd.read_excel(path_affiliation)
df_applicant = pd.read_excel(path_applicant)
df_manufacture = pd.read_excel(path_manufacture)
print(df_affiliation.head())
print(df_applicant.head())
print(df_manufacture.head())


# 相似度匹配函数
def get_similarity(source_name, target_name):
    similarity = fuzz.ratio(source_name, target_name)
    flag = 0
    if similarity >= 85:
        flag = 1
    return flag, similarity



# 构建新的数据表
organization_linkage = []
aff_enti_id = []  ## 存储论文机构与专利机构匹配成功的专利机构id,避免匹配结果重复
### 从论文机构开始匹配
a_e_m_num = 0
a_e_num = 0
a_m_num = 0
e_m_num = 0
for aindex in df_affiliation.index:
    affiliation_name = df_affiliation.loc[aindex,'name']
    for eindex in df_applicant.index:
        entity_name = df_applicant.loc[eindex,'name']
        flag_a_e, similarity_a_e = get_similarity(affiliation_name.lower(),entity_name.lower())
        if flag_a_e == 1:
            ## 找到了与论文机构匹配的专利机构，继续与论文机构相匹配的药物机构
            for mindex in df_manufacture.index:
                manufacture_name = df_manufacture.loc[mindex,'name']
                flag_a_m, similarity_a_m = get_similarity(affiliation_name.lower(), manufacture_name.lower())
                if flag_a_m == 1:
                    each_linkage = {}
                    each_linkage['affiliation_id'] = df_affiliation.loc[aindex,'id']
                    each_linkage['affiliation_name'] = affiliation_name
                    each_linkage['applicant_id'] = df_applicant.loc[eindex,'id']
                    each_linkage['applicant_name'] = entity_name
                    each_linkage['similarity_a_e'] = similarity_a_e
                    each_linkage['manufacture_id'] = df_manufacture.loc[mindex,'id']
                    each_linkage['manufacture_name'] = manufacture_name
                    each_linkage['similarity_a_m'] = similarity_a_m
                    aff_enti_id.append(df_applicant.loc[eindex,'id'])
                    a_e_m_num += 1
                    organization_linkage.append(each_linkage)
            if flag_a_m == 0:
                each_linkage = {}
                each_linkage['affiliation_id'] = df_affiliation.loc[aindex,'id']
                each_linkage['affiliation_name'] = affiliation_name
                each_linkage['applicant_id'] = df_applicant.loc[eindex,'id']
                each_linkage['applicant_name'] = entity_name
                each_linkage['similarity_a_e'] = similarity_a_e
                a_e_num += 1
                aff_enti_id.append(df_applicant.loc[eindex,'id'])
                organization_linkage.append(each_linkage)
    if flag_a_e == 0:
        for mindex in df_manufacture.index:
            manufacture_name = df_manufacture.loc[mindex,'name']
            flag_a_m, similarity_a_m = get_similarity(affiliation_name.lower(), manufacture_name.lower())
            if flag_a_m == 1:
                each_linkage = {}
                each_linkage['affiliation_id'] = df_affiliation.loc[aindex,'id']
                each_linkage['affiliation_name'] = affiliation_name
                each_linkage['manufacture_id'] = df_manufacture.loc[mindex,'id']
                each_linkage['manufacture_name'] = manufacture_name
                each_linkage['similarity_a_m'] = similarity_a_m
                a_m_num += 1
                organization_linkage.append(each_linkage)
            
### 从专利机构匹配
for eindex in df_applicant.index:
    entity_name = df_applicant.loc[eindex,'name']  
    ## 将未匹配成功的专利机构与药物机构进行匹配
    if df_applicant.loc[eindex,'id'] not in aff_enti_id:
        for mindex in df_manufacture.index:
            manufacture_name = df_manufacture.loc[mindex,'name']
            flag_e_m, similarity_e_m = get_similarity(entity_name.lower(), manufacture_name.lower())
            if flag_e_m == 1:
                each_linkage = {}
                each_linkage['applicant_id'] = df_applicant.loc[eindex,'id']
                each_linkage['applicant_name'] = entity_name
                each_linkage['manufacture_id'] = df_manufacture.loc[mindex,'id']
                each_linkage['manufacture_name'] = manufacture_name
                each_linkage['similarity_e_m'] = similarity_e_m
                e_m_num += 1
                organization_linkage.append(each_linkage)

df_organization_linkage = pd.DataFrame(organization_linkage)
df_organization_linkage['id'] = range(1, len(df_organization_linkage) + 1)

df_organization_linkage.to_excel(r"organization_linkage_85.xlsx")



