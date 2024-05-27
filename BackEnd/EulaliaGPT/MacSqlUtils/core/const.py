MAX_ROUND = 3  # max try times of one agent talk
# DESC_LEN_LIMIT = 200  # max length of description of each column (counted by char)
# MAX_OUTPUT_LEN = 1000  # max length of output (counted by tokens)
# RATIO = 0.8  # soft upper bound of max

ENGINE_GPT4 = 'gpt-4'
ENGINE_GPT4_32K = 'gpt-4-32k'

SELECTOR_NAME = 'Selector'
DECOMPOSER_NAME = 'Decomposer'
REFINER_NAME = 'Refiner'
SYSTEM_NAME = 'System'


# The database comprises several tables, all adhering to a consistent structure. Each table serves to encode specific data relevant to the query. Here's a breakdown of the table structure:
# 1. Time encoding: `data_inici` and `data_final`.
# 2. Spatial encoding: Some tables feature spatial data encoded in columns `municipi`, `districte`, and `barri`.
# 3. Fact description: The primary fact is described in the `valor` column.
# 4. Metadata columns: Columns like `fet_ca`, `indicador_ca`, `tags_ca`, `unitat_ca`, and `unitat_mesura_ca` provide additional information about the content of the table and should be considered when understanding the context, but they are irrelevant for SQL queries and can be disregarded.
# 5. Main Dimensions: Other columns in each table represent main dimensions and should always be retained.

selector_template = """
As an experienced and professional database administrator, your task is to analyze a user question and a database schema to provide relevant information. The database schema consists of table descriptions, each containing multiple column descriptions. Your goal is to identify the relevant tables and columns based on the user question and evidence provided.
Take a deep breath and approach this task methodically, step-by-step.

The database comprises several tables, all adhering to a consistent structure. Each table serves to encode specific data relevant to the query. Here's a breakdown of the table structure:
1. Time encoding: `data_inici` and `data_final`.
2. Spatial encoding: Some tables feature spatial data encoded in columns `municipi`, `districte`, and `barri`.
3. Fact description: The primary fact is described in the `valor` column.
4. Metadata columns: Columns like `fet_ca`, `indicador_ca`, `tags_ca`, `unitat_ca`, and `unitat_mesura_ca` provide additional information about the content of the table and should be considered when understanding the context, but they are irrelevant for SQL queries and can be disregarded.
5. Main Dimensions: Other columns in each table represent main dimensions and should always be retained.

[Instruction]:
1. You will be given a tables from a database that has been determined relevant with respect to the query.
2. Based on the user question and the provided evidence, determine if it could contain the information needed to answer the user's query. 
3. Your answer should be either `Useful` or `Not useful`. 
4. Look at the value of `indicador_ca` to understand the context and content of each table. Use this to guide your decision on usefulness.

Here is a typical example:

==========
【DB_ID】 dbeulalia
【Schema】
# poblacio_ocupada_assalariada
[
  (valor, Població ocupada assalariada. Value examples: [Decimal('576.8'), Decimal('614.4'), Decimal('619.4'), Decimal('553.2'), Decimal('100.2')])
  (data_inici, start date. Value examples: ['2021-03-01', '2009-06-01', '2012-01-01', '2023-01-01', '2022-11-01'].),
  (data_final, end date. Value examples: ['2021-03-31', '2009-06-30', '2012-12-31', '2023-12-31', '2022-11-30'].),
  (fet_ca, describes the table, should not be in the SQL query. Value examples: ['Població ocupada assalariada'].),
  (indicador_ca, describes the table, should not be in the SQL query. Value examples: ['Població ocupada assalariada'].),
  (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value examples: ['epa'] ),
  (municipi, municipality, it can only take the value of 'Barcelona'),
  (unitat_ca, gives the type of the column 'value'. Value: ['Nombre'] means that 'value' is a number),
  (unitat_mesura_ca. gives the units of measure of the column 'value'. Value: ['Milers the persones'] which means thousands of people, implying that 'value' must be multiplied by 1000),
]

【Question】
How many doctoral students from Universitat Politècnica de Catalunya were women in 2019?

【Answer】
Not useful

==========
【DB_ID】 dbeulalia
【Schema】

# alumnes_universitaris_titulats_sexe_tipus_estudi_universitat
[
  (data_inici, start date. Value examples: ['2021-09-01', '2009-09-01', '2012-09-01', '2023-09-01', '2022-09-01'].),
  (data_final, end date. Value examples: ['2021-06-30', '2009-06-30', '2012-06-30', '2023-06-30', '2022-06-30'].),
  (fet_ca, describes the table, should not be in the SQL query. Value examples: ['Nombre d’alumnes universitaris titulats'].),
  (indicador_ca, describes the table, should not be in the SQL query. Value examples: ['Nombre d’alumnes universitaris titulats per sexe, tipus d’estudi i universitat'].),
  (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value examples: ['Univesitat, Matricules, Master, Grau, Doctorat'] ),
  (municipi, municipality, it can only take the value of 'Barcelona'),
  (unitat_ca, gives the type of the column 'value'. Value: ['Nombre']),
  (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: ['Persones']),
  (valor, number of students per study, university and sex. Value examples: [2874, 957, 109, 2383, 97].),
  (universitat, university of studies. Value examples: ['Universitat de Barcelona (UB)', 'Universitat Politècnica de Catalunya (UPC)', 'Universitat Abat Oliba (UAO)', 'Universitat Autònoma de Barcelona (UAB)', 'Universitat Internacional de Catalunya (UIC)', 'Universitat Pompeu Fabra (UPF)']),
  (sexe, sex. Value examples: ['Dona', 'Home'].),
  (tipus_d_estudi. Value examples: ['Màster', 'Doctorat', 'Grau'])
]

【Question】
How many doctoral students from Universitat Politècnica de Catalunya were women in 2019?

【Answer】
Useful.

**Most of the tables should be `Useful` unless there is a clear reason they are not relevant.**

Avoid hallucinations: Avoid generating content that is not supported by the provided information, ensuring all claims, references, and data are based on the input.
==========

Here is a new example, please start answering:

【DB_ID】 {db_id}
【Schema】
{desc_str}
【Foreign keys】
{fk_str}
【Question】
{query}
【Evidence】
{evidence}
【Answer】
"""


# selector_template = """
# As an experienced and professional database administrator, your task is to analyze a user question and a database schema to provide relevant information. The database schema consists of table descriptions, each containing multiple column descriptions. Your goal is to identify the relevant tables and columns based on the user question and evidence provided.
# Take a deep breath and approach this task methodically, step-by-step.

# The database comprises several tables, all adhering to a consistent structure. Each table serves to encode specific data relevant to the query. Here's a breakdown of the table structure:
# 1. Time encoding: `data_inici` and `data_final`.
# 2. Spatial encoding: Some tables feature spatial data encoded in columns `municipi`, `districte`, and `barri`.
# 3. Fact description: The primary fact is described in the `valor` column.
# 4. Metadata columns: Columns like `fet_ca`, `indicador_ca`, `tags_ca`, `unitat_ca`, and `unitat_mesura_ca` provide additional information about the content of the table and should be considered when understanding the context, but they are irrelevant for SQL queries and can be disregarded.
# 5. Main Dimensions: Other columns in each table represent main dimensions and should always be retained.

# [Instruction]:
# 1. You will be given up to ten tables from a database that have been determined most relevant with respect to the query.
# 2. Based on the user question and the provided evidence, determine which tables could contain the information needed to answer the user's query. 
# 3. Your answer should be a dictionary of tables marked as `Useful` or `Not Useful`. 
# 4. Consider columns like `data_inici`, `valor`, `indicador_ca`, `tags_ca`, `districte`, etc., as primary in determining usefulness.
# 5. Look at the value of `indicador_ca` to understand the context and content of each table. Use this to guide your decision on usefulness.

# **Most of the tables should be `Useful` unless there is a clear reason they are not relevant.**

# Here is a typical example:

