"""
Step 2：构建article_annotation和patent_annotation表
Step 2.1: 定义预处理函数
Step 2.2： 构建article_annotation表
Step 2.3：构建patent_annotation表

构建article_annotation表和patent_annotation表。
字段包括: id,article_id/patent_id,passage_type,mention,span_start,span_end,
         drug_id,synonym_id,category_id
"""

import pymysql
import pandas as ps
import re

# 建立数据库连接
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='your password',
    database='STInt',
    cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()


### 我们根据step 1的结果，核对了论文引用药物和专利引用药物的数据，
### 并把数据分别存储于citation_article_drug表（ id  article_id  drug_id）
### 和citation_patent_drug（ id  patent_id  drug_id）

"""
Step 2.1: 定义预处理函数
"""
"""
返回关键词所在字符串的位置
"""
def get_keyword_position(text, keyword):
    # Find the start and end positions of the keyword in the text
    start_position = text.find(keyword)
    end_position = start_position + len(keyword) - 1

    return start_position, end_position

"""
获取查询结果
"""
def get_query_result(sql):
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

"""
返回一个dict格式的论文的识别结果
"""
def get_article_annotion_dict(id, article_id, drug_id, text, drug_name, passage_type=None, mention=None,
                              span_start=None, span_end=None, synonym_id=None):
    a_annotion = {}
    a_annotion['id'] = id
    a_annotion['article_id'] = article_id
    a_annotion['text'] = text
    a_annotion['drug_name'] = drug_name
    a_annotion['passage_type'] = passage_type
    a_annotion['mention'] = mention
    a_annotion['span_start'] = span_start
    a_annotion['span_end'] = span_end
    a_annotion['drug_id'] = drug_id
    a_annotion['synonym_id'] = synonym_id
    return a_annotion

def get_patent_annotion_dict(id, patent_id, drug_id, text, drug_name, passage_type=None,
                              mention=None, span_start=None, span_end=None, synonym_id=None):
    a_annotion = {}
    a_annotion['id'] = id
    a_annotion['patent_id'] = patent_id
    a_annotion['text'] = text
    a_annotion['drug_name'] = drug_name
    a_annotion['passage_type'] = passage_type
    a_annotion['mention'] = mention
    a_annotion['span_start'] = span_start
    a_annotion['span_end'] = span_end
    a_annotion['drug_id'] = drug_id
    a_annotion['synonym_id'] = synonym_id
    return a_annotion


"""
文本清洗
"""
def multi_replace(text):
    replace_text = [
        '<article-title>', '</article-title>', '<abstract>', '<p>', '</p>',
        '</abstract>', '\n', '\r', '<invention-title lang="en">', '</invention-title>',
        '<abstract lang="en">'
    ]
    for rep in replace_text:
        text = text.replace(rep, " ")
    return text

"""
Step 2.2： 构建article_annotation表
"""

# 创建查询，读取预处理好的引用数据
sql_query_1 = "SELECT * FROM citation_article_drug;"
citation_article_drug = pd.read_sql_query(sql_query_1, connection)

