from cmath import nan
from collections.abc import Iterable, Mapping
from types import NoneType
from typing import Any


from src.schemas.filters.filter_schemas import BaseFilter


class CreateTempTable(BaseFilter):
    def __init__(self,
                 data: Iterable[Mapping[str, Any]],
                 updated_columns: Iterable[str]):
        self.updated_columns = updated_columns
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
                if key in self.updated_columns:
                    query_create += f"{key} {_type_python_postgresql_dict[type(value)] if key != 'vendor_code' else 'BIGINT'},\n\t"
            break

        query = query_create[:-3] + '\n);'
        return query

class InsertTempTable(BaseFilter):
    def __init__(self,
                 data: Iterable[Mapping[str, Any]],
                 updated_columns: Iterable[str]):
        self.updated_columns = updated_columns
        self.data = data

    def __call__(self, query):
        i = 0
        key_list = []
        query_second = ""
        for row in self.data:
            row_list = []
            for key, value in row.items():
                if key in self.updated_columns:
                    if i == 0:
                        key_list.append(key)
                    if key == 'vendor_code':
                        row_list.append(str(int(value)))
                    else:
                        row_list.append(str(value))
            if len(row_list) > 0:
                query_second += f"({str(row_list)[1:-1]}),\n\t"
            if i == 1:
                break
            i += 1

        columns_str = str(key_list)[1:-1].replace("\'", f"\"")
        query_first = f"INSERT INTO temp_updates ({columns_str})\nVALUES\n\t"

        query = query_first + query_second[:-3] + ';'
        return query

class UpdateOfferWithTempTable(BaseFilter):
    def __init__(self,
                 updating_columns: Iterable[str]):
        self.updating_columns = updating_columns

    def __call__(self, query):
        for column in self.updating_columns:
            query += f"{column} = temp_updates.{column},\n\t"
        query = query[:-3] + f'\nFROM temp_updates\nWHERE offers.sku=temp_updates.sku AND offers.market=temp_updates.market AND offers.name_of_shop = temp_updates.name_of_shop;'
        return query
