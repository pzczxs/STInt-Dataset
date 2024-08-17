"""
Step 1:药物实体识别
Step 1.1：读取药物及其同义词数据
Step 1.2：读取article的标题和摘要
Step 1.3：读取patent的标题和摘要
Step 1.4：article数据的药物实体匹配
Step 1.5：patent数据的药物实体匹配
"""

import pymysql
import pandas as ps
import re

# 连接mysql
conn = pymysql.connect(host="127.0.0.1",
                       port=3306,
                       user='root',
                       passwd='your passwd',
                       charset='utf8')
cursor = conn.cursor()
# 进入数据库
cursor.execute('use STInt')


"""
Step 1.1：读取药物及其同义词数据
"""
select_drug_synonym = """
SELECT d_d_s.id as drug_id, d_d_s.name as drug_name, synonym.id as synonym_id, synonym.name as synonym_name 
from (select drug.id, drug.name, drug_synonym.synonym_id 
from drug join drug_synonym where drug.id = drug_synonym.drug_id) as d_d_s join synonym 
where d_d_s.synonym_id = synonym.id
"""
cursor.execute(select_drug_synonym)
drug_synonym_data = cursor.fetchall()  # 数据类型为tuple（元组）
print(len(drug_synonym_data))
print(drug_synonym_data[0])


## 先遍历一遍查询数据，把drug_name先加入drug_list中去
drug_list = []
drug_dict = {}
drug_id = drug_synonym_data[0][0]
drug_dict["drug_id"] = drug_id
drug_name = []
drug_name.append(drug_synonym_data[0][1])
drug_dict["drug_name"] = drug_name
drug_list.append(drug_dict)
for drug in drug_synonym_data:
    if drug[0] != drug_id:
        drug_id = drug[0]
        drug_dict = {}
        drug_name = []
        drug_name.append(drug[1])
        drug_dict["drug_id"] = drug_id
        drug_dict["drug_name"] = drug_name
        drug_list.append(drug_dict)

# 再次遍历查询数据，把synonym的药物名称加入drug_list(保持id相同)
for drug in drug_list:
    drug_id = drug["drug_id"]
    for d_cited_s in drug_synonym_data:
        if d_cited_s[0] == drug_id:
            if d_cited_s[3] not in drug["drug_name"]:
                drug["drug_name"].append(d_cited_s[3])
df_drug = pd.DataFrame(drug_list)

print(df_drug.head())

"""
根据名称长度对药物进行降序排序, 
在后续识别中，先匹配名称较长的药物
"""
for i in range(len(df_drug)):
    drug_name_list = []
    drug_name_long = []
    drug_name = df_drug.loc[i, "drug_name"]
    # 计算每个药物名称的长度
    for drug in drug_name:
        drug = drug.lstrip().rstrip()  # 去除左右空格
        drug_name_long.append(len(drug))
    # 将长度列表进行降序排序
    drug_name_long = sorted(drug_name_long, reverse=True)
    # 按照长度列表从小到大进行索引
    for j in range(len(drug_name)):
        for drug in drug_name:
            drug = drug.lstrip().rstrip()  # 去除左右空格
            if len(drug) == drug_name_long[j] and drug not in drug_name_list:
                drug_name_list.append(drug)
                break
    df_drug.loc[i, "drug_name"] = str(drug_name_list)
print(df_drug.head())

"""
Step 1.2：读取article的标题和摘要
"""
select_sql = "SELECT id,title,abst from article;"
cursor.execute(select_sql)
article_data = cursor.fetchall()  # 数据类型为tuple（元组）

## 将标题和摘要数据合并
article_list = []
for article in article_data:
    article_infor = {}
    title_abst = []
    t_null_flag = 0
    a_null_flag = 0
    if (pd.isna(article[1])) == False and (pd.isna(article[2])) == False:  # 都不为空
        title_abst.append(article[1])
        title_abst.append(article[2])
    elif (pd.isna(article[1])) == False and (pd.isna(article[2])) == True:  # 标题不为空，摘要为空
        title_abst.append(article[1])
    elif (pd.isna(article[1])) == True and (pd.isna(article[2])) == False: # 标题为空，摘要不为空
        title_abst.append(article[2])
    else:  # 都为空
        title_abst.append(" ")
    article_infor["id"] = article[0]
    article_infor["text"] = " ".join(title_abst)
    article_list.append(article_infor)

df_article = pd.DataFrame(article_list)
df_article.head()


"""
Step 1.3: 读取patent的标题和摘要
"""
select_patent_sql = "SELECT id,title,abst from patent"
cursor.execute(select_patent_sql)
patent_data = cursor.fetchall()  # 数据类型为tuple（元组）