# ==========
# 【DB_ID】 dbeulalia
# 【Schema】
# # Table: poblacio_ocupada_assalariada
# [
#   (valor, Població ocupada assalariada. Value examples: [Decimal('576.8'), Decimal('614.4'), Decimal('619.4'), Decimal('553.2'), Decimal('100.2')])
#   (data_inici, start date. Value examples: ['2021-03-01', '2009-06-01', '2012-01-01', '2023-01-01', '2022-11-01'].),
#   (data_final, end date. Value examples: ['2021-03-31', '2009-06-30', '2012-12-31', '2023-12-31', '2022-11-30'].),
#   (fet_ca, describes the table, should not be in the SQL query. Value examples: ['Població ocupada assalariada'].),
#   (indicador_ca, describes the table, should not be in the SQL query. Value examples: ['Població ocupada assalariada'].),
#   (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value examples: ['epa'] ),
#   (municipi, municipality, it can only take the value of 'Barcelona'),
#   (unitat_ca, gives the type of the column 'value'. Value: ['Nombre'] means that 'value' is a number),
#   (unitat_mesura_ca. gives the units of measure of the column 'value'. Value: ['Milers the persones'] which means thousands of people, implying that 'value' must be multiplied by 1000),
# ]

# # Table: canvis_domicili_titulacio_districte_baixa_districte_alta
# [
#   (data_inici, start date. Value examples: ['2021-03-01', '2009-06-01', '2012-01-01', '2023-01-01', '2022-11-01'].),
#   (data_final, end date. Value examples: ['2021-03-31', '2009-06-30', '2012-12-31', '2023-12-31', '2022-11-30'].),
#   (fet_ca, describes the table, should not be in the SQL query. Value examples: ['Nombre de canvis de domicili'].),
#   (indicador_ca, also describes the table, should not be in the SQL query. Value examples: ['Canvis de domicili per titulació acadèmica i districte de baixa i districte d'alta'].),
#   (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value examples: ['padró municipal, migracions internes, mudances, estudis, educació'] ),
#   (municipi, municipality, it can only take the value of 'Barcelona'),
#   (districte, location in Barcelona. Value examples: ['Sant Martí', 'Gràcia', 'Eixample', 'Ciutat Vella', 'Sarrià-Sant Gervasi'].),
#   (unitat_ca, gives the type of the column 'value'. Value: ['Nombre'].),
#   (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: ['Canvis de domicili'].),
#   (valor, number of address changes. Value examples: [247, 1, 18, 33, 747].),
#   (districte_d_alta. Value examples: ['Sant Martí', 'Gràcia', 'Eixample', 'Ciutat Vella', 'Sarrià-Sant Gervasi'].),
#   (titulacio_academica. Value examples: ['Estudis universitaris, CFGS grau superior', 'Sense estudis', 'Estudis primaris, certificat d'escolaritat, EGB', 'Batxillerat elemental, graduat escolar, ESO, FPI', 'No consta'].)
# ]

# # Table: alumnes_universitaris_titulats_sexe_tipus_estudi_universitat
# [
#   (data_inici, start date. Value examples: ['2021-09-01', '2009-09-01', '2012-09-01', '2023-09-01', '2022-09-01'].),
#   (data_final, end date. Value examples: ['2021-06-30', '2009-06-30', '2012-06-30', '2023-06-30', '2022-06-30'].),
#   (fet_ca, describes the table, should not be in the SQL query. Value examples: ['Nombre d’alumnes universitaris titulats'].),
#   (indicador_ca, describes the table, should not be in the SQL query. Value examples: ['Nombre d’alumnes universitaris titulats per sexe, tipus d’estudi i universitat'].),
#   (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value examples: ['Univesitat, Matricules, Master, Grau, Doctorat'] ),
#   (municipi, municipality, it can only take the value of 'Barcelona'),
#   (unitat_ca, gives the type of the column 'value'. Value: ['Nombre']),
#   (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: ['Persones']),
#   (valor, number of students per study, university and sex. Value examples: [2874, 957, 109, 2383, 97].),
#   (universitat, university of studies. Value examples: ['Universitat de Barcelona (UB)', 'Universitat Politècnica de Catalunya (UPC)', 'Universitat Abat Oliba (UAO)', 'Universitat Autònoma de Barcelona (UAB)', 'Universitat Internacional de Catalunya (UIC)', 'Universitat Pompeu Fabra (UPF)']),
#   (sexe, sex. Value examples: ['Dona', 'Home'].),
#   (tipus_d_estudi. Value examples: ['Màster', 'Doctorat', 'Grau'])
# ]

# # Table: alumnes_matriculats_universitat_sexe_grup_nacionalitat_universi
# [
#   (data_inici, start date. Value examples: ['2021-09-01', '2009-09-01', '2012-09-01', '2023-09-01', '2022-09-01'].),
#   (data_final, end date. Value examples: ['2021-06-30', '2009-06-30', '2012-06-30', '2023-06-30', '2022-06-30'].),
#   (fet_ca, describes the table, should not be in the SQL query. Value examples: ['Nombre d’alumnes matriculats a l’universitat'].),
#   (indicador_ca, describes the table, should not be in the SQL query. Value examples: ['Nombre d’alumnes matriculats a la universitat per sexe, grup de nacionalitat i universitat'].),
#   (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value examples: ['Univesitat, Matricules, Master, Grau, Doctorat'] ),
#   (municipi, municipality, it can only take the value of 'Barcelona'),
#   (unitat_ca, gives the type of the column 'value'. Value: ['Nombre'] means that 'value' is a number.),
#   (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: ['Persones'] which means persons.),
#   (valor, number of students per university, sex and nationality. Value examples: [26251, 1306, 10234, 19556, 9914].),
#   (universitat, university of studies. Value examples: ['Universitat de Barcelona (UB)', 'Universitat Politècnica de Catalunya (UPC)', 'Universitat Abat Oliba (UAO)', 'Universitat Autònoma de Barcelona (UAB)', 'Universitat Internacional de Catalunya (UIC)', 'Universitat Pompeu Fabra (UPF)']),
#   (sexe, sex. Value examples: ['Dona', 'Home']. 'Dona'=Woman; 'Home'=Man.),
#   (grup_de_nacionalitat, nationality. Value examples: ['Estranger', 'Espanya']. 'Estranger'=Foreigner; 'Espanya'=Spain)
# ]

# 【Question】
# How many doctoral students from Universitat Politècnica de Catalunya were women in 2019?

# 【Answer】
# ['poblacio_ocupada_assalariada': 'Not useful', 'canvis_domicili_titulacio_districte_baixa_districte_alta': 'Not useful', 'alumnes_universitaris_titulats_sexe_tipus_estudi_universitat': 'Useful', 'alumnes_matriculats_universitat_sexe_grup_nacionalitat_universi': 'Useful']

# **Most of the tables should be `Useful` unless there is a clear reason they are not relevant.**
# **Most of the tables should be `Useful` unless there is a clear reason they are not relevant.**
# **Most of the tables should be `Useful` unless there is a clear reason they are not relevant.**


# Avoid hallucinations: Avoid generating content that is not supported by the provided information, ensuring all claims, references, and data are based on the input.
# ==========

# Here is a new example, please start answering:

# 【DB_ID】 {db_id}
# 【Schema】
# {desc_str}
# 【Foreign keys】
# {fk_str}
# 【Question】
# {query}
# 【Evidence】
# {evidence}
# 【Answer】
# """

# selector_template1 = """
# As an experienced and professional database administrator, your task is to analyze a user question and a database schema to provide relevant information. The database schema consists of table descriptions, each containing multiple column descriptions. Your goal is to identify the relevant tables and columns based on the user question and evidence provided.
# Take a deep breath and approach this task methodically, step-by-step.

# The database comprises several tables, all adhering to a consistent structure. Each table serves to encode specific data relevant to the query. Here's a breakdown of the table structure:
# 1. Time enconding: `data_inici` and `data_final`.
# 2. Spatial encoding: Some tables feature spatial data encoded in columns `municipi`, `districte` and `barri`.
# 3. Fact description: The primary fact is described in the `valor` column.
# 4. Metadata columns: While some columns like `fet_ca`, `indicador_ca`, `tags_ca`, `unitat_ca`, and `unitat_mesura_ca` provide additional information about the content of the table, they are irrelevant for SQL queries and can be disregarded.
# 5. Main Dimensions: Other columns in each table represent main dimensions and should always be retained.

# [Instruction]:
# 1. You will be given up to ten tables from a database that have been determined most relevant with respect to the query. Discard any table schema that is not related to the user question and evidence.
# 2. Sort the columns in each relevant table in descending order of relevance and keep the top 5 columns.
# 3. Ensure that at least 2 tables are included in the final output JSON.
# 4. The output should be in JSON format.

