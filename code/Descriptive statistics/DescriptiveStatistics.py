import pymysql
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as patches
import seaborn as sns

# 数据库连接参数
config = {
		    'user': 'root',
		    'password': 'your password',
		    'host': '127.0.0.1',
		    'database': 'STInt',
		}
cnx = pymysql.connect(**config)
cursor = cnx.cursor()

"""
(1) 专利和论文数量在不同年份的分布情况
"""
# 查询论文数据
query_articles = "SELECT publication_year, COUNT(*) as paper_count FROM article GROUP BY publication_year;"
cursor.execute(query_articles)
result_articles = cursor.fetchall()
df_articles = pd.DataFrame(result_articles, columns=['publication_year', 'paper_count'])
# 在DataFrame中排序
df_articles = df_articles.sort_values(by='publication_year', ascending=True)

# 查询专利数据
query_patents = "SELECT pub_date FROM patent"
cursor.execute(query_patents)
result_patents = cursor.fetchall()
df_patents = pd.DataFrame(result_patents, columns=['pub_date'])

# 数据预处理：将pub_date转换为年份
df_patents['publication_year'] = pd.to_datetime(df_patents['pub_date']).dt.year
df_patents_grouped = df_patents.groupby('publication_year').size().reset_index(name='patent_count')

# 设置全局字体大小
mpl.rcParams['font.size'] = 15  # 可以根据需要调整字体大小
# 设置全局字体为Times New Roman
mpl.rcParams['font.family'] = 'Times New Roman'

# 可视化数据
plt.figure(figsize=(14, 7))

# 绘制论文数量随年份变化的折线图
plt.plot(df_articles['publication_year'],
         df_articles['paper_count'],
         marker='o',
         label='Article')
# 在论文折线图下方添加阴影
plt.fill_between(df_articles['publication_year'],
                 df_articles['paper_count'],
                 color='blue',
                 alpha=0.1)

# 找出论文数量最大的年份和数量
max_paper_year = df_articles.loc[df_articles['paper_count'].idxmax(),
                                 'publication_year']
max_paper_count = df_articles['paper_count'].max()
# 在图表上显示最大论文数量的数据标签和年份
plt.text(max_paper_year, max_paper_count,
         f'{max_paper_count} ({max_paper_year})', ha='center', va='bottom')

# 绘制专利数量随年份变化的折线图
plt.plot(df_patents_grouped['publication_year'], df_patents_grouped['patent_count'],
         marker='x',label='Patent')
# 在专利折线图下方添加阴影
plt.fill_between(df_patents_grouped['publication_year'], df_patents_grouped['patent_count'],
                 color='red', alpha=0.1)

# 找出专利数量最大的年份和数量
max_patent_year = df_patents_grouped.loc[
    df_patents_grouped['patent_count'].idxmax(), 'publication_year']
max_patent_count = df_patents_grouped['patent_count'].max()
# 在图表上显示最大专利数量的数据标签和年份
plt.text(max_patent_year, max_patent_count,
         f'{max_patent_count} ({max_patent_year})', ha='center', va='bottom')

plt.xlabel('Year')
plt.ylabel('Number')

# 将图例居中显示
plt.legend(loc='upper left')
plt.ylim(0,750)

plt.grid(True)
plt.savefig(r"论文和专利根据年份的统计结果.SVG",format='SVG',dpi=1000,bbox_inches='tight')
plt.show()


"""
(2) 统计专利的被引专利和非专利参考文献数量
"""
# 查询专利引用专利数据（cited_patent表）
query_cited_patents = """
SELECT COALESCE(publication_date, application_date) AS date, COUNT(*) as patent_citations
FROM cited_patent
WHERE publication_date IS NOT NULL OR application_date IS NOT NULL
GROUP BY date;
"""
cursor.execute(query_cited_patents)
result_cited_patents = cursor.fetchall()
df_cited_patents = pd.DataFrame(result_cited_patents, columns=['date', 'patent_citations'])

