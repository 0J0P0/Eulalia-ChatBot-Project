# -*- coding: utf-8 -*-
from core.utils import parse_json, parse_sql_from_string, add_prefix, load_json_file, extract_world_info, is_email, is_valid_date_column, extract_table_type

import sys
sys.path.insert(1, '/dades/eulalia/Eulalia-Project/BackEnd/DataBase')

from chroma import relevant_docs


LLM_API_FUC = None
# try import core.api, if error then import core.llm
    
try:
    from core import api
    LLM_API_FUC = api.safe_call_llm
    print(f"Use func from core.api in agents.py")
except:
    from core import llm
    LLM_API_FUC = llm.safe_call_llm
    print(f"Use func from core.llm in agents.py")

from core.const import *
from typing import List
from copy import deepcopy

import sqlite3
import psycopg2
import time
import abc
import sys
import os
import glob
import pandas as pd
from tqdm import tqdm, trange
from pprint import pprint
import pdb
import tiktoken



class BaseAgent(metaclass=abc.ABCMeta):
    def __init__(self):
        pass

    @abc.abstractmethod
    def talk(self, message: dict):
        pass


class Selector(BaseAgent):
    """
    Get database description and if need, extract relative tables & columns
    """
    name = SELECTOR_NAME
    description = "Get database description and if need, extract relative tables & columns"

    def __init__(self, data_path: str, tables_json_path: str, model_name: str, dataset_name:str, lazy: bool = False, without_selector: bool = False):
        super().__init__()
        self.data_path = data_path.strip('/').strip('\\')
        self.tables_json_path = tables_json_path
        self.model_name = model_name
        self.dataset_name = dataset_name
        self.db2infos = {}  # summary of db (stay in the memory during generating prompt)
        self.db2dbjsons = {} # store all db to tables.json dict by tables_json_path
        self.init_db2jsons()
        if not lazy:
            self._load_all_db_info()
        self._message = {}
        self.without_selector = without_selector
    
    def init_db2jsons(self):
        if not os.path.exists(self.tables_json_path):
            raise FileNotFoundError(f"tables.json not found in {self.tables_json_path}")
        data = load_json_file(self.tables_json_path)
        for item in data:
            db_id = item['db_id']
            
            table_names = item['table_names']
            # 统计表格数量
            item['table_count'] = len(table_names)
            
            column_count_lst = [0] * len(table_names)
            # print(len(column_count_lst))
            for tb_idx, col in item['column_names']:
                if tb_idx >= 0:
                    column_count_lst[tb_idx-1] += 1
            # 最大列名数量
            item['max_column_count'] = max(column_count_lst)
            item['total_column_count'] = sum(column_count_lst)
            item['avg_column_count'] = sum(column_count_lst) // len(table_names)
            
            # print()
            # print(f"db_id: {db_id}")
            # print(f"table_count: {item['table_count']}")
            # print(f"max_column_count: {item['max_column_count']}")
            # print(f"total_column_count: {item['total_column_count']}")
            # print(f"avg_column_count: {item['avg_column_count']}")
            # time.sleep(0.2)
            self.db2dbjsons[db_id] = item
    
    
    def _get_column_attributes(self, cursor, table):
        # # 查询表格的列属性信息
        # cursor.execute(f"PRAGMA table_info(`{table}`)")
        cursor.execute("""
            SELECT *
            FROM information_schema.columns
            WHERE table_name = %s
        """, (table,))
        columns = cursor.fetchall()
        # print(columns)
        # 构建列属性信息的字典列表
        columns_info = []
        column_names = []
        column_types = []
        primary_keys = []
        for column in columns:
            column_names.append(column[3])
            column_types.append(column[7])
            # is_pk = bool(column[5])
            # if is_pk:
            #     primary_keys.append(column[3])
            column_info = {
                'name': column[3],  # 列名
                'type': column[7],  # 数据类型
                'not_null': bool(column[6]),  # 是否允许为空
                'primary_key': False  # 是否为主键
            }
            columns_info.append(column_info)
        """
        table: satscores
        [{'name': 'cds', 'not_null': True, 'primary_key': True, 'type': 'TEXT'},
        {'name': 'rtype', 'not_null': True, 'primary_key': False, 'type': 'TEXT'},
        {'name': 'sname', 'not_null': False, 'primary_key': False, 'type': 'TEXT'},
        {'name': 'dname', 'not_null': False, 'primary_key': False, 'type': 'TEXT'},
        {'name': 'cname', 'not_null': False, 'primary_key': False, 'type': 'TEXT'},
        {'name': 'enroll12','not_null': True, 'primary_key': False, 'type': 'INTEGER'},
        ...
        """
        # print(column_names)
        # haurem de canviar indicador_ca a tags_ca
        # primary_keys = list(column_names[: column_names.index('data_inici') +1]) + list(column_names[column_names.index('indicador_ca')+1 : column_names.index('unitat_ca')]) + list(column_names[column_names.index('valor')+1:])
        # for dictionary in columns_info:
        #     if dictionary["name"] in primary_keys:
        #         dictionary["primary_key"] = True
        
        # print("\n\n\n")
        # print(column_names)
        return column_names, column_types

    
    def _get_unique_column_values_str(self, cursor, table, column_names, column_types, 
                                      json_column_names, is_key_column_lst):

        col_to_values_str_lst = []
        col_to_values_str_dict = {}

        # key_col_list = [json_column_names[i] for i, flag in enumerate(is_key_column_lst) if flag]
        # key_col_list = []
        len_column_names = len(column_names)

        for idx, column_name in enumerate(column_names):
            # 查询每列的 distinct value, 从指定的表中选择指定列的值，并按照该列的值进行分组。然后按照每个分组中的记录数量进行降序排序。
            # print(f"In _get_unique_column_values_str, processing column: {idx}/{len_column_names} col_name: {column_name} of table: {table}", flush=True)

            # skip pk and fk
            # if column_name in key_col_list:
            #     continue
            
            lower_column_name: str = column_name.lower()
            # if lower_column_name ends with [id, email, url], just use empty str
            if lower_column_name.endswith('id') or \
                lower_column_name.endswith('email') or \
                lower_column_name.endswith('url'):
                values_str = ''
                col_to_values_str_dict[column_name] = values_str
                continue

            sql = f"SELECT {column_name} FROM {table} GROUP BY {column_name} ORDER BY COUNT(*) DESC"
            cursor.execute(sql)
            values = cursor.fetchall()
            values = [value[0] for value in values]

            values_str = ''
            # try to get value examples str, if exception, just use empty str
            try:
                values_str = self._get_value_examples_str(values, column_types[idx], column_name)
            except Exception as e:
                print(f"\nerror: get_value_examples_str failed, Exception:\n{e}\n")

            col_to_values_str_dict[column_name] = values_str


        # print(table)
        # print(json_column_names)
        # print(col_to_values_str_dict)
        # print("HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
        for k, column_name in enumerate(json_column_names):
            values_str = ''
            # print(f"column_name: {column_name}")
            # print(f"col_to_values_str_dict: {col_to_values_str_dict}")

            # is_key = is_key_column_lst[k]

            # pk or fk do not need value str

            if column_name in col_to_values_str_dict:
                values_str = col_to_values_str_dict[column_name]
            else:
                time.sleep(3)
                print(f"error: column_name: {column_name} not found in col_to_values_str_dict")
                exit()
            col_to_values_str_lst.append([column_name, values_str])
        
        return col_to_values_str_lst
    

    # 这个地方需要精细化处理
    def _get_value_examples_str(self, values: List[object], col_type: str, column_name: str):
        
        if not values:
            return ''
        if len(values) > 10 and col_type.upper() in ['INTEGER', 'REAL', 'NUMERIC', 'FLOAT', 'INT']:
            return values[:5]
        
        vals = []
        has_null = False
        for v in values:
            if v is None:
                has_null = True
            else:
                tmp_v = str(v).strip()
                if tmp_v == '':
                    continue
                else:
                    vals.append(v)
        if not vals:
            return ''
        
        # drop meaningless values
        if col_type.upper() in ['TEXT', 'VARCHAR']:
            new_values = []
            
            for v in vals:
                if not isinstance(v, str):
                    
                    new_values.append(v)
                else:
                    if self.dataset_name == 'spider':
                        v = v.strip()
                    if v == '': # exclude empty string
                        continue
                    elif ('https://' in v) or ('http://' in v): # exclude url
                        return ''
                    elif is_email(v): # exclude email
                        return ''
                    else:
                        new_values.append(v)
            vals = new_values
            tmp_vals = [len(str(a)) for a in vals]
            if not tmp_vals:
                return ''
            max_len = max(tmp_vals)
            if max_len > 50:
                return ''
        
        if not vals:
            return ''
        
        # vals = vals[:6]
        if column_name in ["data_inici", "data_final"] or col_type.upper() in ['INTEGER', 'REAL', 'NUMERIC', 'FLOAT', 'INT']:
            vals = vals[:4]

        if has_null:
            vals.insert(0, None)
        
        val_str = str(vals)
        return val_str
    
    def _load_single_db_info(self, db_id: str) -> dict:
        table2coldescription = {} # Dict {table_name: [(column_name, full_column_name, column_description), ...]}
        table2primary_keys = {} # DIct {table_name: [primary_key_column_name,...]}
        
        table_foreign_keys = {} # Dict {table_name: [(from_col, to_table, to_col), ...]}
        table_unique_column_values = {} # Dict {table_name: [(column_name, examples_values_str)]}

        db_dict = self.db2dbjsons[db_id]

        # todo: gather all pk and fk id list
        important_key_id_lst = []
        keys = db_dict['primary_keys'] + db_dict['foreign_keys']
        for col_id in keys:
            if isinstance(col_id, list):
                important_key_id_lst.extend(col_id)
            else:
                important_key_id_lst.append(col_id)


        # db_path = f"{self.data_path}/{db_id}/{db_id}.sqlite"
        
        conn = psycopg2.connect(database="dbeulalia", user="postgres", password="password", host="localhost", port="5432", client_encoding="utf8")
        
        cursor = conn.cursor()

        # conn = sqlite3.connect(db_path)
        # conn.text_factory = lambda b: b.decode(errors="ignore")  # avoid gbk/utf8 error, copied from sql-eval.exec_eval

        # todo: AQUÍ ES PODRIA CANVIAR LA LLISTA I PASSAR-LI LES DEL CHROMA, ENTENC
        table_names_original_lst = db_dict['table_names_original']
        ## print("------------------------------")
        ## print("------------------------------")
        ## print("------------------------------")
        ## print(table_names_original_lst)
        ## print("------------------------------")
        ## print("------------------------------")
        ## print("------------------------------")

        # print(table_names_original_lst)    
        # table_names_original_lst = relevant_docs(self._message["query"])
        # table_names_original_lst = [i.lower() for i in table_names_original_lst]
        table_names_original_lst = relevant_docs(self._message["query"], 10)
        for table_namename in table_names_original_lst:
            print(table_namename)
        
        # print("------------------------------")
        # print("------------------------------")
        # print("------------------------------")
        # print(table_names_original_lst)
        # print("------------------------------")
        # print("------------------------------")
        # print("------------------------------")

        # table_names_original_lst = ["edat_mediana_de_la_poblacio_per_comunitat_autonoma_de_naixement", "nombre_d_empreses_per_divisio_economica", "quota_total_eur_dels_carrecs_cadastrals", "nombre_de_families_ateses_per_caritas_diocesana_de_barcelona_pe", "variacio_interanual_de_la_renda_disponible_de_les_llars_trimest", "domicilis_pel_nombre_de_persones_de_18_a_64_anys", "nombre_de_persones_en_locals_ocupats_amb_dinamica_d_assentament", "variacio_mensual_de_l_index_de_preus_de_consum_ipc_", "edat_mediana_dels_canvis_de_domicili_per_sexe_i_districte_de_ba", "nombre_de_locals_per_divisio_economica_i_condicio_juridica"]
        # print("\n\n\n\n\n")
        # print(table_names_original_lst)    
        # exit()
        table_tbidx = dict(load_json_file("/dades/eulalia/Eulalia-Project/BackEnd/EulaliaGPT/MacSqlUtils/core/table_tbidx.json"))
        # print(table_tbidx)

        for idx, tb_name in enumerate(table_names_original_lst):
            # print(idx, tb_name)
            tb_idx = table_tbidx[tb_name]
            # print(tb_idx)
            # 遍历原始列名
            
            all_column_names_original_lst = db_dict['column_names_original']            
            all_column_names_full_lst = db_dict['column_names']
            
            col2dec_lst = []

            pure_column_names_original_lst = []
            is_key_column_lst = []
            for col_idx, (root_tb_idx, orig_col_name) in enumerate(all_column_names_original_lst):
                # print(col_idx, root_tb_idx, orig_col_name)
                if root_tb_idx != tb_idx:
                    continue
                # print("root_tb_idx", root_tb_idx)
                
                pure_column_names_original_lst.append(orig_col_name)
                if col_idx in important_key_id_lst:
                    is_key_column_lst.append(True)
                else:
                    is_key_column_lst.append(False)
                full_col_name: str = all_column_names_full_lst[col_idx][1]
                full_col_name = full_col_name.replace('_', ' ')
                cur_desc_obj = [orig_col_name, full_col_name, '']
                col2dec_lst.append(cur_desc_obj)
            table2coldescription[tb_name] = col2dec_lst

            table_foreign_keys[tb_name] = []
            table_unique_column_values[tb_name] = []
            table2primary_keys[tb_name] = []

            # column_names, column_types
            # todo: aquí és on agafa les dades de la BD
            
            # print("Pure column names original list", pure_column_names_original_lst)
            all_sqlite_column_names_lst, all_sqlite_column_types_lst = self._get_column_attributes(cursor, tb_name)
            col_to_values_str_lst = self._get_unique_column_values_str(cursor, tb_name, all_sqlite_column_names_lst, all_sqlite_column_types_lst, pure_column_names_original_lst, is_key_column_lst)

            table_unique_column_values[tb_name] = col_to_values_str_lst
            

        # table_foreign_keys 处理起来麻烦一些
        foreign_keys_lst = db_dict['foreign_keys'] # realment no hi ha FKs

        for from_col_idx, to_col_idx in foreign_keys_lst:
            from_col_name = all_column_names_original_lst[from_col_idx][1]
            from_tb_idx = all_column_names_original_lst[from_col_idx][0]
            from_tb_name = table_names_original_lst[from_tb_idx]

            to_col_name = all_column_names_original_lst[to_col_idx][1]
            to_tb_idx = all_column_names_original_lst[to_col_idx][0]
            to_tb_name = table_names_original_lst[to_tb_idx]

            table_foreign_keys[from_tb_name].append((from_col_name, to_tb_name, to_col_name))
        

        # table2primary_keys
        pk_list = db_dict['primary_keys']
        # print("HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        for tb_name in table_names_original_lst:
            tb_idx = table_tbidx[tb_name]
            pk_idx_lst = pk_list[tb_idx]   
            # print(pk_idx_lst)         
            for cur_pk_idx in pk_idx_lst:
                col_name = all_column_names_original_lst[cur_pk_idx][1]
                table2primary_keys[tb_name].append(col_name)
            
        # for pk_idx in db_dict['primary_keys']:
        #     # if pk_idx is int
        #     pk_idx_lst = []
        #     if isinstance(pk_idx, int):
        #         pk_idx_lst.append(pk_idx)
        #     elif isinstance(pk_idx, list):
        #         pk_idx_lst = pk_idx
        #     else:
        #         err_message = f"pk_idx: {pk_idx} is not int or list"
        #         print(err_message)
        #         raise Exception(err_message)
        #     for cur_pk_idx in pk_idx_lst:
        #         tb_idx = all_column_names_original_lst[cur_pk_idx][0]
        #         print(all_column_names_original_lst[cur_pk_idx])
        #         print(tb_idx)
        #         print(table_names_original_lst)
        #         col_name = all_column_names_original_lst[cur_pk_idx][1]
        #         tb_name = table_names_original_lst[tb_idx]
        #         table2primary_keys[tb_name].append(col_name)
        
        cursor.close()
        # print table_name and primary keys
        # for tb_name, pk_keys in table2primary_keys.items():
        #     print(f"table_name: {tb_name}; primary key: {pk_keys}")
        time.sleep(3)

        # wrap result and return
        result = {
            "desc_dict": table2coldescription,
            "value_dict": table_unique_column_values,
            "pk_dict": table2primary_keys,
            "fk_dict": table_foreign_keys
        }
        return result

    def _load_all_db_info(self):
        print("\nLoading all database info...", file=sys.stdout, flush=True)
        db_ids = [item for item in os.listdir(self.data_path)]
        for i in range(len(db_ids)):
            db_id = db_ids[i]
            db_info = self._load_single_db_info(db_id)
            self.db2infos[db_id] = db_info
    
    def _build_bird_table_schema_sqlite_str(self, table_name, new_columns_desc, new_columns_val):
        schema_desc_str = ''
        schema_desc_str += f"CREATE TABLE {table_name}\n"
        extracted_column_infos = []
        for (col_name, full_col_name, col_extra_desc), (_, col_values_str) in zip(new_columns_desc, new_columns_val):
            # district_id INTEGER PRIMARY KEY, -- location of branch
            col_line_text = ''
            col_extra_desc = 'And ' + str(col_extra_desc) if col_extra_desc != '' and str(col_extra_desc) != 'nan' else ''
            col_extra_desc = col_extra_desc[:100]
            col_line_text = ''
            col_line_text += f"  {col_name},  --"
            if full_col_name != '':
                full_col_name = full_col_name.strip()
                col_line_text += f" {full_col_name},"
            if col_values_str != '':
                col_line_text += f" Value examples: {col_values_str}."
            if col_extra_desc != '':
                col_line_text += f" {col_extra_desc}"
            extracted_column_infos.append(col_line_text)
        schema_desc_str += '{\n' + '\n'.join(extracted_column_infos) + '\n}' + '\n'
        return schema_desc_str
    
    
    def _build_bird_table_schema_list_str(self, table_name, new_columns_desc, new_columns_val, table_type=None):
        

        schema_desc_str = ''
        schema_desc_str += f"# Table: {table_name}\n"
        extracted_column_infos = []

        for (col_name, full_col_name, col_extra_desc), (_, col_values_str) in zip(new_columns_desc, new_columns_val):
            col_extra_desc = 'And ' + str(col_extra_desc) if col_extra_desc != '' and str(col_extra_desc) != 'nan' else ''
            col_extra_desc = col_extra_desc[:100]

            col_line_text = ''
            col_line_text += f'  ('
            col_line_text += f"{col_name},"

            if col_name == 'valor':
                col_line_text += " " + new_columns_val[4][1][2:-2] + "."
            elif col_name == 'data_inici':
                col_line_text += "start date."
            elif col_name == 'data_final':
                col_line_text += "end date."
            elif col_name in ['fet_ca', 'indicador_ca']:
                col_line_text += " describes the table, should not be in the SQL query."
            elif col_name == "tags_ca":
                col_line_text += " relevant words related to the topic of the table, should not be in the SQL."
            elif col_name == "municipi":
                col_line_text += " municipality, it can only take the value of 'Barcelona'."
            elif col_name == "unitat_ca":
                col_line_text += " gives the type of the column 'value'."
            elif col_name == "unitat_mesura_ca":
                col_line_text += " gives the units of measure of the column 'value'."
                
            elif full_col_name != '':
                full_col_name = full_col_name.strip()
                col_line_text += f" {full_col_name}."
            
            if col_name in ['unitat_ca', 'unitat_mesura_ca', 'tags_ca', 'fet_ca', 'indicador_ca']:
                col_line_text += f" Value: {col_values_str[1:-2]}'"
            elif col_values_str != '' and col_name != 'municipi':
                col_line_text += f" Value examples: {col_values_str}."
            
            if col_extra_desc != '':
                col_line_text += f" {col_extra_desc}"
            col_line_text += '),'
            extracted_column_infos.append(col_line_text)
        schema_desc_str += '[\n' + '\n'.join(extracted_column_infos).strip(',') + '\n]' + '\n'
        
        if table_type == "Mostratge":
            schema_desc_str += f"Given the table {table_name}, you must select the latest data_final with 'GROUP BY data_final ORDER BY data_final LIMIT 1'.\n\n"
        elif table_type == "Contatge_especial": # si les dades estan mensuals+anuals o diàries+mensual+anuals
            schema_desc_str += f"Given the table {table_name} you must filter or select a date by specifying the initial date 'date_inici' and the end date 'data_final'.\n\n"

        return schema_desc_str
    
    def _get_db_desc_str(self,
                         db_id: str,
                         extracted_schema: dict,
                         use_gold_schema: bool = False,
                         need_prune: bool = True) -> List[str]:
        """
        Add foreign keys, and value descriptions of focused columns.
        :param db_id: name of sqlite database
        :param extracted_schema: {table_name: "keep_all" or "drop_all" or ['col_a', 'col_b']}
        :return: Detailed columns info of db; foreign keys info of db
        """
        if self.db2infos.get(db_id, {}) == {}:  # lazy load
            self.db2infos[db_id] = self._load_single_db_info(db_id)
        db_info = self.db2infos[db_id]
        desc_info = db_info['desc_dict']  # table:str -> columns[(column_name, full_column_name, extra_column_desc): str]
        value_info = db_info['value_dict']  # table:str -> columns[(column_name, value_examples_str): str]
        pk_info = db_info['pk_dict']  # table:str -> primary keys[column_name: str]
        fk_info = db_info['fk_dict']  # table:str -> foreign keys[(column_name, to_table, to_column): str]
        tables_1, tables_2, tables_3 = desc_info.keys(), value_info.keys(), fk_info.keys()
        assert set(tables_1) == set(tables_2)
        assert set(tables_2) == set(tables_3)

        # print(f"desc_info: {desc_info}\n\n")

        # schema_desc_str = f"[db_id]: {db_id}\n"
        schema_desc_str = ''  # for concat
        db_fk_infos = []  # use list type for unique check in db

        # print(f"extracted_schema:\n")
        # pprint(extracted_schema)
        # print()

        table_types = {"Mostratge": 0, "Eleccions": 0, "Contatge": 0}
        
        print(f"db_id: {db_id}")
        # For selector recall and compression rate calculation
        chosen_db_schem_dict = {} # {table_name: ['col_a', 'col_b'], ..}
        for (table_name, columns_desc), (_, columns_val), (_, fk_info), (_, pk_info) in \
                zip(desc_info.items(), value_info.items(), fk_info.items(), pk_info.items()):
            
            if need_prune:
                table_decision = extracted_schema.get(table_name, '')
            else:
                table_decision = "keep_all"
                
            if table_decision == '' and use_gold_schema:
                continue

            # columns_desc = [(column_name, full_column_name, extra_column_desc): str]
            # columns_val = [(column_name, value_examples_str): str]
            # fk_info = [(column_name, to_table, to_column): str]
            # pk_info = [column_name: str]

            all_columns = [name for name, _, _ in columns_desc]
            primary_key_columns = [name for name in pk_info]
            foreign_key_columns = [name for name, _, _ in fk_info]

            important_keys = primary_key_columns + foreign_key_columns

            new_columns_desc = []
            new_columns_val = []

            print(f"table_name: {table_name}")
            if table_decision == "drop_all":
                new_columns_desc = deepcopy(columns_desc[:6])
                new_columns_val = deepcopy(columns_val[:6])
            elif table_decision == "keep_all" or table_decision == '':
                new_columns_desc = deepcopy(columns_desc)
                new_columns_val = deepcopy(columns_val)
            else:
                llm_chosen_columns = table_decision
                print(f"llm_chosen_columns: {llm_chosen_columns}")
                append_col_names = []
                for idx, col in enumerate(all_columns):
                    if col in important_keys:
                        new_columns_desc.append(columns_desc[idx])
                        new_columns_val.append(columns_val[idx])
                        append_col_names.append(col)
                    elif col in llm_chosen_columns:
                        new_columns_desc.append(columns_desc[idx])
                        new_columns_val.append(columns_val[idx])
                        append_col_names.append(col)
                    else:
                        pass
                
                # todo: check if len(new_columns_val) ≈ 6
                if len(all_columns) > 6 and len(new_columns_val) < 6:
                    for idx, col in enumerate(all_columns):
                        if len(append_col_names) >= 6:
                            break
                        if col not in append_col_names:
                            new_columns_desc.append(columns_desc[idx])
                            new_columns_val.append(columns_val[idx])
                            append_col_names.append(col)

            # 统计经过 Selector 筛选后的表格信息
            chosen_db_schem_dict[table_name] = [col_name for col_name, _, _ in new_columns_desc]
            
            # 1. Build schema part of prompt
            # schema_desc_str += self._build_bird_table_schema_sqlite_str(table_name, new_columns_desc, new_columns_val)
            table_type=extract_table_type(table_name) # CALCULAR TABLE TYP
            schema_desc_str += self._build_bird_table_schema_list_str(table_name, new_columns_desc, new_columns_val, table_type)
            
            if table_type=="Contatge_especial":
                table_type = "Contatge"
            
            table_types[table_type] += 1

            # 2. Build foreign key part of prompt
            for col_name, to_table, to_col in fk_info:
                from_table = table_name
                if '`' not in str(col_name):
                    col_name = f"`{col_name}`"
                if '`' not in str(to_col):
                    to_col = f"`{to_col}`"
                fk_link_str = f"{from_table}.{col_name} = {to_table}.{to_col}"
                if fk_link_str not in db_fk_infos:
                    db_fk_infos.append(fk_link_str)
        fk_desc_str = '\n'.join(db_fk_infos)
        schema_desc_str = schema_desc_str.strip()
        fk_desc_str = fk_desc_str.strip()
        
        # escollir quina prompt agafar --> Possible que s'hagi de mirar més al detall
        dataset_type = "Mostratge" if table_types["Mostratge"] + table_types["Eleccions"] > table_types["Contatge"] else "Contatge"
        print(table_types)
        print(dataset_type)
        
        return schema_desc_str, fk_desc_str, chosen_db_schem_dict, dataset_type

    def _is_need_prune(self, db_id: str, db_schema: str):
        # encoder = tiktoken.get_encoding("cl100k_base")
        # tokens = encoder.encode(db_schema)
        # return len(tokens) >= 25000
        return False
        db_dict = self.db2dbjsons[db_id]
        avg_column_count = db_dict['avg_column_count']
        total_column_count = db_dict['total_column_count']
        if avg_column_count <= 6 and total_column_count <= 30:
            return False
        else:
            return True

    def _prune(self,
               db_id: str,
               query: str,
               db_schema: str,
               db_fk: str,
               evidence: str = None,
               ) -> dict:
        
        db_schema2 = db_schema.split("Table: ")
        replies = []
        useful = False
        for i in range(1, len(db_schema2)):
            prompt = selector_template.format(db_id=db_id, query=query, evidence=evidence, desc_str=db_schema2[i], fk_str=db_fk) # afegir table names
            word_info = extract_world_info(self._message)
            reply = LLM_API_FUC(prompt, **word_info)
            print(reply)
            if "not useful" not in reply.lower():
                useful = True
                break
            replies.append(reply)

        # extracted_schema_dict = parse_json(reply)
        return useful
        # return extracted_schema_dict

    def talk(self, message: dict):
        """
        :param message: {"db_id": database_name,
                         "query": user_query,
                         "evidence": extra_info,
                         "extracted_schema": None if no preprocessed result found}
        :return: extracted database schema {"desc_str": extracted_db_schema, "fk_str": foreign_keys_of_db}
        """
        if message['send_to'] != self.name: return
        self._message = message
        db_id, ext_sch, query, evidence = message.get('db_id'), \
                                          message.get('extracted_schema', {}), \
                                          message.get('query'), \
                                          message.get('evidence')
        use_gold_schema = False
        if ext_sch:
            use_gold_schema = True
            
        db_schema, db_fk, chosen_db_schem_dict, dataset_type = self._get_db_desc_str(db_id=db_id, extracted_schema=ext_sch, use_gold_schema=use_gold_schema)
        
        need_prune = True
        if self.without_selector:
            need_prune = False
        # else:
        #     need_prune = self._is_need_prune(db_id, db_schema)

        if ext_sch == {} and need_prune:
            try:
                # raw_extracted_schema_dict = self._prune(db_id=db_id, query=query, db_schema=db_schema, db_fk=db_fk, evidence=evidence)
                useful = self._prune(db_id=db_id, query=query, db_schema=db_schema, db_fk=db_fk, evidence=evidence)

            except Exception as e:
                print(e)
                raw_extracted_schema_dict = {}
            
            if useful:
                print(f"query: {message['query']}\n")
                # db_schema_str, db_fk, chosen_db_schem_dict, dataset_type = self._get_db_desc_str(db_id=db_id, extracted_schema=raw_extracted_schema_dict)

                # message['extracted_schema'] = raw_extracted_schema_dict
                message['chosen_db_schem_dict'] = chosen_db_schem_dict
                message['desc_str'] = db_schema
                message['fk_str'] = db_fk
                message['pruned'] = True
                message['send_to'] = DECOMPOSER_NAME
                message['dataset_type'] = dataset_type
            else:
                message['chosen_db_schem_dict'] = chosen_db_schem_dict
                message['desc_str'] = db_schema
                message['fk_str'] = db_fk
                message['pruned'] = True
                message['pred'] = "The database does not have the necessary information to answer the query."
                message['send_to'] = SYSTEM_NAME
                message['dataset_type'] = dataset_type
                
            
        else:
            
            print(db_schema)
            # db_schema, db_fk, chosen_db_schem_dict, dataset_type = self._get_db_desc_str(db_id=db_id, extracted_schema=ext_sch, use_gold_schema=use_gold_schema, need_prune=False)

            message['chosen_db_schem_dict'] = chosen_db_schem_dict
            message['desc_str'] = db_schema
            message['fk_str'] = db_fk
            message['pruned'] = False
            message['send_to'] = DECOMPOSER_NAME
            message['dataset_type'] = dataset_type