# Requirements:
# 1. If a table has less than or equal to 7 columns, mark it as "keep_all".
# 2. If a table is completely irrelevant to the user question and evidence, mark it as "drop_all".
# 3. Prioritize the columns in each relevant table based on their relevance.

# Here is a typical example:

# ==========
# 【DB_ID】 dbeulalia
# 【Schema】
# # Table: Població_ocupada_assalariada
# [
#   (valor, Població ocupada assalariada. Value examples: [Decimal('576.8'), Decimal('614.4'), Decimal('619.4'), Decimal('553.2'), Decimal('100.2')])
#   (data_inici, start date. Value examples: ['2021-03-01', '2009-06-01', '2012-01-01', '2023-01-01', '2022-11-01'].),
#   (data_final, end date. Value examples: ['2021-03-31', '2009-06-30', '2012-12-31', '2023-12-31', '2022-11-30'].),
#   (fet_ca, describes the table, should not be in the SQL query. Value examples: ['Població ocupada assalariada'].),
#   (indicador_ca, describes the table, should not be in the SQL query. Value examples: ['Població ocupada assalariada'].),
#   (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value examples: ['epa'] ),
#   (municipi, municipality, it can only take the value of 'Barcelona'),
#   (unitat_ca, gives the type of the column 'value'. Value: ['Nombre'] means that 'value' is a number),
#   (unitat_mesura_ca. gives the units of measure of the column 'value'. Value: ['Milers the persones'] which means thousands of people, implying that 'value' must be multiplied by 1000),
# ]

# # Table: canvis_domicili_titulacio_districte_baixa_districte_alta
# [
#   (data_inici, start date. Value examples: ['2021-03-01', '2009-06-01', '2012-01-01', '2023-01-01', '2022-11-01'].),
#   (data_final, end date. Value examples: ['2021-03-31', '2009-06-30', '2012-12-31', '2023-12-31', '2022-11-30'].),
#   (fet_ca, describes the table, should not be in the SQL query. Value examples: ['Nombre de canvis de domicili'].),
#   (indicador_ca, also describes the table, should not be in the SQL query. Value examples: ['Canvis de domicili per titulació acadèmica i districte de baixa i districte d'alta'].),
#   (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value examples: ['padró municipal, migracions internes, mudances, estudis, educació'] ),
#   (municipi, municipality, it can only take the value of 'Barcelona'),
#   (districte, location in Barcelona. Value examples: ['Sant Martí', 'Gràcia', 'Eixample', 'Ciutat Vella', 'Sarrià-Sant Gervasi'].),
#   (unitat_ca, gives the type of the column 'value'. Value: ['Nombre'].),
#   (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: ['Canvis de domicili'].),
#   (valor, number of address changes. Value examples: [247, 1, 18, 33, 747].),
#   (districte_d_alta. Value examples: ['Sant Martí', 'Gràcia', 'Eixample', 'Ciutat Vella', 'Sarrià-Sant Gervasi'].),
#   (titulacio_academica. Value examples: ['Estudis universitaris, CFGS grau superior', 'Sense estudis', 'Estudis primaris, certificat d'escolaritat, EGB', 'Batxillerat elemental, graduat escolar, ESO, FPI', 'No consta'].)
# ]

# # Table: alumnes_universitaris_titulats_sexe_tipus_estudi_universitat
# [
#   (data_inici, start date. Value examples: ['2021-09-01', '2009-09-01', '2012-09-01', '2023-09-01', '2022-09-01'].),
#   (data_final, end date. Value examples: ['2021-06-30', '2009-06-30', '2012-06-30', '2023-06-30', '2022-06-30'].),
#   (fet_ca, describes the table, should not be in the SQL query. Value examples: ['Nombre d’alumnes universitaris titulats'].),
#   (indicador_ca, describes the table, should not be in the SQL query. Value examples: ['Nombre d’alumnes universitaris titulats per sexe, tipus d’estudi i universitat'].),
#   (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value examples: ['Univesitat, Matricules, Master, Grau, Doctorat'] ),
#   (municipi, municipality, it can only take the value of 'Barcelona'),
#   (unitat_ca, gives the type of the column 'value'. Value: ['Nombre']),
#   (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: ['Persones']),
#   (valor, number of students per study, university and sex. Value examples: [2874, 957, 109, 2383, 97].),
#   (universitat, university of studies. Value examples: ['Universitat de Barcelona (UB)', 'Universitat Politècnica de Catalunya (UPC)', 'Universitat Abat Oliba (UAO)', 'Universitat Autònoma de Barcelona (UAB)', 'Universitat Internacional de Catalunya (UIC)', 'Universitat Pompeu Fabra (UPF)']),
#   (sexe, sex. Value examples: ['Dona', 'Home'].),
#   (tipus_d_estudi. Value examples: ['Màster', 'Doctorat', 'Grau'])
# ]

# # Table: alumnes_matriculats_universitat_sexe_grup_nacionalitat_universi
# [
#   (data_inici, start date. Value examples: ['2021-09-01', '2009-09-01', '2012-09-01', '2023-09-01', '2022-09-01'].),
#   (data_final, end date. Value examples: ['2021-06-30', '2009-06-30', '2012-06-30', '2023-06-30', '2022-06-30'].),
#   (fet_ca, describes the table, should not be in the SQL query. Value examples: ['Nombre d’alumnes matriculats a l’universitat'].),
#   (indicador_ca, describes the table, should not be in the SQL query. Value examples: ['Nombre d’alumnes matriculats a la universitat per sexe, grup de nacionalitat i universitat'].),
#   (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value examples: ['Univesitat, Matricules, Master, Grau, Doctorat'] ),
#   (municipi, municipality, it can only take the value of 'Barcelona'),
#   (unitat_ca, gives the type of the column 'value'. Value: ['Nombre'] means that 'value' is a number.),
#   (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: ['Persones'] which means persons.),
#   (valor, number of students per university, sex and nationality. Value examples: [26251, 1306, 10234, 19556, 9914].),
#   (universitat, university of studies. Value examples: ['Universitat de Barcelona (UB)', 'Universitat Politècnica de Catalunya (UPC)', 'Universitat Abat Oliba (UAO)', 'Universitat Autònoma de Barcelona (UAB)', 'Universitat Internacional de Catalunya (UIC)', 'Universitat Pompeu Fabra (UPF)']),
#   (sexe, sex. Value examples: ['Dona', 'Home']. 'Dona'=Woman; 'Home'=Man.),
#   (grup_de_nacionalitat, nationality. Value examples: ['Estranger', 'Espanya']. 'Estranger'=Foreigner; 'Espanya'=Spain)
# ]

# 【Question】
# How many doctoral students from Universitat Politècnica de Catalunya were women in 2019?
# 【Answer】
# Useful

# 【Question】
# How many cars were there in Barcelona in 2015?
# 【Answer】
# Not useful

# ==========

# Here is a new example, please start answering:

# 【DB_ID】 {db_id}
# 【Schema】
# {desc_str}
# 【Foreign keys】
# {fk_str}
# 【Question】
# {query}
# 【Evidence】
# {evidence}
# 【Answer】
# """


subq_pattern = r"Sub question\s*\d+\s*:"


