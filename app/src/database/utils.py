# TODO проверить как работает с пустым результатом
async def row_to_dict(row) -> dict:
    return dict(row._mapping)


# TODO проверить как работает с пустым результатом
async def row_list_to_dict_list(row_list) -> list[dict]:
    dict_list: list[dict] = []
    for row in row_list:
        dict_list.append(dict(row._mapping))
    return dict_list


async def add_to_list(request) -> list[dict]:
    data = []
    for row in request:
        data.append(row._asdict())
    return data