class Decomposer(BaseAgent):
    """
    Decompose the question and solve them using CoT
    """
    name = DECOMPOSER_NAME
    description = "Decompose the question and solve them using CoT"

    def __init__(self, dataset_name):
        super().__init__()
        self.dataset_name = dataset_name
        self._message = {}

    def talk(self, message: dict):
        """
        :param self:
        :param message: {"query": user_query,
                        "evidence": extra_info,
                        "desc_str": description of db schema,
                        "fk_str": foreign keys of database}
        :return: decompose question into sub ones and solve them in generated SQL
        """
        if message['send_to'] != self.name: return
        self._message = message
        query, evidence, schema_info, fk_info = message.get('query'), \
                                                message.get('evidence'), \
                                                message.get('desc_str'), \
                                                message.get('fk_str')
        

        if self.dataset_name == 'bird':
            if self._message["dataset_type"] == "Contatge": # contatge
                decompose_template = decompose_template_bird_contatge
            else: # mostratge o eleccions
                decompose_template = decompose_template_bird_mostratge
            prompt = decompose_template.format(query=query, desc_str=schema_info, fk_str=fk_info, evidence=evidence)
        else:
            # default use spider template
            decompose_template = decompose_template_spider
            prompt = decompose_template.format(query=query, desc_str=schema_info, fk_str=fk_info)
        
        
        ## one shot decompose(first) # fixme
        # prompt = oneshot_template_2.format(query=query, evidence=evidence, desc_str=schema_info, fk_str=fk_info)
        word_info = extract_world_info(self._message)
        reply = LLM_API_FUC(prompt, **word_info).strip()
        
        res = ''
        qa_pairs = reply
        
        try:
            res = parse_sql_from_string(reply)
        except Exception as e:
            res = f'error: {str(e)}'
            print(res)
            time.sleep(1)
        
        ## Without decompose
        # prompt = zeroshot_template.format(query=query, evidence=evidence, desc_str=schema_info, fk_str=fk_info)
        # reply = LLM_API_FUC(prompt)
        # qa_pairs = []
        
        message['final_sql'] = res
        message['qa_pairs'] = qa_pairs
        message['fixed'] = False
        message['send_to'] = REFINER_NAME