decompose_template_bird_mostratge = """
Given a 【Database schema】 description and the 【Question】, you need to use valid SQL and understand the database and knowledge for text-to-SQL generation.
When generating SQL, we should always consider constraints:
【Constraints】
- In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If [Value examples] of <column> has 'None' or None, use `JOIN <table>` or `WHERE <column> is NOT NULL` is better
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values
- If you must return "the second most ..." use LIMIT 1 OFFSET 1. If you are asked "The two most..." use LIMIT 2 
- `valor` gives the value that the fact table records. It's worth noting that to obtain the total number, one must sum the values in the `valor` column as SUM(valor).
- `data_inici` and `data_final` have string format 'YYYY-MM-DD'.
==========

【Database schema】
# Table: poblacio_per_sexe
[
    (valor. Value examples: [3941, 1617, 4190, 5502]),
    (data_inici, start date. Value examples: ['1997-01-01', '2023-01-01', '2018-01-01', '2016-01-01', '2015-01-01'].),
    (fet_ca, describes the table, should not be in the SQL query. Value: 'Població'),
    (indicador_ca, describes the table, should not be in the SQL query. Value: 'Població per sexe'),
    (data_final, end date. Value examples: ['1997-01-01', '2023-01-01', '2018-01-01', '2016-01-01', '2015-01-01'].),
    (municipi, municipality, it can only take the value of 'Barcelona'),
    (districte, location in Barcelona. Value examples: ['Sant Martí', 'Gràcia', 'Eixample', 'Ciutat Vella', 'Sarrià-Sant Gervasi'].),
    (barri, location in district of Barcelona. Value examples: ['Sant Andreu', 'el Poblenou', 'Hostafrancs', 'Sants - Badal', 'el Guinardó', 'Montblau'].),
    (area_estadistica_basica. Value examples: [140, 191, 84, 127]),
    (unitat_ca, gives the type of the column 'value'. Value: 'Nombre'), 
    (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: 'Persones'),
    (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value: 'padró municipal, persones, habitants, residents, ciutadans, gènere, sexe'),
    (sexe. Value examples: ['Dona', 'Home'].)
]
Given the table poblacio_per_sexe, you must select the latest data_final with 'GROUP BY data_final ORDER BY data_final LIMIT 1'

# Table: puntuacio_mitjana_de_la_satisfaccio_de_viure_a_la_ciutat
[
    (valor. Value examples: [7.344, 7.825, 7.5675]),
    (data_inici, start date. Value examples: ['2000-04-15', '2011-10-07', '2000-04-15', '2016-01-01', '2021-05-20'].),
    (fet_ca, describes the table, should not be in the SQL query. Value: 'Puntuació mitjana de la satisfacció de viure a la ciutat'),
    (indicador_ca, describes the table, should not be in the SQL query. Value: 'Puntuació mitjana de la satisfacció de viure a la ciutat'),
    (municipi, municipality, it can only take the value of 'Barcelona'),
    (districte, location in Barcelona. Value examples: ['Sant Martí', 'Gràcia', 'Eixample', 'Ciutat Vella', 'Sarrià-Sant Gervasi'].),
    (unitat_ca, gives the type of the column 'value'. Value: 'Mitjana'), 
    (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: 'Puntuació'),
    (data_final, end date. Value examples: ['2000-04-15', '2011-10-07', '2000-04-15', '2016-01-01', '2021-05-20'].)
]

# Table: poblacio
[
    (valor. Value examples: [3941, 4617, 37190, 45502]),
    (data_inici, start date. Value examples: ['1997-01-01', '2023-01-01', '2018-01-01', '2016-01-01', '2015-01-01'].),
    (fet_ca, describes the table, should not be in the SQL query. Value: 'Població'),
    (indicador_ca, describes the table, should not be in the SQL query. Value: 'Població'),
    (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value: 'residents, gent, ciutadans, total')
    (data_final, end date. Value examples: ['1997-01-01', '2023-01-01', '2018-01-01', '2016-01-01', '2015-01-01'].),
    (districte, location in Barcelona. Value examples: ['Sant Martí', 'Gràcia', 'Eixample', 'Ciutat Vella', 'Sarrià-Sant Gervasi'].),
    (barri, location in district of Barcelona. Value examples: ['Sant Andreu', 'el Poblenou', 'Hostafrancs', 'Sants - Badal', 'el Guinardó', 'Montblau'].),
    (unitat_ca, gives the type of the column 'value'. Value: 'Nombre'), 
    (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: 'Persones'),
    (municipi, municipality, it can only take the value of 'Barcelona'),
]
Given the table poblacio, you must select the latest data_final with 'GROUP BY data_final ORDER BY data_final LIMIT 1'


【Question】
Quants habitants hi havia a Barcelona el 2010?

SQL
```sql
SELECT sum(valor)
FROM poblacio
WHERE EXTRACT(YEAR FROM TO_DATE(data_inici,'YYYY-MM-DD')) = 2018
GROUP BY data_final
ORDER BY data_final DESC
LIMIT 1;
```

Question Solved.

==========

【Database schema】
# Table: nombre_de_motocicletes_per_marca
[
    (valor. Value examples: [1926, 8948, 27676, 12552]),
    (data_inici, start date. Value examples: ['2020-12-31', '2023-12-31', '2018-12-31', '2016-12-31', '2015-12-31'].),
    (fet_ca, describes the table, should not be in the SQL query. Value: 'Nombre de motocicletes'),
    (indicador_ca, describes the table, should not be in the SQL query. Value: 'Nombre de motocicletes per marca'),
    (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value: 'parc vehicles, cens vehicles, cotxe')
    (municipi, municipality, it can only take the value of 'Barcelona'),
    (unitat_ca, gives the type of the column 'value'. Value: 'Nombre'), 
    (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: 'Motocicletes'),
    (data_final, end date. Value examples: ['2020-12-31', '2023-12-31', '2018-12-31', '2016-12-31', '2015-12-31'].),
    (marca. Value examples: ['VESPA', 'SYM', 'KYMCO', 'PIAGGIO'])
]
Given the table poblacio, you must select the latest data_final with 'GROUP BY data_final ORDER BY data_final LIMIT 1'

# Table: nombre_de_motocicletes_per_cilindrada_cc_
[
    (valor. Value examples: [57, 88, 1175, 1552]),
    (data_inici, start date. Value examples: ['2020-12-31', '2023-12-31', '2018-12-31', '2016-12-31', '2015-12-31'].),
    (fet_ca, describes the table, should not be in the SQL query. Value: 'Nombre de motocicletes'),
    (indicador_ca, describes the table, should not be in the SQL query. Value: 'Nombre de motocicletes per cilindrada (cc)'),
    (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value: 'parc vehicles, cens vehicles, cotxe')
    (municipi, municipality, it can only take the value of 'Barcelona'),
    (districte, location in Barcelona. Value examples: ['Sant Martí', 'Gràcia', 'Eixample', 'Ciutat Vella', 'Sarrià-Sant Gervasi'].),
    (barri, location in district of Barcelona. Value examples: ['Sant Andreu', 'el Poblenou', 'Hostafrancs', 'Sants - Badal', 'el Guinardó', 'Montblau'].),
    (unitat_ca, gives the type of the column 'value'. Value: 'Nombre'), 
    (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: 'Motocicletes'),
    (data_final, end date. Value examples: ['2020-12-31', '2023-12-31', '2018-12-31', '2016-12-31', '2015-12-31'].),
    (cilindrada. Value examples: ['126-200 cc', '>1000 cc', '201-250 cc', '251-300 cc'])
]
Given the table poblacio, you must select the latest data_final with 'GROUP BY data_final ORDER BY data_final LIMIT 1'

# Table: nombre_de_turismes_per_marca
[
    (valor. Value examples: [38306, 4884, 10624, 28893]),
    (data_inici, start date. Value examples: ['2020-12-31', '2023-12-31', '2018-12-31', '2016-12-31', '2015-12-31'].),
    (fet_ca, describes the table, should not be in the SQL query. Value: 'Nombre de turismes'),
    (indicador_ca, describes the table, should not be in the SQL query. Value: 'Nombre de turismes per marca'),
    (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value: 'parc vehicles, cens vehicles, cotxe')
    (municipi, municipality, it can only take the value of 'Barcelona'),
    (unitat_ca, gives the type of the column 'value'. Value: 'Nombre'), 
    (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: 'Turismes'),
    (data_final, end date. Value examples: ['2020-12-31', '2023-12-31', '2018-12-31', '2016-12-31', '2015-12-31'].),
    (marca. Value examples: ['VOLVO', 'SKODA', 'RENAULT', 'SAAB'])
]
Given the table poblacio, you must select the latest data_final with 'GROUP BY data_final ORDER BY data_final LIMIT 1'

【Question】
Quina era la marca predominant de motocicletes el 2019?

SQL
```sql
SELECT marca
FROM nombre_de_motocicletes_per_marca
WHERE EXTRACT(YEAR FROM TO_DATE(data_inici,'YYYY-MM-DD')) = 2019
GROUP BY data_final, marca
ORDER BY sum(valor) DESC
LIMIT 1;
```

Question Solved.

==========


【Database schema】
{desc_str}
【Foreign keys】
{fk_str}
【Question】
{query}
【Evidence】
{evidence}

Avoid hallucinations: Avoid generating content that is not supported by the provided information, ensuring all claims, references, and data are based on the input.

Considering 【Constraints】 generate the SQL after thinking step by step:     
"""


