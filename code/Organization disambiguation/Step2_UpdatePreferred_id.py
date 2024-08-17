"""
根据人工对相似度计算结果的核查结果，更新机构表的preferred_id。
Step 2:更新机构表的preferred_id
step 2.1 定于预处理函数：找出相似机构对的最小id；更新preferred_id的函数
step 2.2 更新affiliation表的preferred_id
step 2.3 更新invent_applicant表的preferred_id
step 2.4 更新manufacturer表的preferred_id
"""

import mysql.connector
import pandas as pd
from fuzzywuzzy import fuzz
from itertools import combinations

"""
step 2.1 定于预处理函数：找出相似机构对的最小id；更新preferred_id的函数
"""

"""
将是同一家机构的id合并,并找出相同机构中最小的id
"""
def merge_id(disambiguation_institution):
    # 合并id和name
    similarty_disambiguation_institution = []
    all_id = []
    for index in disambiguation_institution.index:
        ### 如果id已出现在之前的id列表中（该对机构已经出现过了）
        id1 = disambiguation_institution.loc[index,'ID 1']
        id2 = disambiguation_institution.loc[index,'ID 2']
        if id1 in all_id:
            for manuf in similarty_disambiguation_institution:
                if id1 in manuf['id']:
                    if id2 not in manuf['id']:
                        manuf['id'].append(id2)
                        all_id.append(id2)
        ### id没出现在之前的id列表中（该对机构还没出现过）
        else:
            each_disambiguation_institution = {}
            id_list = []
            each_disambiguation_institution['name'] = disambiguation_institution.loc[index,'Name 1']
            id_list.append(id1)
            id_list.append(id2)
            for id_1 in id_list:
                all_id.append(id_1)
            each_disambiguation_institution['id'] = id_list
            similarty_disambiguation_institution.append(each_disambiguation_institution)
    return similarty_disambiguation_institution

"""
根据原机构数据和消歧后的数据，更新preferred_id
"""
def update_institution_preferred_id(all_institution,similarty_institution):
    drop_id = []  ## 存储需要跳过处理的id
    for institution in similarty_institution:
        id_list = institution['id']
        for id in id_list:
            if id != institution['min_id']:
                for index in all_institution.index:
                    if all_institution.loc[index,'id'] == id:
                        all_institution.loc[index,'preferred_id'] == institution['min_id']
    return all_institution


"""
step 2.2 更新affiliation表的preferred_id
"""
article_affiliation = pd.read_excel(r"affiliation_消歧_90_已处理.xlsx")
article_affiliation = article_affiliation[article_affiliation['是否相同'] == 'Y']

all_affiliation = pd.read_excel(r"all_affiliation.xlsx")
all_affiliation.head()

similarty_affiliation = merge_id(article_affiliation)
new_affiliation = update_institution_preferred_id(all_affiliation,similarty_affiliation)
new_affiliation.to_excel(r"new_affiliation.xlsx")


"""
step 2.3 更新invent_applicant表的preferred_id
"""
applicant = pd.read_excel(r"applicant_消歧_90_已处理.xlsx")
applicant = applicant[applicant['是否相同'] == 'Y']

all_applicant = pd.read_excel(r"all_applicant.xlsx")

similarty_applicant = merge_id(applicant)
new_applicant = update_institution_preferred_id(all_applicant, similarty_applicant)
new_applicant.to_excel(r"new_applicant.xlsx")


"""
step 2.4 更新manufacturer表的preferred_id
"""
drug_manufacturer = pd.read_excel(r"manufacturer_消歧_90_已处理.xlsx")
# 选出是相同机构的机构对
drug_manufacturer = drug_manufacturer[drug_manufacturer['是否相同'] == "Y"]

all_manufacturer = pd.read_excel(r"all_manufacturer.xlsx")

similarty_manufacturer = merge_id(drug_manufacturer)
new_manufacturer = update_institution_preferred_id(all_manufacturer,similarty_manufacturer)
new_manufacturer.to_excel(r"new_manufacturer.xlsx")