# STInt-Dataset
STInt (**S**cience-**T**echnology-**I**ndustry i**nt**eractions) Dataset

## 1. Introduction
In an era of rapid economic development, science, technology, and industry influence each other and develop together. Scientific research and technological development promote the rapid progress of industries. In turn, industrial progress is also an important driving force for scientific research and technological development1. As early as the early 1990s, some scholars noticed the close connections among science, technology and industry, and conducted relevant research from the perspective of innovation. In the literature, scientific publications, patents, and products are usually viewed as respective proxies of scientific research, technological development, and industrial progress.

Last two decades witnessed significant progress in the science-technology or science-technology-industry interactions. Several perspectives have been investigated as follows: (1) thematic structure based linkages among these three resources; (2) academic inventors bridging science and technology; (3) concordance table among science, technology, and industry classification systems; (4) mutual citations among scholarly articles, patents, and products.

A multi-source integrated dataset covering science, technology, and industry information, named as STInt (**S**cience-**T**echnology-**I**ndustry i**nt**eractions) dataset is developed. This dataset will further promote systematic understanding of the linkages among science, technology, and industry. 
## 2. Tables and Views
The STInt dataset is stored in the format of MySQL database, which comprises the 48 tables and 5 views as follows:
### 2.1 tables

affiliation, article, article_annotation, article_author, article_author_affiliation, article_category, article_cited_article, article_descriptor, article_descriptor_qualifier, atc_code, author, category, cited_article, cited_patent, country_region, cpc, descriptor, descriptor_qualifier, descriptor_tree_number, drug, drug_article, drug_atc_code, drug_descriptor, drug_drugbank_id, drug_interaction, drug_manufacturer, drug_patent_original, drug_synonym, entity_category, inventor_applicant, ipc, manufacturer, non_patent, organization_linkage, patent, patent_annotation, patent_applicant, patent_cited_patent, patent_cpc, patent_inventor, patent_ipc, patent_non_patent, patent_original, patent_priority, qualifier, qualifier_tree_number, researcher_linkage, and synonym

### 2.2 views

view_citation_article_article, view_citation_article_patent, view_citation_drug_patent, view_citation_patent_article, and view_citation_patent_patent

## 3. Source Codes
### 3.1 Drug Entity Identification
To recognize drug entity mentions, the two python files ``Step1_DrugEntityIdentification.py`` and ``Step2_CreateAnnotationTable.py`` in the *Drug entity identification* folder can be run sequentially to achieve this. It is worth noting that after running ``Step1_DrugEntityIdentification.py``, the identification results need to be manually checked. Based on the checked results, then one can run ``Step2_CreateAnnotationTable.py``.

Specifically, ``Step1_DrugEntityIdentification.py`` is divided into five sub-steps for drug entity identification: (1) Step 1.1: obtaining the drug and its synonym data; (2) Step 1.2: obtaining the titles and abstracts of articles; (3) Step 1.3: obtaining the titles and abstracts of patents; (4) Step 1.4: matching drug entities from the title and abstract of each article; (5) Step 1.5: matching drug entities from the title and abstract of each patent.

To implement Step 1.1-1.3, the package ``pymysql`` is used to connect to the local MySQL database and obtain the data by executing the corresponding SQL statements. In order to implement Step1.4-1.5, the package ``re`` is used for matching drug entities, which in turn constructs the citations from articles to drugs and from patents to drugs.

In addition, ``Step2_CreateAnnotationTable.py`` constructs the *article_annotation* table and *patent_annotation* table based on the drug identification results. It is mainly divided into three sub-steps: (1) Step 2.1: defining the preprocessing function, and the defined function has been annotated in ``Step2_CreateAnnotationTable.py``; (2) Step 2.2: creating the *article_annotation* table; (3) Step 2.3: creating the *patent_annotation* table.

### 3.2 Organization Disambiguation
To disambiguate the organizations, four python files ``Step1_CalculateSimilarityOfOrganizationPairs.py``, ``Step2_UpdatePreferred_id.py``, ``Step3_UpdateLinkageTable.py``, and ``Step4_CreateOrganizationLinkageTable.py`` in the *Organization disambiguation* folder can be run sequentially.

``Step1_CalculateSimilarityOfOrganizationPairs.py` obtains three types of organizations through the package ``pymysql``, and further calculates the similarity between different organization in the same category through the package ``fuzzywuzzy``. Finally, the calculation results need to be manually checked.

``Step2_UpdatePreferred_id.py`` further updates the *preferred_id* of the organization based on the disambiguation results.

``Step3_UpdateLinkageTable.py`` further updates the tables associated with three types of organizations with (1) *article_author_affiliation* table, (2) *drug_manufacturer* table, and (3) *patent_applicant* table, based on the update result of *preferred_id* in ``Step2_UpdatePreferred_id.py``.

``Step4_CreateOrganizationLinkageTable.py`` creates the linkage among three types of organizations (i.e., affiliations, applicants, and manufacturers), and save them in the *organization_linkage* table.

### 3.3 Descriptive Statistics
The descriptive statistics of the STInt dataset can be obtained by running ``DescriptiveStatistics.py``.

## 4. References
[1] Shuo Xu, Zhen Liu, and Xin An. [STInt Dataset: A Multi-Source Integrated Dataset Covering Science, Technology, and Industry Information in the Pharmaceutical Field](https://doi.org/10.1080/10494820.2025.2524838). *Scientific Data*, Vol. 12, pp. 1056. 

[2] 徐硕，张跃富，安欣，2025. 全领域多层级科学−技术分类体系映射研究. *情报学报*. (Accepted)

[3] Shuo Xu, Zhen Liu, Xin An, Hong Wang, and Hongshen Pang, 2025. [Linkages among Science, Technology, and Industry on the basis of Main Path Analysis](https://doi.org/10.1016/j.joi.2024.101617). *Journal of Informetrics*, Vol. 19, No. 1, pp. 101617.

[4] Shuo Xu, Xinyi Ma, Hong Wang, Xin An, and Ling Li, 2024. [A Recommendation Approach of Scientific Non-Patent Literature on the basis of Heterogeneous Information Network](https://doi.org/10.1016/j.joi.2024.101557). *Journal of Informetrics*, Vol. 18, No. 4, pp. 101557. 

[5] 徐硕，孙童菲，罗贵缘，苑洲桐，连佳欣，刘畅，2024. [分类体系双向映射视角下的科学-技术互动分析](https://doi.org/10.3969/j.issn.1672-6081.2024.04.001). *中国发明与专利*，Vol. 21，No. 4，pp. 4-15.

[6] Shuo Xu, Ling Li, and Xin An, 2023. [Do Academic Inventors have Diverse Interests?](https://doi.org/10.1007/s11192-022-04587-0) *Scientometrics*, Vol. 128, No. 2, pp. 1023-1053. 

[7] Shuo Xu, Ling Li, Xin An, Liyuan Hao, and Guancan Yang, 2021. [An Approach for Detecting the Commonality and Specialty between Scientific Publications and Patents](https://doi.org/10.1007/s11192-021-04085-9). *Scientometrics*, Vol. 126, No. 9, pp. 7445-7475. 

[8] Shuo Xu, Dongsheng Zhai, Feifei Wang, Xin An, Hongshen Pang, and Yirong Sun, 2019. [A Novel Method for Topic Linkages between Scientific Publications and Patents](https://doi.org/10.1002/asi.24175). *Journal of the Association for Information Science and Technology*, Vol. 70, No. 9, pp. 1026-1042.