decompose_template_bird_contatge = """
Given a 【Database schema】 description and the 【Question】, you need to use valid SQL and understand the database and knowledge for text-to-SQL generation.
When generating SQL, we should always consider constraints:
【Constraints】
- In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If [Value examples] of <column> has 'None' or None, use `JOIN <table>` or `WHERE <column> is NOT NULL` is better
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values
- If you must return "the second most ..." use LIMIT 1 OFFSET 1. If you are asked "The two most..." use LIMIT 2 
- `valor` gives the value that the fact table records. It's worth noting that to obtain the total number, one must sum the values in the `valor` column as SUM(valor).
- `data_inici` and `data_final` have string format 'YYYY-MM-DD'.
==========

【Database schema】
# Table: alumnes_universitaris_titulats_sexe_tipus_estudi_universitat
[
  (data_inici, start date. Value examples: ['2021-09-01', '2009-09-01', '2012-09-01', '2023-09-01', '2022-09-01'].),
  (data_final, end date. Value examples: ['2021-06-30', '2009-06-30', '2012-06-30', '2023-06-30', '2022-06-30'].),
  (fet_ca, describes the table, should not be in the SQL query. Value examples: ['Nombre d’alumnes universitaris titulats'].),
  (indicador_ca, describes the table, should not be in the SQL query. Value examples: ['Nombre d’alumnes universitaris titulats per sexe, tipus d’estudi i universitat'].),
  (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value examples: ['Univesitat, Matricules, Master, Grau, Doctorat'] ),
  (municipi, municipality, it can only take the value of 'Barcelona'),
  (unitat_ca, gives the type of the column 'value'. Value examples: ['Nombre']),
  (unitat_mesura_ca, gives the units of measure of the column 'value'. Value examples: ['Persones'].),
  (valor, Nombre d’alumnes universitaris titulats per sexe, tipus d’estudi i universitat. Value examples: [2874, 957, 109, 2383, 97].),
  (universitat, universitat. Value examples: ['Universitat de Barcelona (UB)', 'Universitat Politècnica de Catalunya (UPC)', 'Universitat Abat Oliba (UAO)', 'Universitat Autònoma de Barcelona (UAB)', 'Universitat Internacional de Catalunya (UIC)', 'Universitat Pompeu Fabra (UPF)']),
  (sexe, sexe. Value examples: ['Dona', 'Home'].),
  (tipus_d_estudi, tipus d'estudi. Value examples: ['Màster', 'Doctorat', 'Grau'])
]

# Table: alumnes_matriculats_universitat_sexe_grup_nacionalitat_universi
[
  (data_inici, start date. Value examples: ['2021-09-01', '2009-09-01', '2012-09-01', '2023-09-01', '2022-09-01'].),
  (data_final, end date. Value examples: ['2021-06-30', '2009-06-30', '2012-06-30', '2023-06-30', '2022-06-30'].),
  (unitat_ca, gives the type of the column 'value'. Value examples: ['Nombre'].),
  (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: ['Persones'].),
  (valor, Nombre d’alumnes universitaris titulats per sexe, tipus d’estudi i universitat. Value examples: [26251, 1306, 10234, 19556, 9914].),
  (universitat, university of studies. Value examples: ['Universitat de Barcelona (UB)', 'Universitat Politècnica de Catalunya (UPC)', 'Universitat Abat Oliba (UAO)', 'Universitat Autònoma de Barcelona (UAB)', 'Universitat Internacional de Catalunya (UIC)', 'Universitat Pompeu Fabra (UPF)']),
  (sexe, sex. Value examples: ['Dona', 'Home'].),
  (grup_de_nacionalitat, nacionalitat. Value examples: ['Estranger', 'Espanya'].)
]

【Question】
Quants estudiants de doctorat de la Universitat Politècnica de Catalunya són dones actualment?

Considering 【Constraints】 generate the SQL after thinking step by step:

Question: Quants estudiants de doctorat de la Universitat Politècnica de Catalunya eren dones l'any 2019?

```sql
SELECT sum(valor)
FROM alumnes_universitaris_titulats_sexe_tipus_estudi_universitat
WHERE universitat='Universitat Politècnica de Catalunya (UPC)' and sexe='Dona' and tipus_d_estudi='Doctorat' and EXTRACT(YEAR FROM TO_DATE(data_inici, "YYYY-MM-DD")) == 2019
```

Question Solved.

==========

【Database schema】
# Table: resultats_eleccions_congres_diputats_3_marc_1996_candidatura
[
  (data_inici, start date of the school year. Value examples: ['2021-09-01', '2009-09-01', '2012-09-01', '2023-09-01', '2022-09-01'].),
  (data_final, end date. Value examples: ['2021-06-30', '2009-06-30', '2012-06-30', '2023-06-30', '2022-06-30'].),
  (fet_ca, describes the table, should not be in the SQL query. Value examples: ['Resultats a les eleccions al Congrés de Diputats del 3 de març de 1996'].),
  (indicador_ca, also describes the table, should not be in the SQL query. Value examples: ['Resultats a les eleccions al Congrés de Diputats del 3 de març de 1996 per candidatura'].),
  (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value examples: ['generals, comicis, vots, vàlids, diputats'] ),
  (municipi, municipality, it can only take the value of 'Barcelona'),
  (districte, location in Barcelona. Value examples: ['Sant Martí', 'Gràcia', 'Eixample', 'Ciutat Vella', 'Sarrià-Sant Gervasi'].),
  (unitat_ca, gives the type of the column 'value'. Value: ['Nombre'] means that 'value' is a number.),
  (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: ['Vots'] which means votes.),
  (valor, number of votes by district and candidacy in the elections of 1996. Value examples: [10507, 159, 0, 7].),
  (candidatura, candidacy. Value examples: ['FEA', 'POR', 'PP', 'PSC'].)
]

# Table: dades_de_les_eleccions_al_congres_de_diputats
[
  (data_inici, start date. Value examples: ['2016-06-26', '2011-11-20', '2019-04-28', '2019-11-10'].),
  (data_final, end date. Value examples: ['2016-06-26', '2011-11-20', '2019-04-28', '2019-11-10'].),
  (fet_ca, describes the table, should not be in the SQL query. Value examples: ['Dades de les eleccions al Congrés de Diputats'].),
  (indicador_ca, also describes the table, should not be in the SQL query. Value examples: ['Dades de les eleccions al Congrés de Diputats'].),
  (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value examples: ['generals, comicis, vots, votants, cens, electors, abstenció, vàlids, diputats'] ),
  (municipi, municipality, it can only take the value of 'Barcelona'),
  (districte, location in Barcelona. Value examples: ['Sant Martí', 'Gràcia', 'Eixample', 'Ciutat Vella', 'Sarrià-Sant Gervasi'].),
  (barri, location in district of Barcelona. Value examples: ['Sant Andreu', 'el Poblenou', 'Hostafrancs', 'Sants - Badal', 'el Guinardó', 'Montblau'].),
  (unitat_ca, gives the type of the column 'value'. Value: ['Índex'] means that 'value' is an index),
  (unitat_mesura_ca. gives the units of measure of the column 'value'. Value: ['Persones'] which means numer of people.),
  (valor. represents the information that the table contains. Value examples: [13228, 36, 5808, 22040, 7190].),
  (tipus_de_recompte. Type of index. Value examples: ['Electors', 'Vots en blanc', 'Abstenció', 'Vots nuls'].)
]

【Question】
Diferència de vots entre el partit polític més votat i el segon a les eleccions del 1996.

In this case, it is easier to decompose the question into sub questions, considering 【Constraints】, and generate the SQL after thinking step by step:
Sub question 1: Quin va ser el partit més votat a les eleccions del 1996?
SQL
```sql
SELECT candidatura AS partit_mes_votat
    FROM resultats_eleccions_congres_diputats_3_marc_1996_candidatura
    GROUP BY candidatura
    ORDER BY SUM(valor) DESC
    LIMIT 1
```

Sub question 2: Quin va ser el segon partit més votat a les eleccions del 1996?

SQL
```sql
SELECT candidatura AS segon_partit_mes_votat
    FROM resultats_eleccions_congres_diputats_3_marc_1996_candidatura
    GROUP BY candidatura
    ORDER BY SUM(valor) DESC
    LIMIT 1 OFFSET 1
```

Sub question 3: Quina és la diferència de vots entre el partit polític més votat i el segon a les eleccions del 1996?

SQL
```sql
SELECT (SELECT SUM(valor) FROM resultats_eleccions_congres_diputats_3_marc_1996_candidatura WHERE candidatura = partido_mas_votado) -
    (SELECT SUM(valor) FROM resultats_eleccions_congres_diputats_3_marc_1996_candidatura WHERE candidatura = segundo_partido_mas_votado) AS diferencia_vots
FROM (
    SELECT candidatura AS partit_mes_votat
    FROM resultats_eleccions_congres_diputats_3_marc_1996_candidatura
    GROUP BY candidatura
    ORDER BY SUM(valor) DESC
    LIMIT 1
) AS partit1,
(
    SELECT candidatura AS segon_partit_mes_votat
    FROM resultats_eleccions_congres_diputats_3_marc_1996_candidatura
    GROUP BY candidatura
    ORDER BY SUM(valor) DESC
    LIMIT 1 OFFSET 1
) AS partit2;
```

Question Solved.

==========


【Database schema】
{desc_str}
【Foreign keys】
{fk_str}
【Question】
{query}
【Evidence】
{evidence}

Avoid hallucinations: Avoid generating content that is not supported by the provided information, ensuring all claims, references, and data are based on the input.

Considering 【Constraints】 generate the SQL after thinking step by step:
"""