# 查询非专利参考文献数据（non_patent表）
query_non_patents = """
SELECT publication_year, COUNT(*) as non_patent_references
FROM non_patent
WHERE publication_year IS NOT NULL and doi is not null
GROUP BY publication_year;
"""
cursor.execute(query_non_patents)
result_non_patents = cursor.fetchall()
df_non_patents = pd.DataFrame(result_non_patents, columns=['publication_year', 'non_patent_references'])
# 在DataFrame中排序
df_non_patents = df_non_patents.sort_values(by='publication_year', ascending=True)

# 数据预处理
df_cited_patents['publication_year'] = pd.to_datetime(df_cited_patents['date']).dt.year
df_cited_patents_grouped = df_cited_patents.groupby('publication_year').sum().reset_index()

# 合并数据
df_combined = pd.merge(df_cited_patents_grouped, df_non_patents, on='publication_year', how='outer')


plt.figure(figsize=(14, 7))

# 绘制专利引用数量随年份变化的折线图
plt.plot(df_combined['publication_year'],
         df_combined['patent_citations'],
         marker='o',
         label='Cited Patent')
plt.fill_between(df_combined['publication_year'],
                 df_combined['patent_citations'],
                 color='blue',
                 alpha=0.1)

# 找出专利引用数量最大的年份和数量
max_citation_year = int(df_combined.loc[df_combined['patent_citations'].idxmax(),
                                    'publication_year'])
max_citation_count = int(df_combined['patent_citations'].max())
# 在图表上显示最大专利引用数量的数据标签和年份
plt.text(max_citation_year,
         max_citation_count,
         f'{max_citation_count} ({max_citation_year})',
         ha='center',
         va='bottom')

# 绘制非专利参考文献数量随年份变化的折线图
plt.plot(df_combined['publication_year'],
         df_combined['non_patent_references'],
         marker='x',
         label='scientific non-Patent Reference')
plt.fill_between(df_combined['publication_year'],
                 df_combined['non_patent_references'],
                 color='red',
                 alpha=0.1)

# 找出非专利参考文献数量最大的年份和数量
max_reference_year = int(df_combined.loc[df_combined['non_patent_references'].idxmax(),
                                     'publication_year'])
max_reference_count = int(df_combined['non_patent_references'].max())
# 在图表上显示最大非专利参考文献数量的数据标签和年份
plt.text(max_reference_year,
         max_reference_count,
         f'{max_reference_count} ({max_reference_year})',
         ha='center',
         va='bottom')

plt.xlabel('Year')
plt.ylabel('Number')
plt.legend(loc='upper left')
plt.ylim(0,3500)
plt.grid(True)

# 保存和显示图表
plt.savefig(
    r"专利的被引专利和非专利参考文献根据年份的统计结果.SVG",
    format='SVG',
    dpi=1000,
    bbox_inches='tight')
plt.show()


"""
(3) 论文的参考文献和被引专利数量的年度分析情况
"""
# 查询论文参考文献数据（doi不为空）
query_ref_articles = """
SELECT publication_year, COUNT(*) as reference_count
FROM cited_article
WHERE doi IS NOT NULL AND publication_year IS NOT NULL AND flag = 0
GROUP BY publication_year
ORDER BY publication_year;
"""
cursor.execute(query_ref_articles)
result_ref_articles = cursor.fetchall()
df_ref_articles = pd.DataFrame(result_ref_articles, columns=['publication_year', 'reference_count'])

# 查询被引专利数据（doc_no不为空）
query_cited_patents = """
SELECT publication_date, COUNT(*) as cited_patent_count
FROM cited_article
WHERE doc_no IS NOT NULL AND publication_date IS NOT NULL
GROUP BY publication_date
"""
cursor.execute(query_cited_patents)
result_cited_patents = cursor.fetchall()
df_cited_patents = pd.DataFrame(result_cited_patents, columns=['publication_date', 'cited_patent_count'])

# 数据预处理
df_cited_patents['publication_year'] = pd.to_datetime(
    df_cited_patents['publication_date']).dt.year
df_cited_patents_grouped = df_cited_patents.groupby('publication_year').sum().reset_index().sort_values(by='publication_year')


fig, axs = plt.subplots(1, 2, figsize=(18, 7))

# 子图1：论文参考文献数量
axs[0].plot(df_ref_articles['publication_year'],
            df_ref_articles['reference_count'],
            marker='o',
            label='Article Reference')