## 将标题和摘要数据合并
patent_list = []
for patent in patent_data:
    patent_infor = {}
    p_title_abst = []
    if (pd.isna(patent[1])) == False and (pd.isna(patent[2])) == False:
        p_title_abst.append(patent[1])
        p_title_abst.append(patent[2])
    elif (pd.isna(patent[1])) == False and (pd.isna(patent[2])) == True:
        p_title_abst.append(patent[1])
    elif (pd.isna(patent[1])) == True and (pd.isna(patent[2])) == False:
        p_title_abst.append(patent[2])
    else:
        p_title_abst.append(" ")
    patent_infor["id"] = patent[0]
    patent_infor["text"] = " ".join(p_title_abst)
    patent_list.append(patent_infor)

df_patent = pd.DataFrame(patent_list)
df_patent.head()


"""
Step 1.4: article数据的药物实体匹配

建立引用表article_cited_drug：id, drug_id, article_id, drug_word
"""
article_cited_drug = []
id = 0
for d_index in df_drug.index:
    """
    检索每一个drug在每一篇论文中是否被引用
    记录引用次数，如果引用次数大于0，则将其记录下来
    一个drug可能被多个article引用
    """ 
    for a_index in df_article.index:
        a_cited_d = {}
        cited_num = 0
        # ast.literal_eval()hanshu jiang 
        for drug_name in df_drug.loc[d_index, "drug_name"]:
            try:
                if len(drug_name) <= 4:  # 名称长度小于等于4的，不用去除大小写匹配
                    pattern = fr'\b{drug_name}\b'
                    if re.search(pattern, df_article.loc[a_index,"text"]):
                        cited_num += 1
                        a_cited_d["drug_word"] = drug_name
                        break
                else:  # 长度大于4的，需要进行去除大小写匹配
                    pattern = fr'\b{drug_name.lower()}\b'
                    if re.search(pattern, df_article.loc[a_index,"text"].lower()):
                        cited_num += 1
                        a_cited_d["drug_word"] = drug_name
                        break
            except:
                if drug_name in df_article.loc[a_index,"text"]:
                    cited_num += 1
                    a_cited_d["drug_word"] = drug_name
                    break
        # 判断cited_num是否大于0
        if cited_num > 0:
            id += 1
            a_cited_d["id"] = id
            a_cited_d["drug_id"] = df_drug.loc[d_index, "drug_id"]
            a_cited_d["article_id"] = df_article.loc[a_index,"id"]
            article_cited_drug.append(a_cited_d)


df_match_article = pd.DataFrame(article_cited_drug)
df_match_article.to_excel(r"match_article_cited_drug.xlsx")

"""
Step 1.5: patent数据的药物实体匹配

建立引用表patent_cited_drug：id, drug_id, patent_id, drug_word
"""
patent_cited_drug = []
id = 0
for d_index in df_drug.index:
    """
    检索每一个drug在每一篇论文中是否被引用
    记录引用次数，如果引用次数大于0，则将其记录下来
    一个drug可能被多个patent引用
    """
    for p_index in df_patent.index:
        p_cited_d = {}
        cited_num = 0
        # ast.literal_eval()hanshu jiang 
        for drug_name in ast.literal_eval(df_drug.loc[d_index, "drug_name"]):
            try:
                if len(drug_name) <= 4:  # 名称长度小于等于4的，不用去除大小写匹配
                    pattern = fr'\b{drug_name}\b'
                    if re.search(pattern, df_patent.loc[p_index,"text"]):
                        cited_num += 1
                        p_cited_d["drug_word"] = drug_name
                        break
                else:  # 长度大于4的，需要进行去除大小写匹配
                    pattern = fr'\b{drug_name.lower()}\b'
                    if re.search(pattern, patent["text"]):
                        cited_num += 1
                        p_cited_d["drug_word"] = drug_name
                        break
            except:
                if drug_name in df_patent.loc[p_index,"text"]:
                    cited_num += 1
                    p_cited_d['drug_word'] = drug_name
                    break
        # 判断cited_num是否大于0
        if cited_num > 0:
            id += 1
            p_cited_d["id"] = id
            p_cited_d["drug_id"] = df_drug.loc[d_index, "drug_id"]
            p_cited_d["article_id"] = df_patent.loc[p_index,"id"]
            patent_cited_drug.append(p_cited_d)

df_match_patent = pd.DataFrame(patent_cited_drug)
df_match_patent.to_excel(r"match_patent_cited_drug.xlsx")