refiner_template = """
【Instruction】
When executing SQL below, some errors occurred, please fix up SQL based on query and database info.
Solve the task step by step if you need to. Using SQL format in the code block, and indicate script type in the code block.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
【Constraints】

- Make sure that the columns you are referring to exist and are part of the table.
- Make sure that when filtering by a value, it is one of the Value Examples.
- EXTRACT(YEAR FROM TO_DATE(data_inici, 'YYYY-MM-DD')) in order to extract month or year of date
- In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If [Value examples] of <column> has 'None' or None, use `JOIN <table>` or `WHERE <column> is NOT NULL` is better
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values

【Query】
-- {query}
【Evidence】
{evidence}
【Database info】
{desc_str}
【Foreign keys】
{fk_str}
【old SQL】
```sql
{sql}
```
【SQLite error】 
{sqlite_error}
【Exception class】
{exception_class}

Now please fixup old SQL and generate new SQL again.

Avoid hallucinations: Avoid generating content that is not supported by the provided information, ensuring all claims, references, and data are based on the input.
【correct SQL】
"""

refiner_template_mostratge = """
【Instruction】
When executing SQL below, some errors occurred, please fix up SQL based on query and database info.
Solve the task step by step if you need to. Using SQL format in the code block, and indicate script type in the code block.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
【Constraints】

- Make sure that the columns you are refering to exist and are part of the table.
- Make sure that when filtering by a value, it is one of the Value Examples.
- EXTRACT(YEAR FROM TO_DATE(data_inici, 'YYYY-MM-DD')) in order to extract month or year of date
- In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If [Value examples] of <column> has 'None' or None, use `JOIN <table>` or `WHERE <column> is NOT NULL` is better
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values


Here is a typical example:

==========

Given a 【Database schema】 description and the 【Question】, you need to use valid SQL and understand the database and knowledge for text-to-SQL generation.
When generating SQL, we should always consider constraints:
【Constraints】
- In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If [Value examples] of <column> has 'None' or None, use `JOIN <table>` or `WHERE <column> is NOT NULL` is better
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values
- If you must return "the second most ..." use LIMIT 1 OFFSET 1. If you are asked "The two most..." use LIMIT 2 
- `valor` gives the value that the fact table records. It's worth noting that to obtain the total number, one must sum the values in the `valor` column as SUM(valor).
- `data_inici` and `data_final` have string format 'YYYY-MM-DD'.
==========

【Database schema】
# Table: poblacio_per_sexe
[
    (valor. Value examples: [3941, 1617, 4190, 5502]),
    (data_inici, start date. Value examples: ['1997-01-01', '2023-01-01', '2018-01-01', '2016-01-01', '2015-01-01'].),
    (fet_ca, describes the table, should not be in the SQL query. Value: 'Població'),
    (indicador_ca, describes the table, should not be in the SQL query. Value: 'Població per sexe'),
    (data_final, end date. Value examples: ['1997-01-01', '2023-01-01', '2018-01-01', '2016-01-01', '2015-01-01'].),
    (municipi, municipality, it can only take the value of 'Barcelona'),
    (districte, location in Barcelona. Value examples: ['Sant Martí', 'Gràcia', 'Eixample', 'Ciutat Vella', 'Sarrià-Sant Gervasi'].),
    (barri, location in district of Barcelona. Value examples: ['Sant Andreu', 'el Poblenou', 'Hostafrancs', 'Sants - Badal', 'el Guinardó', 'Montblau'].),
    (area_estadistica_basica. Value examples: [140, 191, 84, 127]),
    (unitat_ca, gives the type of the column 'value'. Value: 'Nombre'), 
    (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: 'Persones'),
    (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value: 'padró municipal, persones, habitants, residents, ciutadans, gènere, sexe'),
    (sexe. Value examples: ['Dona', 'Home'].)
]
Given the table poblacio_per_sexe, you must select the latest data_final with 'GROUP BY data_final ORDER BY data_final LIMIT 1'

# Table: puntuacio_mitjana_de_la_satisfaccio_de_viure_a_la_ciutat
[
    (valor. Value examples: [7.344, 7.825, 7.5675]),
    (data_inici, start date. Value examples: ['2000-04-15', '2011-10-07', '2000-04-15', '2016-01-01', '2021-05-20'].),
    (fet_ca, describes the table, should not be in the SQL query. Value: 'Puntuació mitjana de la satisfacció de viure a la ciutat'),
    (indicador_ca, describes the table, should not be in the SQL query. Value: 'Puntuació mitjana de la satisfacció de viure a la ciutat'),
    (municipi, municipality, it can only take the value of 'Barcelona'),
    (districte, location in Barcelona. Value examples: ['Sant Martí', 'Gràcia', 'Eixample', 'Ciutat Vella', 'Sarrià-Sant Gervasi'].),
    (unitat_ca, gives the type of the column 'value'. Value: 'Mitjana'), 
    (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: 'Puntuació'),
    (data_final, end date. Value examples: ['2000-04-15', '2011-10-07', '2000-04-15', '2016-01-01', '2021-05-20'].)
]

# Table: poblacio
[
    (valor. Value examples: [3941, 4617, 37190, 45502]),
    (data_inici, start date. Value examples: ['1997-01-01', '2023-01-01', '2018-01-01', '2016-01-01', '2015-01-01'].),
    (fet_ca, describes the table, should not be in the SQL query. Value: 'Població'),
    (indicador_ca, describes the table, should not be in the SQL query. Value: 'Població'),
    (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value: 'residents, gent, ciutadans, total')
    (data_final, end date. Value examples: ['1997-01-01', '2023-01-01', '2018-01-01', '2016-01-01', '2015-01-01'].),
    (districte, location in Barcelona. Value examples: ['Sant Martí', 'Gràcia', 'Eixample', 'Ciutat Vella', 'Sarrià-Sant Gervasi'].),
    (barri, location in district of Barcelona. Value examples: ['Sant Andreu', 'el Poblenou', 'Hostafrancs', 'Sants - Badal', 'el Guinardó', 'Montblau'].),
    (unitat_ca, gives the type of the column 'value'. Value: 'Nombre'), 
    (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: 'Persones'),
    (municipi, municipality, it can only take the value of 'Barcelona'),
]
Given the table poblacio, you must select the latest data_final with 'GROUP BY data_final ORDER BY data_final LIMIT 1'


【Question】
Quants habitants hi havia a Barcelona el 2010?

SQL
```sql
SELECT sum(valor)
FROM poblacio
WHERE EXTRACT(YEAR FROM TO_DATE(data_inici,'YYYY-MM-DD')) = 2018
GROUP BY data_final
ORDER BY data_final DESC
LIMIT 1;
```

Question Solved.

==========

【Query】
-- {query}
【Evidence】
{evidence}
【Database info】
{desc_str}
【Foreign keys】
{fk_str}
【old SQL】
```sql
{sql}
```
【SQLite error】 
{sqlite_error}
【Exception class】
{exception_class}

Now please fixup old SQL and generate new SQL again.

Avoid hallucinations: Avoid generating content that is not supported by the provided information, ensuring all claims, references, and data are based on the input.
【correct SQL】
"""

