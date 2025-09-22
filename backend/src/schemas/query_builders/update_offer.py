from collections.abc import Iterable, Mapping, Generator
from types import NoneType
from typing import Any
import json

from src.schemas.filters.filter_schemas import BaseFilter


class CreateTempTable(BaseFilter):
    def __init__(self,
                 data: Iterable[Mapping[str, Any]]):
        self.data = data

    def __call__(self, query):
        type_python_postgresql_dict = {
            int: 'INT',
            dict: 'JSONB',
            float: 'DOUBLE PRECISION',
            bool: 'BOOLEAN',
            str: 'VARCHAR',
            NoneType: 'VARCHAR',
        }
        double_prec_attrs = {
            'self_length', 'self_width', 'self_weight', 'self_weight', 'volume',
            'seller_discount', 'old_discount', 'attractive_price_threshold',
            'moderately_attractive_price_threshold',
        }
        query_create = query

        query_create += "CREATE TEMP TABLE IF NOT EXISTS temp_updates (\n\t"

        for row in self.data:
            for key, value in row.items():
                if key == 'search_words':
                    value = ''
                if key == 'price_index':
                    query_create += f"{key} VARCHAR,\n\t"
                elif key == 'group_sellers_amount' or key == 'business_id':
                    query_create += f"{key} INTEGER,\n\t"
                elif key in double_prec_attrs:
                    query_create += f"{key} DOUBLE PRECISION,\n\t"
                else:
                    query_create += f"{key} {type_python_postgresql_dict[type(value)] if key != 'vendor_code' else 'BIGINT'},\n\t"
            break

        query = query_create[:-3] + '\n);'
        return query

class InsertTempTable:
    def __init__(self,
                 data: list[Mapping[str, Any]]):
        self.data = data

    def __call__(self, query: str, chunk_size: int = 500) -> Generator[tuple[str, dict[str, Any]], None, None]:
        data = self.data
        json_cols = {k for k, v in data[0].items() if isinstance(v, dict)}

        key_list = [key for key in data[0].keys()]

        columns_str = '("' + '", "'.join(key_list) + '")'
        query_first = (
            f"INSERT INTO temp_updates {columns_str}\nVALUES\n\t"
        )
        # Определяем количество чанков
        for i in range((len(data) // chunk_size) + 1):
            insert_data = {}
            query_second = ""
            # Разбиваем данные по чанкам для обхода ограничения на количество значений в одном запросе SQLAlchemy
            for j in range(chunk_size * i, min(len(data), chunk_size * (i + 1))):
                row_values = []
                for key in key_list:
                    val = data[j][key]
                    if key in json_cols and val is not None:
                        val = json.dumps(val, ensure_ascii=False)
                    insert_data[f'{key}_{j}'] = val
                    placeholder = f'CAST(:{key}_{j} AS JSONB)' if key in json_cols else f':{key}_{j}'
                    row_values.append(placeholder)
                row_str = '(' + ', '.join(row_values) + ')'
                query_second += f"{row_str},\n\t"
            if len(insert_data) == 0:
                return
            query_insert: str = query_first + query_second[:-3] + ';'

            yield query_insert, insert_data


class UpdateOfferWithTempTable(BaseFilter):
    def __init__(self,
                 columns: Iterable[str],
                 synced_columns: Iterable[str]):
        self.columns = columns
        self.synced_columns = synced_columns

    def __call__(self, query):
        for column in self.columns:
            if column in self.synced_columns:
                query += f"""{column} = CASE
                WHEN offers.synchronization = true THEN offers.{column}
                ELSE temp_updates.{column}
                END,\n\t"""
            else:
                query += f"{column} = temp_updates.{column},\n\t"
        query = query[:-3] + '\nFROM temp_updates\nWHERE offers.sku=temp_updates.sku AND offers.market=temp_updates.market AND offers.name_of_shop = temp_updates.name_of_shop;'
        return query
