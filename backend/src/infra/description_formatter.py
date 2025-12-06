import asyncio
from collections import deque
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


def html_to_md_linear(html: str) -> str:
    if html[0] == '\'' and html[-1] == '\'':
        html = html[1:-1]
    res = []
    i = 0
    n = len(html)

    list_stack = deque()
    counters = deque()

    def open_ul():
        list_stack.append("ul")
        counters.append(None)

    def open_ol():
        list_stack.append("ol")
        counters.append(1)

    def close_list():
        if list_stack:
            list_stack.pop()
            counters.pop()

    def open_li():
        if not list_stack:
            res.append("\n- ")
            return

        tag = list_stack.pop()
        counter = counters.pop()

        level = len(list_stack) + 1
        indent = "  " * (level - 1)

        if tag == "ul":
            prefix = "- "
        else:
            prefix = f"{counter}. "
            counter += 1

        res.append("\n" + indent + prefix)

        list_stack.append(tag)
        counters.append(counter)

    def br():
        res.append("\n")

    def p_open():
        res.append("\n\n")

    def p_close():
        res.append("\n\n")

    handlers_open = {
        "ul": open_ul,
        "ol": open_ol,
        "li": open_li,
        "br": br,
        "p": p_open,
    }

    handlers_close = {
        "ul": close_list,
        "ol": close_list,
        "p": p_close,
    }

    while i < n:
        if html[i] != '<':
            res.append(html[i])
            i += 1
            continue

        j = i + 1
        closing = False

        if j < n and html[j] == '/':
            closing = True
            j += 1

        start = j
        while j < n and html[j].isalnum():
            j += 1
        tag = html[start:j].lower()

        while j < n and html[j] != '>':
            j += 1
        i = j + 1

        if closing:
            h = handlers_close.get(tag)
            if h:
                h()
        else:
            h = handlers_open.get(tag)
            if h:
                h()

    return ''.join(res).strip()


async def sasat():
    print("Start")
    engine2 = create_async_engine(
        'postgresql+asyncpg://4jkEBoIe2dFve73:ruskys-nuzvok-puzFa2@localhost:5432/local_db'
    )
    engine1 = create_async_engine(
        'postgresql+asyncpg://hGjP58cDJH4GE6U:zapkAp-cerwen-9xiqfy@10.0.0.3:5432/woym_market_db'
    )

    session_maker1 = async_sessionmaker(engine1)

    async with session_maker1() as session1:
        result = await session1.execute(
            text('SELECT id, description FROM offers')
        )

        print("Start poehali")
        for row in result:
            await session1.execute(
                text(
                    'UPDATE offers SET description = :desc WHERE id = :id'
                ),
                {'desc': html_to_md_linear(row.description), 'id': row.id}
            )

        await session1.commit()


if __name__ == '__main__':
    asyncio.run(sasat())