refiner_template_contatge = """
【Instruction】
When executing SQL below, some errors occurred, please fix up SQL based on query and database info.
Solve the task step by step if you need to. Using SQL format in the code block, and indicate script type in the code block.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
【Constraints】

- Make sure that the columns you are refering to exist and are part of the table.
- Make sure that when filtering by a value, it is one of the Value Examples.
- Remember that
- In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If [Value examples] of <column> has 'None' or None, use `JOIN <table>` or `WHERE <column> is NOT NULL` is better
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values


Here is a typical example:

==========
【Database schema】
# Table: alumnes_universitaris_titulats_sexe_tipus_estudi_universitat
[
  (data_inici, start date. Value examples: ['2021-09-01', '2009-09-01', '2012-09-01', '2023-09-01', '2022-09-01'].),
  (data_final, end date. Value examples: ['2021-06-30', '2009-06-30', '2012-06-30', '2023-06-30', '2022-06-30'].),
  (fet_ca, describes the table, should not be in the SQL query. Value examples: ['Nombre d’alumnes universitaris titulats'].),
  (indicador_ca, describes the table, should not be in the SQL query. Value examples: ['Nombre d’alumnes universitaris titulats per sexe, tipus d’estudi i universitat'].),
  (tags_ca, relevant words related to the topic of the table, should not be in the SQL. Value examples: ['Univesitat, Matricules, Master, Grau, Doctorat'] ),
  (municipi, municipality, it can only take the value of 'Barcelona'),
  (unitat_ca, gives the type of the column 'value'. Value examples: ['Nombre']),
  (unitat_mesura_ca, gives the units of measure of the column 'value'. Value examples: ['Persones'].),
  (valor, Nombre d’alumnes universitaris titulats per sexe, tipus d’estudi i universitat. Value examples: [2874, 957, 109, 2383, 97].),
  (universitat, universitat. Value examples: ['Universitat de Barcelona (UB)', 'Universitat Politècnica de Catalunya (UPC)', 'Universitat Abat Oliba (UAO)', 'Universitat Autònoma de Barcelona (UAB)', 'Universitat Internacional de Catalunya (UIC)', 'Universitat Pompeu Fabra (UPF)']),
  (sexe, sexe. Value examples: ['Dona', 'Home'].),
  (tipus_d_estudi, tipus d'estudi. Value examples: ['Màster', 'Doctorat', 'Grau'])
]

# Table: alumnes_matriculats_universitat_sexe_grup_nacionalitat_universi
[
  (data_inici, start date. Value examples: ['2021-09-01', '2009-09-01', '2012-09-01', '2023-09-01', '2022-09-01'].),
  (data_final, end date. Value examples: ['2021-06-30', '2009-06-30', '2012-06-30', '2023-06-30', '2022-06-30'].),
  (unitat_ca, gives the type of the column 'value'. Value examples: ['Nombre'].),
  (unitat_mesura_ca, gives the units of measure of the column 'value'. Value: ['Persones'].),
  (valor, Nombre d’alumnes universitaris titulats per sexe, tipus d’estudi i universitat. Value examples: [26251, 1306, 10234, 19556, 9914].),
  (universitat, university of studies. Value examples: ['Universitat de Barcelona (UB)', 'Universitat Politècnica de Catalunya (UPC)', 'Universitat Abat Oliba (UAO)', 'Universitat Autònoma de Barcelona (UAB)', 'Universitat Internacional de Catalunya (UIC)', 'Universitat Pompeu Fabra (UPF)']),
  (sexe, sex. Value examples: ['Dona', 'Home'].),
  (grup_de_nacionalitat, nacionalitat. Value examples: ['Estranger', 'Espanya'].)
]

【Question】
Quants estudiants de doctorat de la Universitat Politècnica de Catalunya són dones actualment?

Considering 【Constraints】 generate the SQL after thinking step by step:

Question: Quants estudiants de doctorat de la Universitat Politècnica de Catalunya eren dones l'any 2019?

```sql
SELECT sum(valor)
FROM alumnes_universitaris_titulats_sexe_tipus_estudi_universitat
WHERE universitat='Universitat Politècnica de Catalunya (UPC)' and sexe='Dona' and tipus_d_estudi='Doctorat' and EXTRACT(YEAR FROM TO_DATE(data_inici, "YYYY-MM-DD")) == 2019
```

Question Solved.

==========

【Query】
-- {query}
【Evidence】
{evidence}
【Database info】
{desc_str}
【Foreign keys】
{fk_str}
【old SQL】
```sql
{sql}
```
【SQL error】 
{sqlite_error}
【Exception class】
{exception_class}

Now please fixup old SQL and generate new SQL again.

Avoid hallucinations: Avoid generating content that is not supported by the provided information, ensuring all claims, references, and data are based on the input.

【correct SQL】
"""



# decompose_template_spider = """
# Given a 【Database schema】 description, and the 【Question】, you need to use valid SQLite and understand the database, and then generate the corresponding SQL.

# ==========

# 【Database schema】
# # Table: stadium
# [
#   (Stadium_ID, stadium id. Value examples: [1, 2, 3, 4, 5, 6].),
#   (Location, location. Value examples: ['Stirling Albion', 'Raith Rovers', "Queen's Park", 'Peterhead', 'East Fife', 'Brechin City'].),
#   (Name, name. Value examples: ["Stark's Park", 'Somerset Park', 'Recreation Park', 'Hampden Park', 'Glebe Park', 'Gayfield Park'].),
#   (Capacity, capacity. Value examples: [52500, 11998, 10104, 4125, 4000, 3960].),
#   (Highest, highest. Value examples: [4812, 2363, 1980, 1763, 1125, 1057].),
#   (Lowest, lowest. Value examples: [1294, 1057, 533, 466, 411, 404].),
#   (Average, average. Value examples: [2106, 1477, 864, 730, 642, 638].)
# ]
# # Table: concert
# [
#   (concert_ID, concert id. Value examples: [1, 2, 3, 4, 5, 6].),
#   (concert_Name, concert name. Value examples: ['Week 1', 'Week 2', 'Super bootcamp', 'Home Visits', 'Auditions'].),
#   (Theme, theme. Value examples: ['Wide Awake', 'Party All Night', 'Happy Tonight', 'Free choice 2', 'Free choice', 'Bleeding Love'].),
#   (Stadium_ID, stadium id. Value examples: ['2', '9', '7', '10', '1'].),
#   (Year, year. Value examples: ['2015', '2014'].)
# ]
# 【Foreign keys】
# concert.`Stadium_ID` = stadium.`Stadium_ID`
# 【Question】
# Show the stadium name and the number of concerts in each stadium.

# SQL
# ```sql
# SELECT T1.`Name`, COUNT(*) FROM stadium AS T1 JOIN concert AS T2 ON T1.`Stadium_ID` = T2.`Stadium_ID` GROUP BY T1.`Stadium_ID`
# ```

# Question Solved.

# ==========

# 【Database schema】
# # Table: singer
# [
#   (Singer_ID, singer id. Value examples: [1, 2].),
#   (Name, name. Value examples: ['Tribal King', 'Timbaland'].),
#   (Country, country. Value examples: ['France', 'United States', 'Netherlands'].),
#   (Song_Name, song name. Value examples: ['You', 'Sun', 'Love', 'Hey Oh'].),
#   (Song_release_year, song release year. Value examples: ['2016', '2014'].),
#   (Age, age. Value examples: [52, 43].)
# ]
# # Table: concert
# [
#   (concert_ID, concert id. Value examples: [1, 2].),
#   (concert_Name, concert name. Value examples: ['Super bootcamp', 'Home Visits', 'Auditions'].),
#   (Theme, theme. Value examples: ['Wide Awake', 'Party All Night'].),
#   (Stadium_ID, stadium id. Value examples: ['2', '9'].),
#   (Year, year. Value examples: ['2015', '2014'].)
# ]
# # Table: singer_in_concert
# [
#   (concert_ID, concert id. Value examples: [1, 2].),
#   (Singer_ID, singer id. Value examples: ['3', '6'].)
# ]
# 【Foreign keys】
# singer_in_concert.`Singer_ID` = singer.`Singer_ID`
# singer_in_concert.`concert_ID` = concert.`concert_ID`
# 【Question】
# Show the name and the release year of the song by the youngest singer.


# SQL
# ```sql
# SELECT `Song_Name`, `Song_release_year` FROM singer WHERE Age = (SELECT MIN(Age) FROM singer)
# ```

# Question Solved.

# ==========

# 【Database schema】
# {desc_str}
# 【Foreign keys】
# {fk_str}
# 【Question】
# {query}

# SQL

# """