class Refiner(BaseAgent):
    name = REFINER_NAME
    description = "Execute SQL and preform validation"

    def __init__(self, data_path: str, dataset_name: str):
        super().__init__()
        self.data_path = data_path  # path to all databases
        self.dataset_name = dataset_name
        self._message = {}

    def _execute_sql(self, sql: str, db_id: str) -> dict:
        # Get database connection
        # db_path = f"{self.data_path}/{db_id}/{db_id}.sqlite"
        # conn = sqlite3.connect(db_path)
        conn = psycopg2.connect(database="dbeulalia", user="postgres", password="password", host="localhost", port="5432", client_encoding="utf8")
        
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            return {
                "sql": str(sql),
                "data": result[:5],
                "postgresql_error": "",
                "exception_class": ""
            }
        except psycopg2.Error as er:
            return {
                "sql": str(sql),
                "sqlite_error": str(' '.join(er.pgcode)),
                "exception_class": str(er.__class__)
            }
        except Exception as e:
            return {
                "sql": str(sql),
                "sqlite_error": str(e),
                "exception_class": str(type(e).__name__)
            }

    def _is_need_refine(self, exec_result: dict):
        # spider exist dirty values, even gold sql execution result is None
    
        if self.dataset_name == 'spider':
            if 'data' not in exec_result:
                return True
            return False
        
        data = exec_result.get('data', None)
        if data is not None:
            if len(data) == 0:
                exec_result['postgresql_error'] = 'no data selected'
                return True
            for t in data:
                for n in t:
                     if n is None: 
                        exec_result['postgresql_error'] = 'exist None value, you can add `NOT NULL` in SQL'
                        return True
            return False
        else:
            return True

    def _refine(self,
               query: str,
               evidence:str,
               schema_info: str,
               fk_info: str,
               error_info: dict,
               type_taula_escollida: str = "no_type") -> dict:
        
        sql_arg = add_prefix(error_info.get('sql'))
        
        postgresql_error = error_info.get('postgresql_error')
        exception_class = error_info.get('exception_class')

        if type_taula_escollida == "no_type":
            prompt = refiner_template.format(query=query, evidence=evidence, desc_str=schema_info, \
                                       fk_str=fk_info, sql=sql_arg, sqlite_error=postgresql_error, \
                                        exception_class=exception_class)
        else:
            wrong_table_type = "You must select the latest data_final with 'GROUP BY data_final ORDER BY data_final LIMIT 1'.\n"
            prompt = refiner_template_mostratge.format(query=query, evidence=evidence, desc_str=schema_info, \
                                       fk_str=fk_info, sql=sql_arg, sqlite_error=wrong_table_type, \
                                        exception_class=wrong_table_type)            

        word_info = extract_world_info(self._message)
        reply = LLM_API_FUC(prompt, **word_info)
        res = parse_sql_from_string(reply)
        return res

    def talk(self, message: dict):
        """
        Execute SQL and preform validation
        :param message: {"query": user_query,
                        "evidence": extra_info,
                        "desc_str": description of db schema,
                        "fk_str": foreign keys of database,
                        "final_sql": generated SQL to be verified,
                        "db_id": database name to execute on}
        :return: execution result and if need, refine SQL according to error info
        """
        if message['send_to'] != self.name: return
        self._message = message
        db_id, old_sql, query, evidence, schema_info, fk_info = message.get('db_id'), \
                                                            message.get('pred', message.get('final_sql')), \
                                                            message.get('query'), \
                                                            message.get('evidence'), \
                                                            message.get('desc_str'), \
                                                            message.get('fk_str')
        # do not fix sql containing "error" string
        if 'error' in old_sql:
            message['try_times'] = message.get('try_times', 0) + 1
            message['pred'] = old_sql
            message['send_to'] = SYSTEM_NAME
            return
           
        try:
            taula_escollida = old_sql.split("\nFROM ")[1].split("\n")[0]
            type_taula_escollida = extract_table_type(taula_escollida)
            refine_table = type_taula_escollida != message.get("dataset_type")
            print(old_sql)
        except:
            print("There was a little error with the SQL.")
            print(old_sql)
            refine_table = False            
        
        
        if refine_table and type_taula_escollida == "Contatge":
            old_sql = old_sql.replace("\nGROUP BY data_final", "").replace("\nORDER BY data_final DESC\nLIMIT 1", "")
            refine_table = False

        # if tipus_de_recompte(message) 
        error_info = self._execute_sql(old_sql, db_id)
        
        if message.get('try_times', 0) + 1 == 1 and refine_table:
            
            new_sql = self._refine(query, evidence, schema_info, fk_info, error_info, type_taula_escollida)
            message['try_times'] = message.get('try_times', 0) + 1
            message['pred'] = old_sql.replace("count(valor)", "sum(valor)").replace("COUNT(valor)", "SUM(valor)").replace("count(*)", "sum(valor)").replace("COUNT(*)", "SUM(valor)")
            message['fixed'] = True            
            message['send_to'] = REFINER_NAME
            
        elif not self._is_need_refine(error_info):  # correct in one pass or refine success
            message['try_times'] = message.get('try_times', 0) + 1
            message['pred'] = old_sql.replace("count(valor)", "sum(valor)").replace("COUNT(valor)", "SUM(valor)").replace("count(*)", "sum(valor)").replace("COUNT(*)", "SUM(valor)")
            message['send_to'] = SYSTEM_NAME
        else:
            new_sql = self._refine(query, evidence, schema_info, fk_info, error_info)
            message['try_times'] = message.get('try_times', 0) + 1
            message['pred'] = new_sql.replace("count(valor)", "sum(valor)").replace("COUNT(valor)", "SUM(valor)").replace("count(*)", "sum(valor)").replace("COUNT(*)", "SUM(valor)")
            message['fixed'] = True
            message['send_to'] = REFINER_NAME
        return


if __name__ == "__main__":
    m = 0