axs[0].fill_between(df_ref_articles['publication_year'],
                    df_ref_articles['reference_count'],
                    color='blue',
                    alpha=0.1)

# 最大值标签
max_ref_year = df_ref_articles['publication_year'][
    df_ref_articles['reference_count'].idxmax()]
max_ref_count = df_ref_articles['reference_count'].max()
axs[0].text(max_ref_year,
            max_ref_count,
            f'{max_ref_count} ({max_ref_year})',
            ha='center',
            va='bottom')

axs[0].set_xlabel('Year')
axs[0].set_ylabel('Number')
axs[0].grid(True)
axs[0].set_ylim(0, max_ref_count+1000)  # 设置纵坐标范围从0开始到max_value

# 子图2：被引专利数量
axs[1].plot(df_cited_patents_grouped['publication_year'],
            df_cited_patents_grouped['cited_patent_count'],
            marker='x',
            color='darkorange',
            label='Cited Patent')
axs[1].fill_between(df_cited_patents_grouped['publication_year'],
                    df_cited_patents_grouped['cited_patent_count'],
                    color='red',
                    alpha=0.1)

# 最大值标签
max_patent_year = df_cited_patents_grouped['publication_year'][
    df_cited_patents_grouped['cited_patent_count'].idxmax()]
max_patent_count = df_cited_patents_grouped['cited_patent_count'].max()
axs[1].text(max_patent_year,
            max_patent_count,
            f'{max_patent_count} ({max_patent_year})',
            ha='center',
            va='bottom')

axs[1].set_xlabel('Year')
# axs[1].set_ylabel('Count')
axs[1].grid(True)
axs[1].set_ylim(0, max_patent_count+2)  # 设置纵坐标范围从0开始到max_value
# axs[1].legend(loc='upper left')

# 显示图表
plt.savefig(
    r"论文的参考文献和引用专利根据年份的统计结果.SVG",
    format='SVG',
    dpi=1000,
    bbox_inches='tight')
# 设置纵坐标从0开始
plt.ylim(ymin=0)
plt.show()


"""
(4) 不同机构的作者数量
"""
# SQL 查询语句
query = """
select aa.affiliation_id, name, aa.count, aa.`比例` from (
SELECT aesa.affiliation_id, count(*) as count, count(*) / 43283 as `比例`
    FROM
    (SELECT es.id, aes.id as aes_id
    FROM entity_science es JOIN article_entity_science aes ON es.id = aes.entity_id) a1
    JOIN article_entity_science_affiliation aesa ON a1.aes_id=aesa.article_entity_science_id
    WHERE aesa.affiliation_id IS NOT NULL
    GROUP BY aesa.affiliation_id
    ORDER BY count(*) DESC
    LIMIT 20) aa JOIN affiliation on aa.affiliation_id=affiliation.id;
"""

# 连接数据库并执行查询
try:
    df = pd.read_sql(query, conn)

    # 可视化展示
    plt.figure(figsize=(14, 6))
    barplot = sns.barplot(x='count', y='name', data=df)
    plt.xlabel('Number of authors')
    plt.ylabel('Affiliation')

    # 在条形图上添加数据标签
    for index, p in enumerate(barplot.patches):
        width = p.get_width()
        proportion = df.iloc[index]['比例'] * 100  # 获取对应行的比例值并转换为百分比
        plt.text(width + 5,
                 p.get_y() + p.get_height() / 2,
                 f'{int(width)} ({proportion:.2f}%)',
                 ha='left',
                 va='center')

    plt.savefig(r"作者数量的机构分布统计.SVG", format='SVG', dpi=1000,bbox_inches='tight')
    plt.show()
except pymysql.MySQLError as e:
    print(f"Error: {e}")


"""
(5) 不同机构的学术发明人分布情况
"""
# SQL 查询语句
query = """
select aesa.institution, count(*) as count from
(select es.entity_science_id as id, aes.id as aes_id
from entity_linkage es join article_entity_science aes on es.entity_science_id = aes.entity_id) a1
join article_entity_science_affiliation aesa on a1.aes_id=aesa.article_entity_science_id 
where aesa.institution is not null GROUP BY aesa.institution ORDER BY count(*) DESC limit 20;
"""

