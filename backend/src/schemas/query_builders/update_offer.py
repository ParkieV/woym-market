from collections.abc import Iterable, Mapping, Sequence, Generator
from types import NoneType
from typing import Any, overload

from src.schemas.filters.filter_schemas import BaseFilter


class CreateTempTable(BaseFilter):
    def __init__(self,
                 data: Iterable[Mapping[str, Any]]):
        self.data = data

    def __call__(self, query):
        _type_python_postgresql_dict = {
            int: 'INT',
            dict: 'DICT',
            float: 'DOUBLE PRECISION',
            bool: 'BOOLEAN',
            str: 'VARCHAR',
            NoneType: 'VARCHAR',
        }
        query_create = query

        query_create += "CREATE TEMP TABLE temp_updates (\n\t"

        for row in self.data:
            for key, value in row.items():
                if key == 'search_words':
                    value = ''

                if key == 'price_index':
                    query_create += f"{key} VARCHAR,\n\t"
                elif key == 'group_sellers_amount':
                    query_create += f"{key} INTEGER,\n\t"
                elif key == 'business_id':
                    query_create += f"{key} INTEGER,\n\t"
                elif key == 'self_length' or key == 'self_width':
                    query_create += f"{key} DOUBLE PRECISION,\n\t"
                else:
                    query_create += f"{key} {_type_python_postgresql_dict[type(value)] if key != 'vendor_code' else 'BIGINT'},\n\t"
            break

        query = query_create[:-3] + '\n);'
        return query

class InsertTempTable(BaseFilter):
    def __init__(self,
                 data: list[Mapping[str, Any]]):
        self.data = data

    def __call__(self, query: str) -> Generator[list[str], list[dict[str, Any]]]:
        data = self.data

        key_list = [key for key in data[0].keys()]

        columns_str = '("' + '", "'.join(key_list) + '")'
        query_first = f"INSERT INTO temp_updates {columns_str}\nVALUES\n\t"
        # Определяем количество чанков
        for i in range((len(data) // 950) + 1):
            insert_data = {}
            query_second = ""
            # Разбиваем данные по чанкам для обхода ограничения на количество значений в одном запросе SQLAlchemy
            for j in range(950 * i, min(len(data), 950 * (i + 1))):
                insert_data.update({f'{key}_{j}': data[j][key] for key in key_list})
                row_str = '(' + ', '.join([f':{column}_{j}' for column in key_list]) + ')'
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
        query = query[:-3] + f'\nFROM temp_updates\nWHERE offers.sku=temp_updates.sku AND offers.market=temp_updates.market AND offers.name_of_shop = temp_updates.name_of_shop;'
        return query