article_annotation = []  ## 保存结果
non_match_id = []
abst_None_id = []
for index in citation_article_drug.index:
    try:
        id = citation_article_drug.loc[index, 'id']
        article_id = citation_article_drug.loc[index, 'article_id']
        drug_id = citation_article_drug.loc[index, 'drug_id']

        # 获取药物的名称
        drug_name = get_query_result(
            "select name from drug where id = {}".format(drug_id))[0]['name']

        # 获取药物的同义词
        select_synonym_sql = "select ds.synonym_id, name from drug_synonym ds join synonym s on ds.synonym_id=s.id where drug_id = {};".format(drug_id)
        drug_synonym_name = get_query_result(select_synonym_sql)

        # 获取论文的标题和摘要
        article_title_abst = get_query_result(
            "select title,abst from article where id = {}".format(article_id))[0]
        if not pd.isna(article_title_abst['title']):
            title = multi_replace(article_title_abst['title'])
        if not pd.isna(article_title_abst['abst']):
            abst = multi_replace(article_title_abst['abst'])

        ### 先进行标题的识别
        result_flag = 0
        if len(drug_name) > 4:
            start_position, end_position = get_keyword_position(title.lower(), drug_name.lower())
        else:
            start_position, end_position = get_keyword_position(title, drug_name)
        if start_position != -1:  ## 药物名称匹配成功
            result_flag = 1
            a_annotion = get_article_annotion_dict(
                id, article_id, drug_id, article_title_abst,
                drug_name + str(drug_synonym_name), 'TITLE', drug_name,
                start_position, end_position)
        else:
            """
            如果药物名称匹配不成功的话，进行药物同义词的匹配
            """
            for synonym in drug_synonym_name:
                synonym_name = synonym['name']
                if len(synonym_name) > 4:
                    start_position, end_position = get_keyword_position(title.lower(), synonym_name.lower())
                else:
                    start_position, end_position = get_keyword_position(title, synonym_name)
                if start_position != -1:
                    result_flag = 1
                    a_annotion = get_article_annotion_dict(
                        id, article_id, drug_id, article_title_abst,
                        drug_name + str(drug_synonym_name), 'TITLE', synonym_name,
                        start_position, end_position, synonym['synonym_id'])
                    break
        if result_flag == 0:
            """
            标题匹配不成功，进行摘要的匹配
            """
            if len(drug_name) > 4:
                start_position, end_position = get_keyword_position(abst.lower(), drug_name.lower())
            else:
                start_position, end_position = get_keyword_position(abst, drug_name)
            if start_position != -1:  ## 药物名称匹配成功
                result_flag = 1
                a_annotion = get_article_annotion_dict(
                    id, article_id, drug_id, article_title_abst,
                    drug_name + str(drug_synonym_name), 'ABSTRACT', drug_name,
                    start_position, end_position)
            else:
                """
                如果药物名称匹配不成功的话，进行药物同义词的匹配
                """
                for synonym in drug_synonym_name:
                    synonym_name = synonym['name']
                    if len(synonym_name) > 4:
                        start_position, end_position = get_keyword_position(abst.lower(), synonym_name.lower())
                    else:
                        start_position, end_position = get_keyword_position(abst, synonym_name)
                    if start_position != -1:
                        result_flag = 1
                        a_annotion = get_article_annotion_dict(
                            id, article_id, drug_id, article_title_abst,
                            drug_name + str(drug_synonym_name), 'ABSTRACT',
                            synonym_name, start_position, end_position,
                            synonym['synonym_id'])
                        break
        if result_flag == 1:
            article_annotation.append(a_annotion)
        else:
            non_match_id.append(id)
            article_annotation.append(
                get_article_annotion_dict(id, article_id, drug_id,
                                          article_title_abst,
                                          drug_name + str(drug_synonym_name)))
    except Exception as e:
        print(e.args)
        print(article_title_abst)
        abst_None_id.append(article_id)
        non_match_id.append(id)
        article_annotation.append(get_article_annotion_dict(id, article_id, drug_id,
                                      article_title_abst,drug_name + str(drug_synonym_name)))
    
print(pd.DataFrame(article_annotation).head())

pd.DataFrame(article_annotation).to_excel(r"article_annotion.xlsx")


"""
Step 2.3：构建patent_annotation表
"""

sql_query_2 = "SELECT * FROM citation_patent_drug;"
citation_patent_drug = pd.read_sql_query(sql_query_2, connection)

