"""
由于一些表关联了机构数据，因此，在机构消歧之后，更新关联表的机构id
Step 3:更新关联表的机构id
step 3.1: article_author_affiliation
step 3.2: drug_manufacturer
step 3.3: patent_applicant
"""

import pandas as pd
import pymysql
# 建立数据库连接
connection = pymysql.connect(
	host='localhost',
    user='root',
    password='your password',
    database='STInt',
    cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()


"""
step 3.1: article_author_affiliation
"""
article_author_affiliation = pd.read_sql_query("select * from article_author_affiliation;", connection)
success_num = 0
try:
    for index in article_author_affiliation.index:
        if article_author_affiliation.loc[index,'id'] == 31071:
            continue
        if not pd.isna(article_author_affiliation.loc[index, 'affiliation_id']):
            affiliation_id = article_author_affiliation.loc[index, 'affiliation_id']
            cursor.execute(
                f"select preferred_id from affiliation where id = {affiliation_id};")
            result = cursor.fetchall()
            if not pd.isna(result[0]['preferred_id']):
                preferred_id = int(result[0]['preferred_id'])
                # 执行SQL语句
                # 更新数据的SQL语句
                update_sql = "update article_author_affiliation set affiliation_id = %s where id = %s;"
                aaa_id = article_author_affiliation.loc[index, 'id']
                cursor.execute(update_sql,(preferred_id,aaa_id))
                # 提交事务
                connection.commit()
                success_num += 1
except Exception as e:
    print(e.args)
    print(article_author_affiliation.loc[index])
print(success_num)


"""
step 3.2: drug_manufacturer
"""
drug_manufacturer = pd.read_sql_query(
    "select * from (select dm.*, m.`name`, m.preferred_id from drug_manufacturer dm left join manufacturer m on dm.manufacturer_id=m.id) a where preferred_id is not null;",
    connection)

success_num = 0
list_d_m = []
for index in drug_manufacturer.index:
    try:
        preferred_id = int(drug_manufacturer.loc[index,'preferred_id'])
        id = int(drug_manufacturer.loc[index,'id'])
        update_sql = "update drug_manufacturer set manufacturer_id = %s where id = %s;"
        cursor.execute(update_sql,(preferred_id,id))
        # 提交事务
        connection.commit()
        success_num += 1
    except:
        # 编写DELETE语句
        delete_sql = "DELETE FROM drug_manufacturer WHERE id = %s;"
        # 执行SQL语句
        cursor.execute(delete_sql, (drug_manufacturer.loc[index,"id"]))
        # 提交事务
        connection.commit()
        list_d_m.append(dict(drug_manufacturer.loc[index]))
print(success_num)
print(list_d_m)



"""
step 3.3: patent_applicant
"""
patent_applicant = pd.read_sql_query(
    "select * from (select dm.*, m.`name`, m.preferred_id from patent_applicant dm left join inventor_applicant m on dm.applicant_id=m.id) a where preferred_id is not null;",
    connection)
patent_applicant.head()

success_num = 0
list_d_m = []
for index in patent_applicant.index:
    try:
        preferred_id = int(patent_applicant.loc[index,'preferred_id'])
        id = int(patent_applicant.loc[index,'id'])
        update_sql = "update patent_applicant set applicant_id = %s where id = %s;"
        cursor.execute(update_sql,(preferred_id,id))
        # 提交事务
        connection.commit()
        success_num += 1
    except:
        list_d_m.append(dict(patent_applicant.loc[index]))
print(success_num)
print(list_d_m)

### 由于更新机构id之后，可能存在与之前的数据重复的情况。
### 因此，针对重复的情况，需要根据专利的原文档进行核对，下面是导出专利的专利号和标题的代码。

patent_id_list = pd.read_sql_query(
    "select patent_id from (select dm.*, m.`name`, m.preferred_id from patent_applicant dm left join inventor_applicant m on dm.applicant_id=m.id) a where preferred_id is not null;",
    connection)
patent_id_list.head()

patent_NO_list = []
for index in patent_id_list.index:
    each_patent = {}
    patent_id = patent_id_list.loc[index,'patent_id']
    sql = 'select title, pub_doc_no, pub_auth, pub_date, pub_kind from patent where id = {}'.format(patent_id)
    cursor.execute(sql)
    result = cursor.fetchall()[0]
    patent_NO = result['pub_auth'] + result["pub_doc_no"] + result["pub_kind"]
    Title = result["title"].replace('<invention-title lang="en">',"").replace('</invention-title>',"")
    each_patent["ID"] = patent_id
    each_patent["Patent NO."] = patent_NO
    each_patent["Publication"] = str(result["pub_date"])
    each_patent["Title"] = Title
    patent_NO_list.append(each_patent)
for p in patent_NO_list:
    print(p)

    