# 连接数据库并执行查询
try:
    df = pd.read_sql(query, conn)

    # 可视化展示
    plt.figure(figsize=(14, 6))
    barplot = sns.barplot(x='count', y='institution', data=df)
    plt.xlabel('Number of academic inventors')
    plt.ylabel('Institution')

    # 在条形图上添加数据标签
    for p in barplot.patches:
        width = p.get_width()
        plt.text(width, p.get_y() + p.get_height() / 2,
                 f'{int(width)}', ha='left', va='center')

    plt.savefig(r"不同机构的学术发明人分布情况.SVG", format='SVG', dpi=1000,bbox_inches='tight')
    plt.show()

except pymysql.MySQLError as e:
    print(f"Error: {e}")



"""
(6) 不同MeSH分类的论文数量分析
"""
# SQL 查询语句
descriptor_query = """
select a1.descriptor_id, a1.count, descriptor.name from
(select descriptor_id, count(*) as count from article_descriptor 
GROUP BY descriptor_id ORDER BY count(*) DESC) a1 join descriptor
on a1.descriptor_id=descriptor.id ORDER BY count DESC limit 20;
"""
dataframe_descriptor = pd.read_sql(descriptor_query, conn)

qualifier_query = """
select a1.qualifier_id, a1.count, qualifier.name from
(select qualifier_id, count(*) as count from article_descriptor_qualifier
GROUP BY qualifier_id ORDER BY count(*) DESC) a1 join qualifier
on a1.qualifier_id=qualifier.id ORDER BY count DESC limit 20;
"""
dataframe_qualifier = pd.read_sql(qualifier_query, conn)

# 设置全局字体大小
mpl.rcParams['font.size'] = 18  # 可以根据需要调整字体大小

sns.set_palette("muted")

# 创建一个图形和两个子图（按照一列两行排列）
fig, axes = plt.subplots(2, 1, figsize=(20, 14))  # 你可以根据需要调整图形的尺寸

# 第一个子图 - descriptors-描述符
sns.barplot(x='count', y='name', data=dataframe_descriptor, ax=axes[0])
# axes[0].set_title('The top 20 descriptors by number of articles')
axes[0].set_xlabel('Number of articles')
axes[0].set_ylabel('Descriptor')
# 添加数据标签
for p in axes[0].patches:
    width = p.get_width()
    axes[0].text(width, p.get_y() + p.get_height() / 2,
                 f'{int(width)}',
                 ha='left', va='center')

# 第二个子图 - qualifiers - 限定符
sns.barplot(x='count', y='name', data=dataframe_qualifier, ax=axes[1])
# axes[1].set_title('The top 20 qualifiers by number of articles')
axes[1].set_xlabel('Number of articles')
axes[1].set_ylabel('Qualifier')
# 添加数据标签
for p in axes[1].patches:
    width = p.get_width()
    axes[1].text(width, p.get_y() + p.get_height() / 2,
                 f'{int(width)}',
                 ha='left', va='center')

# 调整子图的布局，防止标签重叠
plt.tight_layout()

plt.savefig(r"不同MeSH分类的论文数量分析.SVG", format='SVG', dpi=1000,bbox_inches='tight')
plt.show()



"""
(7) 不同IPC和CPC的专利数量分布
"""
import matplotlib.pyplot as plt
import seaborn as sns

# SQL 查询语句
IPC_query = """
select a1.ipc_id, a1.count, ipc.symbol FROM
(select ipc_id, count(*) as count from patent_ipc  
GROUP BY ipc_id ORDER BY count(*) DESC) a1 join ipc
on a1.ipc_id=ipc.id ORDER BY count desc limit 20;
"""
dataframe_IPC = pd.read_sql(IPC_query, conn)

CPC_query = """
select a1.cpc_id, a1.count, cpc.symbol FROM
(select cpc_id, count(*) as count from patent_cpc  
GROUP BY cpc_id ORDER BY count(*) DESC) a1 join cpc
on a1.cpc_id=cpc.id ORDER BY count desc limit 20;
"""
dataframe_CPC = pd.read_sql(CPC_query, conn)