patent_annotation = []  ## 保存结果
non_match_id = []
abst_None_id = []
for index in citation_patent_drug.index:
    try:
        id = citation_patent_drug.loc[index, 'id']
        patent_id = citation_patent_drug.loc[index, 'patent_id']
        drug_id = citation_patent_drug.loc[index, 'drug_id']

        # 获取药物的名称
        drug_name = get_query_result(
            "select name from drug where id = {}".format(drug_id))[0]['name']

        # 获取药物的同义词
        select_synonym_sql = "select ds.synonym_id, name from drug_synonym ds join synonym s on ds.synonym_id=s.id where drug_id = {};".format(drug_id)
        drug_synonym_name = get_query_result(select_synonym_sql)

        # 获取论文的标题和摘要
        patent_title_abst = get_query_result(
            "select title,abst from patent where id = {}".format(patent_id))[0]
        if not pd.isna(patent_title_abst['title']):
            title = multi_replace(patent_title_abst['title'])
        if not pd.isna(patent_title_abst['abst']):
            abst = multi_replace(patent_title_abst['abst'])

        ### 先进行标题的识别
        result_flag = 0
        if len(drug_name) > 4:
            start_position, end_position = get_keyword_position(title.lower(), drug_name.lower())
        else:
            start_position, end_position = get_keyword_position(title, drug_name)
        if start_position != -1:  ## 药物名称匹配成功
            result_flag = 1
            a_annotion = get_patent_annotion_dict(
                id, patent_id, drug_id, patent_title_abst,
                drug_name + str(drug_synonym_name), 'TITLE', drug_name,
                start_position, end_position)
        else:
            """
            如果药物名称匹配不成功的话，进行药物同义词的匹配
            """
            for synonym in drug_synonym_name:
                synonym_name = synonym['name']
                if len(synonym_name) > 4:
                    start_position, end_position = get_keyword_position(title.lower(), synonym_name.lower())
                else:
                    start_position, end_position = get_keyword_position(title, synonym_name)
                if start_position != -1:
                    result_flag = 1
                    a_annotion = get_patent_annotion_dict(
                        id, patent_id, drug_id, patent_title_abst,
                        drug_name + str(drug_synonym_name), 'TITLE', synonym_name,
                        start_position, end_position, synonym['synonym_id'])
                    break
        if result_flag == 0:
            """
            标题匹配不成功，进行摘要的匹配
            """
            if len(drug_name) > 4:
                start_position, end_position = get_keyword_position(abst.lower(), drug_name.lower())
            else:
                start_position, end_position = get_keyword_position(abst, drug_name)
            if start_position != -1:  ## 药物名称匹配成功
                result_flag = 1
                a_annotion = get_patent_annotion_dict(
                    id, patent_id, drug_id, patent_title_abst,
                    drug_name + str(drug_synonym_name), 'ABSTRACT', drug_name,
                    start_position, end_position)
            else:
                """
                如果药物名称匹配不成功的话，进行药物同义词的匹配
                """
                for synonym in drug_synonym_name:
                    synonym_name = synonym['name']
                    if len(synonym_name) > 4:
                        start_position, end_position = get_keyword_position(abst.lower(), synonym_name.lower())
                    else:
                        start_position, end_position = get_keyword_position(abst, synonym_name)
                    if start_position != -1:
                        result_flag = 1
                        a_annotion = get_patent_annotion_dict(
                            id, patent_id, drug_id, patent_title_abst,
                            drug_name + str(drug_synonym_name), 'ABSTRACT',
                            synonym_name, start_position, end_position,
                            synonym['synonym_id'])
                        break
        if result_flag == 1:
            patent_annotation.append(a_annotion)
        else:
            non_match_id.append(id)
            patent_annotation.append(
                get_patent_annotion_dict(id, patent_id, drug_id,
                                          patent_title_abst,
                                          drug_name + str(drug_synonym_name)))
    except Exception as e:
        print(e.args)
        print(patent_title_abst)
        abst_None_id.append(patent_id)
        non_match_id.append(id)
        patent_annotation.append(get_patent_annotion_dict(id, patent_id, drug_id,
                                      patent_title_abst,drug_name + str(drug_synonym_name)))
    
print(pd.DataFrame(patent_annotation).head())
pd.DataFrame(patent_annotation).to_excel(r"patent_annotion.xlsx")