# oneshot_template_1 = """
# Given a 【Database schema】 description, a knowledge 【Evidence】 and the 【Question】, you need to use valid SQLite and understand the database and knowledge, and then decompose the question into subquestions for text-to-SQL generation.
# When generating SQL, we should always consider constraints:
# 【Constraints】
# - In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
# - In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
# - If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
# - If [Value examples] of <column> has 'None' or None, use `JOIN <table>` or `WHERE <column> is NOT NULL` is better
# - If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values

# ==========

# 【Database schema】
# # Table: frpm
# [
#   (CDSCode, CDSCode. Value examples: ['01100170109835', '01100170112607'].),
#   (Charter School (Y/N), Charter School (Y/N). Value examples: [1, 0, None]. And 0: N;. 1: Y),
#   (Enrollment (Ages 5-17), Enrollment (Ages 5-17). Value examples: [5271.0, 4734.0, 4718.0].),
#   (Free Meal Count (Ages 5-17), Free Meal Count (Ages 5-17). Value examples: [3864.0, 2637.0, 2573.0]. And eligible free rate = Free Meal Count / Enrollment)
# ]
# # Table: satscores
# [
#   (cds, California Department Schools. Value examples: ['10101080000000', '10101080109991'].),
#   (sname, school name. Value examples: ['None', 'Middle College High', 'John F. Kennedy High', 'Independence High', 'Foothill High'].),
#   (NumTstTakr, Number of Test Takers in this school. Value examples: [24305, 4942, 1, 0, 280]. And number of test takers in each school),
#   (AvgScrMath, average scores in Math. Value examples: [699, 698, 289, None, 492]. And average scores in Math),
#   (NumGE1500, Number of Test Takers Whose Total SAT Scores Are Greater or Equal to 1500. Value examples: [5837, 2125, 0, None, 191]. And Number of Test Takers Whose Total SAT Scores Are Greater or Equal to 1500. And commonsense evidence: Excellence Rate = NumGE1500 / NumTstTakr)
# ]
# 【Foreign keys】
# frpm.`CDSCode` = satscores.`cds`
# 【Question】
# List school names of charter schools with an SAT excellence rate over the average.
# 【Evidence】
# Charter schools refers to `Charter School (Y/N)` = 1 in the table frpm; Excellence rate = NumGE1500 / NumTstTakr


# Decompose the question into sub questions, considering 【Constraints】, and generate the SQL after thinking step by step:
# Sub question 1: Get the average value of SAT excellence rate of charter schools.
# SQL
# ```sql
# SELECT AVG(CAST(T2.`NumGE1500` AS REAL) / T2.`NumTstTakr`)
#     FROM frpm AS T1
#     INNER JOIN satscores AS T2
#     ON T1.`CDSCode` = T2.`cds`
#     WHERE T1.`Charter School (Y/N)` = 1
# ```

# Sub question 2: List out school names of charter schools with an SAT excellence rate over the average.
# SQL
# ```sql
# SELECT T2.`sname`
#   FROM frpm AS T1
#   INNER JOIN satscores AS T2
#   ON T1.`CDSCode` = T2.`cds`
#   WHERE T2.`sname` IS NOT NULL
#   AND T1.`Charter School (Y/N)` = 1
#   AND CAST(T2.`NumGE1500` AS REAL) / T2.`NumTstTakr` > (
#     SELECT AVG(CAST(T4.`NumGE1500` AS REAL) / T4.`NumTstTakr`)
#     FROM frpm AS T3
#     INNER JOIN satscores AS T4
#     ON T3.`CDSCode` = T4.`cds`
#     WHERE T3.`Charter School (Y/N)` = 1
#   )
# ```

# Question Solved.

# ==========

# 【Database schema】
# {desc_str}
# 【Foreign keys】
# {fk_str}
# 【Question】
# {query}
# 【Evidence】
# {evidence}

# Decompose the question into sub questions, considering 【Constraints】, and generate the SQL after thinking step by step:
# """



# oneshot_template_2 = """
# Given a 【Database schema】 description, a knowledge 【Evidence】 and the 【Question】, you need to use valid SQLite and understand the database and knowledge, and then decompose the question into subquestions for text-to-SQL generation.
# When generating SQL, we should always consider constraints:
# 【Constraints】
# - In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
# - In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
# - If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
# - If [Value examples] of <column> has 'None' or None, use `JOIN <table>` or `WHERE <column> is NOT NULL` is better
# - If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values

# ==========

# 【Database schema】
# # Table: account
# [
#   (account_id, the id of the account. Value examples: [11382, 11362, 2, 1, 2367].),
#   (district_id, location of branch. Value examples: [77, 76, 2, 1, 39].),
#   (frequency, frequency of the acount. Value examples: ['POPLATEK MESICNE', 'POPLATEK TYDNE', 'POPLATEK PO OBRATU'].),
#   (date, the creation date of the account. Value examples: ['1997-12-29', '1997-12-28'].)
# ]
# # Table: client
# [
#   (client_id, the unique number. Value examples: [13998, 13971, 2, 1, 2839].),
#   (gender, gender. Value examples: ['M', 'F']. And F：female . M：male ),
#   (birth_date, birth date. Value examples: ['1987-09-27', '1986-08-13'].),
#   (district_id, location of branch. Value examples: [77, 76, 2, 1, 39].)
# ]
# # Table: district
# [
#   (district_id, location of branch. Value examples: [77, 76, 2, 1, 39].),
#   (A4, number of inhabitants . Value examples: ['95907', '95616', '94812'].),
#   (A11, average salary. Value examples: [12541, 11277, 8114, 8110, 8814].)
# ]
# 【Foreign keys】
# account.`district_id` = district.`district_id`
# client.`district_id` = district.`district_id`
# 【Question】
# What is the gender of the youngest client who opened account in the lowest average salary branch?
# 【Evidence】
# Later birthdate refers to younger age; A11 refers to average salary

# Decompose the question into sub questions, considering 【Constraints】, and generate the SQL after thinking step by step:
# Sub question 1: What is the district_id of the branch with the lowest average salary?
# SQL
# ```sql
# SELECT `district_id`
#   FROM district
#   ORDER BY `A11` ASC
#   LIMIT 1
# ```

# Sub question 2: What is the youngest client who opened account in the lowest average salary branch?
# SQL
# ```sql
# SELECT T1.`client_id`
#   FROM client AS T1
#   INNER JOIN district AS T2
#   ON T1.`district_id` = T2.`district_id`
#   ORDER BY T2.`A11` ASC, T1.`birth_date` DESC 
#   LIMIT 1
# ```

# Sub question 3: What is the gender of the youngest client who opened account in the lowest average salary branch?
# SQL
# ```sql
# SELECT T1.`gender`
#   FROM client AS T1
#   INNER JOIN district AS T2
#   ON T1.`district_id` = T2.`district_id`
#   ORDER BY T2.`A11` ASC, T1.`birth_date` DESC 
#   LIMIT 1 
# ```
# Question Solved.

# ==========

# 【Database schema】
# {desc_str}
# 【Foreign keys】
# {fk_str}
# 【Question】
# {query}
# 【Evidence】
# {evidence}

# Decompose the question into sub questions, considering 【Constraints】, and generate the SQL after thinking step by step:
# """


# zeroshot_template = """
# Given a 【Database schema】 description, a knowledge 【Evidence】 and the 【Question】, you need to use valid SQLite and understand the database and knowledge, and then generate SQL.
# You can write answer in script blocks, and indicate script type in it, like this:
# ```sql
# SELECT column_a
# FROM table_b
# ```
# When generating SQL, we should always consider constraints:
# 【Constraints】
# - In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
# - In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
# - If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
# - If [Value examples] of <column> has 'None' or None, use `JOIN <table>` or `WHERE <column> is NOT NULL` is better
# - If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values

# Now let's start!

# 【Database schema】
# {desc_str}
# 【Foreign keys】
# {fk_str}
# 【Question】
# {query}
# 【Evidence】
# {evidence}
# 【Answer】
# """


baseline_template = """
Given a 【Database schema】 description, a knowledge 【Evidence】 and the 【Question】, you need to use valid SQLite and understand the database and knowledge, and then generate SQL.
You can write answer in script blocks, and indicate script type in it, like this:
```sql
SELECT column_a
FROM table_b
```

【Database schema】
{desc_str}
【Question】
{query}
【Evidence】
{evidence}
【Answer】
"""