sns.set_palette("muted")
# 创建一个图形和两个子图（按照一列两行排列）
fig, axes = plt.subplots(2, 1, figsize=(20, 14))  # 你可以根据需要调整图形的尺寸

# 第一个子图 - descriptors-描述符
sns.barplot(x='count', y='symbol', data=dataframe_IPC, ax=axes[0])
# axes[0].set_title('The top 20 IPCs by number of patents')
axes[0].set_xlabel('Number of patents')
axes[0].set_ylabel('IPC')
# 添加数据标签
for p in axes[0].patches:
    width = p.get_width()
    axes[0].text(width, p.get_y() + p.get_height() / 2,
                 f'{int(width)}',
                 ha='left', va='center')

# 第二个子图 - qualifiers - 限定符
sns.barplot(x='count', y='symbol', data=dataframe_CPC, ax=axes[1])
# axes[1].set_title('The top 20 CPCs by number of patents')
axes[1].set_xlabel('Number of patents')
axes[1].set_ylabel('CPC')
# 添加数据标签
for p in axes[1].patches:
    width = p.get_width()
    axes[1].text(width, p.get_y() + p.get_height() / 2,
                 f'{int(width)}',
                 ha='left', va='center')

# 调整子图的布局，防止标签重叠
plt.tight_layout()

plt.savefig(r"不同IPC和CPC的专利数量分布.SVG", format='SVG', dpi=1000,bbox_inches='tight')
plt.show()


"""
(8) 不同ATC分类的药物数量分析
"""
query = """
select code, count(*) as count from 
(SELECT id, drug_id, LEFT(code, 1) AS code FROM drug_atc_code) as a1
GROUP BY code ORDER BY count(*) desc;
"""
df = pd.read_sql(query, conn)

code_list = [
    'A - Alimentary tract and metabolism',
    'B - Blood and blood forming organs',
    'C - Cardiovascular system',
    'D - Dermatologicals',
    'G - Genito-urinary system and sex hormones',
    'H - Systemic hormonal preparations',
    'J - Antiinfectives for systemic use',
    'L - Antineoplastic and immunomodulating agents',
    'M - Musculo-skeletal system',
    'N - Nervous system',
    'P - Antiparasitic products, insecticides and repellents',
    'R - Respiratory system',
    'S - Sensory organs',
    'V - Various'
]
for index in df.index:
    code = df.loc[index,'code']
    for atc in code_list:
        if code in atc.split('-')[0]:
            df.loc[index,'code'] = atc

# 可视化展示
plt.figure(figsize=(16, 8))
barplot = sns.barplot(x='count', y='code', data=df)
#     plt.title('Top 20 Institutions by Author Count')
plt.xlabel('Number of drugs')
plt.ylabel('ATC code')

# 在条形图上添加数据标签
for p in barplot.patches:
    width = p.get_width()
    plt.text(width + 2, p.get_y() + p.get_height() / 2,
             f'{int(width)}',
             ha='left', va='center')

plt.savefig(r"不同ATC分类的药物数量分析.SVG", format='SVG', dpi=1000,bbox_inches='tight')
plt.show()


"""
(9) 不同WoS分类的论文数量分布
"""
# SQL 查询语句
WoS_query = """
select c.name, a1.article_number from 
(select category_id, count(*) as article_number from article_category GROUP BY category_id ORDER BY count(*) desc limit 20) a1 
join category c on a1.category_id=c.id;
"""
df_WoS = pd.read_sql(WoS_query, conn)


# 设置科研风格的配色方案
sns.set_palette("muted")

# 可视化展示
plt.figure(figsize=(16, 8))
barplot = sns.barplot(x='article_number', y='name', data=df_WoS)
#     plt.title('Top 20 Institutions by Author Count')
plt.xlabel('Number of articles')
plt.ylabel('WoS category')

# 在条形图上添加数据标签
for p in barplot.patches:
    width = p.get_width()
    plt.text(width + 2, p.get_y() + p.get_height() / 2,
             f'{int(width)}',
             ha='left', va='center')

plt.savefig(r"不同WoS分类的论文数量分布.SVG", format='SVG', dpi=1000,bbox_inches='tight')
plt.show()
