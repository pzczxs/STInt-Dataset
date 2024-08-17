"""
Step 1：计算机构对的相似度
step 1.1: 计算专利机构对的相似度
step 1.2：计算作者机构对的相似度
step 1.3：计算药物制造商对的相似度
"""

import mysql.connector
import pandas as pd
from fuzzywuzzy import fuzz
from itertools import combinations

#建立与MysQL数据库的连接
cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='your PW',
    database='STInt'
)

"""
Step 1.1：计算专利机构对的相似度
step 1.1.1: 计算导出专利机构的数据
step 1.1.2：计算专利机构对的相似度
"""

"""
step 1.1.1: 计算导出专利机构的数据
"""
#执行sQL查询
all_applicant_query = "select * from inventor_applicant;"
all_applicant = pd .read_sql(all_applicant_query,cnx)
all_applicant.to_excel("all_applicant.xlsx")

inventor_applicant_query = "select * from inventor_applicant where first_name is null;"
inventor_applicant = pd .read_sql(inventor_applicant_query,cnx)

"""
step 1.1.2：计算专利机构对的相似度
"""
## 将机构转换为小写
for index in inventor_applicant.index:
    inventor_applicant.loc[index,'name'] = inventor_applicant.loc[index,'name'].lower()
inventor_applicant[['id','name']].head()

# 设置相似度阈值
similarity_threshold = 90

# 包括机构对应的id在内部保存相似度较大的机构名称对
applicant_potential_duplicates = []
# 重新计算前10个数据的相似度，并包括id信息
for (id1, name1), (id2, name2) in combinations(
        inventor_applicant[['id', 'name']].iterrows(), 2):
    similarity = fuzz.token_sort_ratio(name1['name'], name2['name'])
    if similarity > similarity_threshold:
        applicant_potential_duplicates.append(
            (name1['id'], name1['name'], name2['id'], name2['name'],
             similarity))

# 转换为DataFrame以便更好地展示
df_applicant_potential_duplicates = pd.DataFrame(
    applicant_potential_duplicates,
    columns=['ID 1', 'Name 1', 'ID 2', 'Name 2', 'Similarity'])

df_applicant_potential_duplicates.to_excel(r"applicant_消歧_90_1.xlsx")


"""
Step 1.2：计算作者机构对的相似度
step 1.2.1: 计算导出作者机构的数据
step 1.2.2：计算作者机构对的相似度
"""

"""
step 1.2.1: 计算导出作者机构的数据
"""
#执行sQL查询
affiliation_query = "select * from affiliation;"
affiliation = pd .read_sql(affiliation_query,cnx)
affiliation.to_excel(r"all_affiliation.xlsx")

"""
step 1.2.2：计算作者机构对的相似度
"""
# 设置相似度阈值
similarity_threshold = 90

# 包括机构对应的id在内部保存相似度较大的机构名称对
affiliation_potential_duplicates = []

# 计算相似度，并包括id信息
for (id1, name1), (id2, name2) in combinations(affiliation[['id', 'name']].iterrows(), 2):
    similarity = fuzz.token_sort_ratio(name1['name'], name2['name'])
    if similarity > similarity_threshold:
        affiliation_potential_duplicates.append((name1['id'], name1['name'], name2['id'], name2['name'], similarity))

# 转换为DataFrame以便更好地展示
df_affiliation_potential_duplicates = pd.DataFrame(affiliation_potential_duplicates, columns=['ID 1', 'Name 1', 'ID 2', 'Name 2', 'Similarity'])

df_affiliation_potential_duplicates.to_excel(r"affiliation_消歧_90.xlsx")


"""
Step 1.3：计算药物制造商对的相似度
step 1.3.1: 计算导出药物制造商的数据
step 1.3.2：计算药物制造商对的相似度
"""

"""
step 1.3.1: 计算导出药物制造商的数据
"""
#执行sQL查询
manufacturer_query = "select * from manufacturer;"
manufacturer = pd .read_sql(manufacturer_query,cnx)
manufacturer.to_excel(r"all_manufacturer.xlsx")


"""
step 1.3.2：计算药物制造商对的相似度
"""
# 设置相似度阈值
similarity_threshold = 90

# 包括机构对应的id在内部保存相似度较大的机构名称对
manufacturer_potential_duplicates = []

# 重新计算前10个数据的相似度，并包括id信息
for (id1, name1), (id2, name2) in combinations(manufacturer[['id', 'name']].iterrows(), 2):
    similarity = fuzz.token_sort_ratio(name1['name'], name2['name'])
    if similarity > similarity_threshold:
        manufacturer_potential_duplicates.append(
            (name1['id'], name1['name'], name2['id'], name2['name'],
             similarity))

# 转换为DataFrame以便更好地展示
df_manufacturer_potential_duplicates = pd.DataFrame(
    manufacturer_potential_duplicates,
    columns=['ID 1', 'Name 1', 'ID 2', 'Name 2', 'Similarity'])

df_manufacturer_potential_duplicates.to_excel(r"manufacturer_消歧_90.xlsx")
















