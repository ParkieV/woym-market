import asyncio
import random
from contextlib import asynccontextmanager

from fastapi import FastAPI, Path, Request


# ---------------------------------------------------------------------------
# State — 50 real products from SKRAB catalog, 10 warehouses from DB
# ---------------------------------------------------------------------------

WAREHOUSES = [
    {"id": 429, "name": "Tashkent 1"},
    {"id": 310, "name": "СЦ Псков"},
    {"id": 314, "name": "СЦ Самара"},
    {"id": 450, "name": "Ташкент 2"},
    {"id": 432, "name": "Коледино: Горючее"},
    {"id": 254, "name": "Котовск"},
    {"id": 255, "name": "Краснодар (Тихорецкая)"},
    {"id": 517, "name": "Нижний Тагил Восточное"},
    {"id": 433, "name": "Пенза"},
    {"id": 478, "name": "Пермь 4"},
]

PRODUCTS: dict[str, dict] = {
    "20841": {
        "nmID": 20841,
        "vendorCode": "20841",
        "title": "Пилки для лобзика (дерево/металл/пластик) SKRAB 20841",
        "description": "Пилки для электролобзика дерево-металл-пластик 3шт. SKRAB 20841 Технические характеристики Тип : универсальные ; Назначение : прямой рез ; Тип хвостовика : хвостовик Т ; Количество, шт : 3 ; Рабочая длина, мм : 74 ; Общая длина, мм : 100 ; Шаг : 1.1-1.5; 4; 3. Вес нетто, кг : 0.026 ; Алмазная : нет",
        "dimensions": {"length": 16.0, "width": 6.0, "height": 1.0, "weightBrutto": 0.026},
        "sizes": [{"skus": ["4750735208412"]}],
        "characteristics": [{"id": 88953, "value": 0.026}],
        "photos": [{"big": "https://images.wb.ru/big/new/20841.jpg"}],
        "price": 723.0,
        "discount": 0,
        "search_words": "пилки для электролобзика; пилки для электролобзика по дереву; пилка для лобзика; набор пилок для электролобзика",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20783": {
        "nmID": 20783,
        "vendorCode": "20783",
        "title": "Полотно по металлу, биметаллическая сталь HSS SKRAB 20783",
        "description": "Полотна по металлу 300мм 32TPI/S500 Bi-Metal 20783 от SKRAB. Биметаллическая конструкция полотна гарантирует долгий срок службы.",
        "dimensions": {"length": 32.0, "width": 1.0, "height": 1.0, "weightBrutto": 0.176},
        "sizes": [{"skus": ["4750735207835"]}],
        "characteristics": [{"id": 88953, "value": 0.176}],
        "photos": [{"big": "https://images.wb.ru/big/new/20783.jpg"}],
        "price": 2432.0,
        "discount": 0,
        "search_words": "полотно по металлу; полотна по металлу; полотно для лобзика; пилки по металлу",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20241": {
        "nmID": 20241,
        "vendorCode": "20241",
        "title": "Молоток 100г с фибер. ручкой оранж. SKRAB 20241",
        "description": "Инструмент создан с применением технологий ковки. Обладает бойком в виде квадрата. Рукоятка сделана из стеклопластика с функцией антискольжения.",
        "dimensions": {"length": 28.0, "width": 8.0, "height": 2.0, "weightBrutto": 0.237},
        "sizes": [{"skus": ["4750735202410"]}],
        "characteristics": [{"id": 88953, "value": 0.237}],
        "photos": [{"big": "https://images.wb.ru/big/new/20241.jpg"}],
        "price": 1096.0,
        "discount": 0,
        "search_words": "молоток; молоток строительный; молоток слесарный; молоток гвоздодер; молоток с фиберглассовой ручкой",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20347": {
        "nmID": 20347,
        "vendorCode": "20347",
        "title": "Топор 1650 гр фиберглассовая ручка SKRAB 20347",
        "description": "Топор 1650 гр фиберглассовая ручка SKRAB 20347. Лезвие топора выполнено из углеродистой стали методом ковки. Фиберглассовая ручка.",
        "dimensions": {"length": 103.0, "width": 23.0, "height": 4.0, "weightBrutto": 2.95},
        "sizes": [{"skus": ["4750735203479"]}],
        "characteristics": [{"id": 88953, "value": 2.95}],
        "photos": [{"big": "https://images.wb.ru/big/new/20347.jpg"}],
        "price": 8052.0,
        "discount": 0,
        "search_words": "топор; топор для дров; топор туристический; топор колун; топор кованый; топор для плотника; топор с фиберглассовой ручкой",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20771": {
        "nmID": 20771,
        "vendorCode": "20771",
        "title": "Полотно по металлу 150мм 10шт. MGH SKRAB 20771",
        "description": "Полотно по металлу 150мм 24TPI 10пр. SKRAB 20771. Длина 150 мм. Количество в наборе 10 шт.",
        "dimensions": {"length": 20.0, "width": 4.0, "height": 1.0, "weightBrutto": 0.03},
        "sizes": [{"skus": ["4750735207712"]}],
        "characteristics": [{"id": 88953, "value": 0.03}],
        "photos": [{"big": "https://images.wb.ru/big/new/20771.jpg"}],
        "price": 760.0,
        "discount": 0,
        "search_words": "пилки для лобзика; пилки для лобзика по металлу; полотно по металлу; полотно для лобзика",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20069": {
        "nmID": 20069,
        "vendorCode": "20069",
        "title": "Молоток-гвоздодер с фибер.ручкой оранж. 560г SKRAB 20069",
        "description": "Молоток-гвоздодер 560г с фиберглассовой оранжевой ручкой SKRAB. Головка молотка выполнена из закаленной высококачественной стали.",
        "dimensions": {"length": 34.0, "width": 14.0, "height": 3.0, "weightBrutto": 0.789},
        "sizes": [{"skus": ["4750735200690"]}],
        "characteristics": [{"id": 88953, "value": 0.789}],
        "photos": [{"big": "https://images.wb.ru/big/new/20069.jpg"}],
        "price": 1753.0,
        "discount": 0,
        "search_words": "молоток; молоток строительный; гвоздодер; молоток слесарный; молоток гвоздодер; молоток с фиберглассовой ручкой",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20256": {
        "nmID": 20256,
        "vendorCode": "20256",
        "title": "Кувалда 1250г с фибер. ручкой оранж. SKRAB 20256",
        "description": "Кувалда 1250г с фибер. ручкой оранж. SKRAB 20256. Инструмент из закалённой стали. Рукоятка сделана из стеклопластика с функцией антискольжения.",
        "dimensions": {"length": 26.0, "width": 10.0, "height": 4.0, "weightBrutto": 1.4},
        "sizes": [{"skus": ["4750735202564"]}],
        "characteristics": [{"id": 88953, "value": 1.4}],
        "photos": [{"big": "https://images.wb.ru/big/new/20256.jpg"}],
        "price": 1713.0,
        "discount": 0,
        "search_words": "кувалда",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20141": {
        "nmID": 20141,
        "vendorCode": "20141",
        "title": "Топор 600г с фибр.ручкой зелено-черный SKRAB 20141",
        "description": "Топор с фиберглассовой ручкой Skrab 20141 подходит для заготовки древесины и плотницких работ.",
        "dimensions": {"length": 35.0, "width": 15.0, "height": 2.0, "weightBrutto": 0.94},
        "sizes": [{"skus": ["4750735201413"]}],
        "characteristics": [{"id": 88953, "value": 0.94}],
        "photos": [{"big": "https://images.wb.ru/big/new/20141.jpg"}],
        "price": 1863.0,
        "discount": 0,
        "search_words": "топор; топор для дров; топор туристический; топор кованый; топор для плотника; топор с фиберглассовой ручкой",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20248": {
        "nmID": 20248,
        "vendorCode": "20248",
        "title": "Молоток 800г с фибер. ручкой оранж. SKRAB 20248",
        "description": "Инструмент создан с применением технологий ковки. Обладает бойком в виде квадрата. Рукоятка сделана из стеклопластика с функцией антискольжения.",
        "dimensions": {"length": 36.0, "width": 13.0, "height": 3.0, "weightBrutto": 1.057},
        "sizes": [{"skus": ["4750735202489"]}],
        "characteristics": [{"id": 88953, "value": 1.057}],
        "photos": [{"big": "https://images.wb.ru/big/new/20248.jpg"}],
        "price": 2024.0,
        "discount": 0,
        "search_words": "молоток; молоток строительный; молоток слесарный; молоток с фиберглассовой ручкой",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20784": {
        "nmID": 20784,
        "vendorCode": "20784",
        "title": 'Полотно по металлу 12"/300 мм 24 TPI, 10 штук SKRAB 20784',
        "description": "Полотно по металлу SKRAB 20784. Шаг зубьев 24 TPI. В комплекте 10 штук. Рабочая длина 300 мм.",
        "dimensions": {"length": 31.0, "width": 2.0, "height": 1.0, "weightBrutto": 0.15},
        "sizes": [{"skus": ["4750735207842"]}],
        "characteristics": [{"id": 88953, "value": 0.15}],
        "photos": [{"big": "https://images.wb.ru/big/new/20784.jpg"}],
        "price": 760.0,
        "discount": 0,
        "search_words": "пилки для лобзика; пилки для лобзика по металлу; полотно по металлу; полотно для лобзика",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20845": {
        "nmID": 20845,
        "vendorCode": "20845",
        "title": "Пилки для электролобзика по дереву/металлу 5 шт. SKRAB 20845",
        "description": "Набор полотен для электролобзика 5 шт. Skrab 20845 подходят как для прямого, так и фигурного реза по дереву, металлу и пластику.",
        "dimensions": {"length": 15.0, "width": 6.0, "height": 1.0, "weightBrutto": 0.038},
        "sizes": [{"skus": ["4750735208450"]}],
        "characteristics": [{"id": 88953, "value": 0.038}],
        "photos": [{"big": "https://images.wb.ru/big/new/20845.jpg"}],
        "price": 900.0,
        "discount": 0,
        "search_words": "пилки для электролобзика; пилки для электролобзика по дереву; пилка для лобзика; набор пилок для электролобзика",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20346": {
        "nmID": 20346,
        "vendorCode": "20346",
        "title": 'Топор-колун кованый Fiber 1000г 28" 720мм SKRAB 20346',
        "description": "Топор-колун кованый Fiber 1000г 28\"/720мм SKRAB 20346. Лезвие из углеродистой стали с тефлоновым покрытием PTFE. Рукоятка из стекловолокна.",
        "dimensions": {"length": 80.0, "width": 21.0, "height": 4.0, "weightBrutto": 1.81},
        "sizes": [{"skus": ["4750735203462"]}],
        "characteristics": [{"id": 88953, "value": 1.81}],
        "photos": [{"big": "https://images.wb.ru/big/new/20346.jpg"}],
        "price": 6470.0,
        "discount": 0,
        "search_words": "топор; топор для дров; топор колун; топор кованый; топор для плотника",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20525": {
        "nmID": 20525,
        "vendorCode": "20525",
        "title": "Ножовка по дереву 400мм каленый зуб GREEN SK5 SKRAB 20525",
        "description": "Ножовка SKRAB 20525 предназначена для столярных работ. Полотно длиной 40 см изготовлено из прочной японской стали SK-5.",
        "dimensions": {"length": 47.0, "width": 13.0, "height": 13.0, "weightBrutto": 0.35},
        "sizes": [{"skus": ["4750735205251"]}],
        "characteristics": [{"id": 88953, "value": 0.35}],
        "photos": [{"big": "https://images.wb.ru/big/new/20525.jpg"}],
        "price": 1927.0,
        "discount": 0,
        "search_words": "ножовка по дереву; ножовка; ножовка садовая; ножовка по дереву ручная; ножовки по дереву",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20086": {
        "nmID": 20086,
        "vendorCode": "20086",
        "title": "Молоток кровельщика с фибер.ручкой оранж.600г SKRAB 20086",
        "description": "Молоток кровельщика предназначен для выравнивания краев кровли. Выполнен из прочной инструментальной стали.",
        "dimensions": {"length": 34.0, "width": 17.0, "height": 3.0, "weightBrutto": 0.82},
        "sizes": [{"skus": ["4750735200867"]}],
        "characteristics": [{"id": 88953, "value": 0.82}],
        "photos": [{"big": "https://images.wb.ru/big/new/20086.jpg"}],
        "price": 1788.0,
        "discount": 0,
        "search_words": "молоток; молоток строительный; молоток кровельщика; молоток с фиберглассовой ручкой",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20526": {
        "nmID": 20526,
        "vendorCode": "20526",
        "title": "Ножовка по дереву 450мм каленый зуб GREEN SK5 SKRAB 20526",
        "description": "Ножовка SKRAB 20526 предназначена для столярных работ. Полотно длиной 45 см изготовлено из прочной японской стали SK-5.",
        "dimensions": {"length": 50.0, "width": 13.0, "height": 2.0, "weightBrutto": 0.5},
        "sizes": [{"skus": ["4750735205268"]}],
        "characteristics": [{"id": 88953, "value": 0.5}],
        "photos": [{"big": "https://images.wb.ru/big/new/20526.jpg"}],
        "price": 1537.0,
        "discount": 0,
        "search_words": "ножовка по дереву; ножовка; ножовка садовая; ножовка по дереву ручная; ножовки по дереву",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20863": {
        "nmID": 20863,
        "vendorCode": "20863",
        "title": "Полотно для сабельной пилы по газобетону 462 мм SKRAB 20863",
        "description": "Полотно по газобетону 462 х 47 х 2мм 20 TCT SKRAB 20863. Хвостовик универсальный. Для пиления газобетонных блоков и пористого кирпича.",
        "dimensions": {"length": 58.0, "width": 3.0, "height": 1.0, "weightBrutto": 0.2},
        "sizes": [{"skus": ["4750735208634"]}],
        "characteristics": [{"id": 88953, "value": 0.2}],
        "photos": [{"big": "https://images.wb.ru/big/new/20863.jpg"}],
        "price": 1753.0,
        "discount": 0,
        "search_words": "полотно для сабельной пилы; полотно для сабельной пилы по газобетону; полотна для сабельной пилы",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20781": {
        "nmID": 20781,
        "vendorCode": "20781",
        "title": "Полотно по металлу (10 шт; 300 мм; 18TPI/С300) SKRAB 20781",
        "description": "Полотно по металлу 300 мм С300 18TPI 10 шт. SKRAB 20781. Изготовлено из быстрорежущей стали. Шаг зубьев 18 TPI.",
        "dimensions": {"length": 31.0, "width": 1.0, "height": 1.0, "weightBrutto": 0.17},
        "sizes": [{"skus": ["4750735207811"]}],
        "characteristics": [{"id": 88953, "value": 0.17}],
        "photos": [{"big": "https://images.wb.ru/big/new/20781.jpg"}],
        "price": 1141.0,
        "discount": 0,
        "search_words": "пилки для лобзика; пилки для лобзика по металлу; полотно по металлу; полотно для лобзика",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20340": {
        "nmID": 20340,
        "vendorCode": "20340",
        "title": "Топор 440 гр фиберглассовая ручка SKRAB 20340",
        "description": "Топор туристический кованый 230 мм с фиберглассовой ручкой. Выполнен из высокоуглеродистой стали методом ковки с тефлоновым покрытием.",
        "dimensions": {"length": 30.0, "width": 17.0, "height": 2.0, "weightBrutto": 0.67},
        "sizes": [{"skus": ["4750735203400"]}],
        "characteristics": [{"id": 88953, "value": 0.67}],
        "photos": [{"big": "https://images.wb.ru/big/new/20340.jpg"}],
        "price": 3219.0,
        "discount": 0,
        "search_words": "топор; топор для дров; топор туристический; топор кованый; топор для плотника; топор с фиберглассовой ручкой",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20844": {
        "nmID": 20844,
        "vendorCode": "20844",
        "title": "Пилки для лобзика SKRAB Т-344 D п/дер Cr-V 2 шт SKRAB 20844",
        "description": "Пилки для лобзика SKRAB Т-344 D п/дер Cr-V 2 шт. Общая длина 125 мм, рабочая длина 100 мм. TPI 6. Тип хвостовика — Т.",
        "dimensions": {"length": 19.0, "width": 5.0, "height": 1.0, "weightBrutto": 0.022},
        "sizes": [{"skus": ["4750735208443"]}],
        "characteristics": [{"id": 88953, "value": 0.022}],
        "photos": [{"big": "https://images.wb.ru/big/new/20844.jpg"}],
        "price": 707.0,
        "discount": 0,
        "search_words": "пилки для электролобзика; пилки для электролобзика по дереву; пилка для лобзика; набор пилок для электролобзика",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20342": {
        "nmID": 20342,
        "vendorCode": "20342",
        "title": 'Топор кованый Fiber 820г 23,5" 610мм SKRAB 20342',
        "description": "Топор кованый Fiber 820г 23,5\"/610мм SKRAB 20342. Изготовлен из углеродистой стали методом ковки. Тефлоновое покрытие PTFE. Рукоятка из стекловолокна.",
        "dimensions": {"length": 67.0, "width": 20.0, "height": 3.0, "weightBrutto": 0.82},
        "sizes": [{"skus": ["4750735203424"]}],
        "characteristics": [{"id": 88953, "value": 0.82}],
        "photos": [{"big": "https://images.wb.ru/big/new/20342.jpg"}],
        "price": 5246.0,
        "discount": 0,
        "search_words": "топор; топор для дров; топор туристический; топор кованый; топор для плотника",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20501": {
        "nmID": 20501,
        "vendorCode": "20501",
        "title": "Ножовка по дереву SKRAB, с меняющимся углом 20501",
        "description": "Ножовка по дереву Skrab 20501. Сменное полотно можно устанавливать под 5-ю различными углами. Обрезиненная рукоятка.",
        "dimensions": {"length": 48.0, "width": 14.0, "height": 2.0, "weightBrutto": 0.49},
        "sizes": [{"skus": ["4750735205015"]}],
        "characteristics": [{"id": 88953, "value": 0.49}],
        "photos": [{"big": "https://images.wb.ru/big/new/20501.jpg"}],
        "price": 1719.0,
        "discount": 0,
        "search_words": "ножовка по дереву; ножовка; ножовка по дереву ручная; ножовки по дереву",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20862": {
        "nmID": 20862,
        "vendorCode": "20862",
        "title": "Полотно для сабельной пилы п/газобетону 14TСТ SKRAB 20862",
        "description": "Пилка для сабельной пилы по газобетону 320х47х2мм 14TCT Skrab 20862. HCS — высокоуглеродистая сталь. 14 зубьев с твердосплавными напайками.",
        "dimensions": {"length": 42.0, "width": 10.0, "height": 1.0, "weightBrutto": 0.21},
        "sizes": [{"skus": ["4750735208627"]}],
        "characteristics": [{"id": 88953, "value": 0.21}],
        "photos": [{"big": "https://images.wb.ru/big/new/20862.jpg"}],
        "price": 1502.0,
        "discount": 0,
        "search_words": "полотно для сабельной пилы; полотно для сабельной пилы по газобетону; полотна для сабельной пилы",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20860": {
        "nmID": 20860,
        "vendorCode": "20860",
        "title": "Полотно для сабельной пилы п/газобетону SKRAB 20860",
        "description": "HCS — высокоуглеродистая сталь. 13 зубьев с твердосплавными напайками (TCT). Универсальный хвостовик. Длина 215 мм.",
        "dimensions": {"length": 30.0, "width": 8.0, "height": 1.0, "weightBrutto": 0.07},
        "sizes": [{"skus": ["4750735208603"]}],
        "characteristics": [{"id": 88953, "value": 0.07}],
        "photos": [{"big": "https://images.wb.ru/big/new/20860.jpg"}],
        "price": 1156.0,
        "discount": 0,
        "search_words": "полотно для сабельной пилы; полотно для сабельной пилы по газобетону; полотна для сабельной пилы",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20075": {
        "nmID": 20075,
        "vendorCode": "20075",
        "title": "Молоток-гвоздодер Fiber 450 г. Сталь 40Cr SKRAB 20075",
        "description": "Молоток-гвоздодер Skrab 20075. Вес бойка 450 г. Изготовлен из высококачественной легированной стали GB 40CR.",
        "dimensions": {"length": 34.0, "width": 14.0, "height": 3.0, "weightBrutto": 0.6},
        "sizes": [{"skus": ["4750735200751"]}],
        "characteristics": [{"id": 88953, "value": 0.6}],
        "photos": [{"big": "https://images.wb.ru/big/new/20075.jpg"}],
        "price": 3285.0,
        "discount": 0,
        "search_words": "молоток; молоток строительный; гвоздодер; молоток слесарный; молоток гвоздодер; молоток с фиберглассовой ручкой",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20153": {
        "nmID": 20153,
        "vendorCode": "20153",
        "title": "Кувалда с защитой 1500г дер.ручка SKRAB 20153",
        "description": "Кувалда с защитой 1500г SKRAB 20153. Деревянная ручка защищена металлической защитой от излома. Обрезиненная ручка.",
        "dimensions": {"length": 27.0, "width": 10.0, "height": 4.0, "weightBrutto": 1.6},
        "sizes": [{"skus": ["4750735201536"]}],
        "characteristics": [{"id": 88953, "value": 1.6}],
        "photos": [{"big": "https://images.wb.ru/big/new/20153.jpg"}],
        "price": 1240.0,
        "discount": 0,
        "search_words": "кувалда",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20152": {
        "nmID": 20152,
        "vendorCode": "20152",
        "title": "Кувалда с защитой 1250г дер.ручка SKRAB 20152",
        "description": "Кувалда с защитой 1250г SKRAB 20152. Деревянная ручка кувалды защищена металлической защитой от излома.",
        "dimensions": {"length": 26.0, "width": 10.0, "height": 4.0, "weightBrutto": 1.3},
        "sizes": [{"skus": ["4750735201529"]}],
        "characteristics": [{"id": 88953, "value": 1.3}],
        "photos": [{"big": "https://images.wb.ru/big/new/20152.jpg"}],
        "price": 1227.0,
        "discount": 0,
        "search_words": "кувалда",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20149": {
        "nmID": 20149,
        "vendorCode": "20149",
        "title": "Топор-колун 2000г с фибр. ручкой удлиненый SKRAB 20149",
        "description": "Топор-колун SKRAB 20149. Удлиненная ручка из стеклопластика 800 мм. Антифрикционное покрытие. Обрезиненная ручка.",
        "dimensions": {"length": 85.0, "width": 20.0, "height": 4.0, "weightBrutto": 2.86},
        "sizes": [{"skus": ["4750735201499"]}],
        "characteristics": [{"id": 88953, "value": 2.86}],
        "photos": [{"big": "https://images.wb.ru/big/new/20149.jpg"}],
        "price": 4520.0,
        "discount": 0,
        "search_words": "топор; топор для дров; топор туристический; топор колун; топор кованый; топор для плотника; топор с фиберглассовой ручкой",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20724": {
        "nmID": 20724,
        "vendorCode": "20724",
        "title": "Ножовка Libman по металлу 300мм SKRAB 20724",
        "description": "Ножовка по металлу SKRAB 300мм 20724. Полотно из прочной стали. Рукоятка не скользит в руке.",
        "dimensions": {"length": 40.0, "width": 14.0, "height": 3.0, "weightBrutto": 0.3},
        "sizes": [{"skus": ["4750735207248"]}],
        "characteristics": [{"id": 88953, "value": 0.3}],
        "photos": [{"big": "https://images.wb.ru/big/new/20724.jpg"}],
        "price": 1028.0,
        "discount": 0,
        "search_words": "ножовка по металлу ручная; ножовка универсальная; ножовка по металлу мини; мини ножовка по металлу",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20113": {
        "nmID": 20113,
        "vendorCode": "20113",
        "title": 'Топор 1000г с деревянной ручкой "ПЛОТНИК" SKRAB 20113',
        "description": "Кованый топор ПЛОТНИК Skrab 20113. Голова из инструментальной стали. Применяется для колки дров и рубки древесины.",
        "dimensions": {"length": 40.0, "width": 18.0, "height": 3.0, "weightBrutto": 1.27},
        "sizes": [{"skus": ["4750735201130"]}],
        "characteristics": [{"id": 88953, "value": 1.27}],
        "photos": [{"big": "https://images.wb.ru/big/new/20113.jpg"}],
        "price": 2636.0,
        "discount": 0,
        "search_words": "топор; топор для дров; топор кованый; топор с деревянной ручкой; топор для плотника",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20786": {
        "nmID": 20786,
        "vendorCode": "20786",
        "title": "Полотно для ручного лобзика 150мм 10шт. SKRAB 20786",
        "description": "Полотна для ручного лобзика 150мм 10шт. SKRAB 20786. Для распиливания металла, твердой древесины и жесткого пластика.",
        "dimensions": {"length": 23.0, "width": 5.0, "height": 1.0, "weightBrutto": 0.023},
        "sizes": [{"skus": ["4750735207866"]}],
        "characteristics": [{"id": 88953, "value": 0.023}],
        "photos": [{"big": "https://images.wb.ru/big/new/20786.jpg"}],
        "price": 902.0,
        "discount": 0,
        "search_words": "пилки для лобзика; пилки для лобзика по металлу; полотно по металлу; пилки для ручного лобзика по дереву",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20341": {
        "nmID": 20341,
        "vendorCode": "20341",
        "title": "Топор 630 гр фиберглассовая ручка SKRAB 20341",
        "description": "Топор универсальный с фиберглассовой ручкой SKRAB 20341. Материал лезвия: кованая углеродистая сталь с тефлоновым покрытием.",
        "dimensions": {"length": 53.0, "width": 20.0, "height": 2.0, "weightBrutto": 1.08},
        "sizes": [{"skus": ["4750735203417"]}],
        "characteristics": [{"id": 88953, "value": 1.08}],
        "photos": [{"big": "https://images.wb.ru/big/new/20341.jpg"}],
        "price": 5367.0,
        "discount": 0,
        "search_words": "топор; топор для дров; топор туристический; топор кованый; топор для плотника; топор с фиберглассовой ручкой",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20593": {
        "nmID": 20593,
        "vendorCode": "20593",
        "title": "Ножовка по газобетону с закаленными зубьями SKRAB 20593",
        "description": "Ножовка по газобетону 600мм SKRAB 20593. Длина полотна 600мм. Закаленные зубья. Двухкомпонентная рукоять с резиновым покрытием.",
        "dimensions": {"length": 73.0, "width": 15.0, "height": 3.0, "weightBrutto": 0.85},
        "sizes": [{"skus": ["4757305205930"]}],
        "characteristics": [{"id": 88953, "value": 0.85}],
        "photos": [{"big": "https://images.wb.ru/big/new/20593.jpg"}],
        "price": 1614.0,
        "discount": 0,
        "search_words": "ножовка по газобетону; ножовка; ножовка для газобетона; ножовки по газобетону",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20118": {
        "nmID": 20118,
        "vendorCode": "20118",
        "title": 'Топор 1250г с деревянной ручкой "ПЛОТНИК" SKRAB 20118',
        "description": "Кованый топор ПЛОТНИК Skrab 20118. Голова из инструментальной стали. Применяется для колки дров и рубки древесины.",
        "dimensions": {"length": 50.0, "width": 21.0, "height": 4.0, "weightBrutto": 1.59},
        "sizes": [{"skus": ["4750735201185"]}],
        "characteristics": [{"id": 88953, "value": 1.59}],
        "photos": [{"big": "https://images.wb.ru/big/new/20118.jpg"}],
        "price": 3648.0,
        "discount": 0,
        "search_words": "топор; топор для дров; топор кованый; топор с деревянной ручкой; топор для плотника",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20782": {
        "nmID": 20782,
        "vendorCode": "20782",
        "title": "Полотна для ручной ножовки SKRAB 20782",
        "description": "Полотна для ручной ножовки Skrab 20782. Шаг зубьев 24 TPI. В комплекте 10 штук. Изготовлены из биметалла.",
        "dimensions": {"length": 31.0, "width": 1.0, "height": 1.0, "weightBrutto": 0.2},
        "sizes": [{"skus": ["4750735207828"]}],
        "characteristics": [{"id": 88953, "value": 0.2}],
        "photos": [{"big": "https://images.wb.ru/big/new/20782.jpg"}],
        "price": 2277.0,
        "discount": 0,
        "search_words": "полотно для ножовки по металлу; полотно по металлу для ножовки; полотно для ножовки",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20111": {
        "nmID": 20111,
        "vendorCode": "20111",
        "title": 'Топор 600г с деревянной ручкой "ПЛОТНИК" SKRAB 20111',
        "description": "Кованый топор ПЛОТНИК Skrab 20111. Голова из инструментальной стали. Применяется для колки дров и плотничных работ.",
        "dimensions": {"length": 36.0, "width": 15.0, "height": 3.0, "weightBrutto": 0.84},
        "sizes": [{"skus": ["4750735201116"]}],
        "characteristics": [{"id": 88953, "value": 0.84}],
        "photos": [{"big": "https://images.wb.ru/big/new/20111.jpg"}],
        "price": 2003.0,
        "discount": 0,
        "search_words": "топор; топор для дров; топор кованый; топор с деревянной ручкой; топор для плотника",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20846": {
        "nmID": 20846,
        "vendorCode": "20846",
        "title": "Пилки для лобзика набор 5пр. Ламинат/Дерево SKRAB 20846",
        "description": "Набор пилок для лобзика SKRAB 20846. Для обработки дерева, ламината, пластика и ДСП. 5 пилок с T-образным хвостовиком.",
        "dimensions": {"length": 20.0, "width": 10.0, "height": 1.0, "weightBrutto": 0.15},
        "sizes": [{"skus": ["4750735208467"]}],
        "characteristics": [{"id": 88953, "value": 0.15}],
        "photos": [{"big": "https://images.wb.ru/big/new/20846.jpg"}],
        "price": 960.0,
        "discount": 0,
        "search_words": "пилки для электролобзика; пилки для электролобзика по дереву; пилка для лобзика; набор пилок для электролобзика",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20109": {
        "nmID": 20109,
        "vendorCode": "20109",
        "title": "Киянка 75 мм 900г. белая, деревянная ручка SKRAB 20109",
        "description": "КИЯНКА 75 ММ 900Г БЕЛАЯ ДЕРЕВЯННАЯ РУЧКА SKRAB 20109. Резиновая ударная часть не повреждает поверхность материала. Удобная деревянная ручка.",
        "dimensions": {"length": 36.0, "width": 11.0, "height": 7.0, "weightBrutto": 0.9},
        "sizes": [{"skus": ["4750735201093"]}],
        "characteristics": [{"id": 88953, "value": 0.9}],
        "photos": [{"big": "https://images.wb.ru/big/new/20109.jpg"}],
        "price": 1734.0,
        "discount": 0,
        "search_words": "киянка резиновая; киянка",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20714": {
        "nmID": 20714,
        "vendorCode": "20714",
        "title": "Ножовка Libman универсальная, рамка 150мм SKRAB 20714",
        "description": "Ножовка SKRAB рамка 150мм 20714. Лезвие из прочной инструментальной стали. Рукоятка из алюминия. Тип: лучковая пила.",
        "dimensions": {"length": 24.0, "width": 7.0, "height": 1.0, "weightBrutto": 0.075},
        "sizes": [{"skus": ["4750735207149"]}],
        "characteristics": [{"id": 88953, "value": 0.075}],
        "photos": [{"big": "https://images.wb.ru/big/new/20714.jpg"}],
        "price": 557.0,
        "discount": 0,
        "search_words": "ножовка по металлу ручная; ножовка универсальная; мини ножовка по металлу",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20112": {
        "nmID": 20112,
        "vendorCode": "20112",
        "title": 'Топор 800г с деревянной ручкой "ПЛОТНИК" SKRAB 20112',
        "description": "Кованый топор ПЛОТНИК Skrab 20112. Голова из инструментальной стали. Для колки дров и плотничных работ.",
        "dimensions": {"length": 38.0, "width": 17.0, "height": 3.0, "weightBrutto": 1.0},
        "sizes": [{"skus": ["4750735201123"]}],
        "characteristics": [{"id": 88953, "value": 1.0}],
        "photos": [{"big": "https://images.wb.ru/big/new/20112.jpg"}],
        "price": 2131.0,
        "discount": 0,
        "search_words": "топор; топор для дров; топор кованый; топор с деревянной ручкой; топор для плотника",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20245": {
        "nmID": 20245,
        "vendorCode": "20245",
        "title": "Молоток 500г с фибер. ручкой оранж. SKRAB 20245",
        "description": "Инструмент создан с применением технологий ковки. Обладает бойком в виде квадрата. Рукоятка из стеклопластика с антискольжением.",
        "dimensions": {"length": 33.0, "width": 11.0, "height": 3.0, "weightBrutto": 0.683},
        "sizes": [{"skus": ["4750735202458"]}],
        "characteristics": [{"id": 88953, "value": 0.683}],
        "photos": [{"big": "https://images.wb.ru/big/new/20245.jpg"}],
        "price": 1556.0,
        "discount": 0,
        "search_words": "молоток; молоток строительный; молоток слесарный; молоток с фиберглассовой ручкой",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20100": {
        "nmID": 20100,
        "vendorCode": "20100",
        "title": "Киянка резиновая с фиберглассовой ручкой SKRAB 20100",
        "description": "Киянка резиновая с фиберглассовой ручкой SKRAB 20100. Для притирки деревянных массивов, укладки плитки и газобетонных блоков.",
        "dimensions": {"length": 29.0, "width": 8.0, "height": 5.0, "weightBrutto": 0.39},
        "sizes": [{"skus": ["4750735201000"]}],
        "characteristics": [{"id": 88953, "value": 0.39}],
        "photos": [{"big": "https://images.wb.ru/big/new/20100.jpg"}],
        "price": 1047.0,
        "discount": 0,
        "search_words": "киянка резиновая; киянка",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20507": {
        "nmID": 20507,
        "vendorCode": "20507",
        "title": "Ножовка по гипсокартону выкружная 180мм. SKRAB. 20507",
        "description": "Ножовка по гипсокартону выкружная 180мм 7 TPI SKRAB 20507. Толщина полотна 1,25мм. Зубья разведены. Пластиковая ручка.",
        "dimensions": {"length": 33.0, "width": 10.0, "height": 2.0, "weightBrutto": 0.1},
        "sizes": [{"skus": ["4750735205077"]}],
        "characteristics": [{"id": 88953, "value": 0.1}],
        "photos": [{"big": "https://images.wb.ru/big/new/20507.jpg"}],
        "price": 838.0,
        "discount": 0,
        "search_words": "ножовка универсальная; ножовка по гипсокартону; ножовки по гипсокартону; складная ножовка по гипсокартону",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20068": {
        "nmID": 20068,
        "vendorCode": "20068",
        "title": "Молоток-гвоздодер с фибер.ручкой оранж. 450г SKRAB 20068",
        "description": "Молоток-гвоздодер 450г с фиберглассовой оранжевой ручкой SKRAB. Головка из закаленной высококачественной стали.",
        "dimensions": {"length": 34.0, "width": 14.0, "height": 3.0, "weightBrutto": 0.72},
        "sizes": [{"skus": ["4750735200683"]}],
        "characteristics": [{"id": 88953, "value": 0.72}],
        "photos": [{"big": "https://images.wb.ru/big/new/20068.jpg"}],
        "price": 1541.0,
        "discount": 0,
        "search_words": "молоток; молоток строительный; гвоздодер; молоток слесарный; молоток гвоздодер; молоток с фиберглассовой ручкой",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20110": {
        "nmID": 20110,
        "vendorCode": "20110",
        "title": "Топор кованый 520 г с деревянной ручкой УДАЛЕЦ SKRAB 20110",
        "description": "Топор кованый УДАЛЕЦ Skrab 20110. Вес 520 г. Голова из инструментальной стали, деревянная ручка.",
        "dimensions": {"length": 21.0, "width": 25.0, "height": 4.0, "weightBrutto": 0.67},
        "sizes": [{"skus": ["4750735201109"]}],
        "characteristics": [{"id": 88953, "value": 0.67}],
        "photos": [{"big": "https://images.wb.ru/big/new/20110.jpg"}],
        "price": 2100.0,
        "discount": 0,
        "search_words": "топор; топор для дров; топор туристический; топор кованый; топор с деревянной ручкой; топор для плотника",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20101": {
        "nmID": 20101,
        "vendorCode": "20101",
        "title": "Киянка,белая резина, с фиберглассовой ручкой SKRAB 20101",
        "description": "Киянка 340 г (белая резина) с фиберглассовой ручкой Skrab 20101. Головка из белой резины, спрессованной под давлением. Ручка из фибергласса.",
        "dimensions": {"length": 30.0, "width": 9.0, "height": 5.0, "weightBrutto": 0.5},
        "sizes": [{"skus": ["4750735201017"]}],
        "characteristics": [{"id": 88953, "value": 0.5}],
        "photos": [{"big": "https://images.wb.ru/big/new/20101.jpg"}],
        "price": 1019.0,
        "discount": 0,
        "search_words": "киянка резиновая; киянка",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20108": {
        "nmID": 20108,
        "vendorCode": "20108",
        "title": "Киянка 65 ММ 680г белая деревянная ручка SKRAB 20108",
        "description": "Киянка 65 ММ 680г белая деревянная ручка SKRAB 20108. Резиновая ударная часть. Удобная деревянная ручка.",
        "dimensions": {"length": 34.0, "width": 11.0, "height": 6.0, "weightBrutto": 0.68},
        "sizes": [{"skus": ["4750735201086"]}],
        "characteristics": [{"id": 88953, "value": 0.68}],
        "photos": [{"big": "https://images.wb.ru/big/new/20108.jpg"}],
        "price": 1440.0,
        "discount": 0,
        "search_words": "киянка резиновая; киянка",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20780": {
        "nmID": 20780,
        "vendorCode": "20780",
        "title": "Полотно по металлу 300 мм С200 24TPI, 10 шт. SKRAB 20780",
        "description": "Полотно по металлу 300 мм С200 24TPI 10 шт. SKRAB 20780. Из быстрорежущей стали. Шаг зубьев 24 TPI.",
        "dimensions": {"length": 32.0, "width": 1.0, "height": 1.0, "weightBrutto": 0.167},
        "sizes": [{"skus": ["4750735207804"]}],
        "characteristics": [{"id": 88953, "value": 0.167}],
        "photos": [{"big": "https://images.wb.ru/big/new/20780.jpg"}],
        "price": 1055.0,
        "discount": 0,
        "search_words": "пилки для лобзика; пилки для лобзика по металлу; полотно по металлу; полотно для лобзика",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20840": {
        "nmID": 20840,
        "vendorCode": "20840",
        "title": "Пилки для лобзика 3пр. по дереву Т144D SKRAB 20840",
        "description": "Пилки для лобзика 3 шт. по дереву Т144D SKRAB 20840. Хвостовик Т. Для прямого реза по дереву.",
        "dimensions": {"length": 16.0, "width": 6.0, "height": 1.0, "weightBrutto": 0.027},
        "sizes": [{"skus": ["4750735208405"]}],
        "characteristics": [{"id": 88953, "value": 0.027}],
        "photos": [{"big": "https://images.wb.ru/big/new/20840.jpg"}],
        "price": 611.0,
        "discount": 0,
        "search_words": "пилки для электролобзика; пилки для электролобзика по дереву; пилка для лобзика; набор пилок для электролобзика",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20842": {
        "nmID": 20842,
        "vendorCode": "20842",
        "title": "Пилки для лобзика по дереву Cr-V,2 шт SKRAB 20842",
        "description": "Пилки для лобзика по дереву Cr-V 2 шт. SKRAB 20842. Хвостовик Т. Для прямого реза по дереву.",
        "dimensions": {"length": 14.0, "width": 5.0, "height": 1.0, "weightBrutto": 0.011},
        "sizes": [{"skus": ["4750735208429"]}],
        "characteristics": [{"id": 88953, "value": 0.011}],
        "photos": [{"big": "https://images.wb.ru/big/new/20842.jpg"}],
        "price": 552.0,
        "discount": 0,
        "search_words": "пилки для электролобзика; пилки для электролобзика по дереву; пилка для лобзика; набор пилок для электролобзика",
        "updatedAt": "2025-08-22T00:00:00",
    },
    "20843": {
        "nmID": 20843,
        "vendorCode": "20843",
        "title": "Пилки для лобзика SKRAB Т-101 B п/дер Cr-V 2 шт 20843",
        "description": "Пилки для лобзика SKRAB Т-101 B п/дер Cr-V 2 шт 20843. Хвостовик Т. Для чистого реза по дереву.",
        "dimensions": {"length": 17.0, "width": 5.0, "height": 1.0, "weightBrutto": 0.016},
        "sizes": [{"skus": ["4750735208436"]}],
        "characteristics": [{"id": 88953, "value": 0.016}],
        "photos": [{"big": "https://images.wb.ru/big/new/20843.jpg"}],
        "price": 563.0,
        "discount": 0,
        "search_words": "пилки для электролобзика; пилки для электролобзика по дереву; пилка для лобзика; набор пилок для электролобзика",
        "updatedAt": "2025-08-22T00:00:00",
    },
}

# barcode → vendorCode
BARCODE_TO_SKU: dict[str, str] = {
    "4750735208412": "20841",
    "4750735207835": "20783",
    "4750735202410": "20241",
    "4750735203479": "20347",
    "4750735207712": "20771",
    "4750735200690": "20069",
    "4750735202564": "20256",
    "4750735201413": "20141",
    "4750735202489": "20248",
    "4750735207842": "20784",
    "4750735208450": "20845",
    "4750735203462": "20346",
    "4750735205251": "20525",
    "4750735200867": "20086",
    "4750735205268": "20526",
    "4750735208634": "20863",
    "4750735207811": "20781",
    "4750735203400": "20340",
    "4750735208443": "20844",
    "4750735203424": "20342",
    "4750735205015": "20501",
    "4750735208627": "20862",
    "4750735208603": "20860",
    "4750735200751": "20075",
    "4750735201536": "20153",
    "4750735201529": "20152",
    "4750735201499": "20149",
    "4750735207248": "20724",
    "4750735201130": "20113",
    "4750735207866": "20786",
    "4750735203417": "20341",
    "4757305205930": "20593",
    "4750735201185": "20118",
    "4750735207828": "20782",
    "4750735201116": "20111",
    "4750735208467": "20846",
    "4750735201093": "20109",
    "4750735207149": "20714",
    "4750735201123": "20112",
    "4750735202458": "20245",
    "4750735201000": "20100",
    "4750735205077": "20507",
    "4750735200683": "20068",
    "4750735201109": "20110",
    "4750735201017": "20101",
    "4750735201086": "20108",
    "4750735207804": "20780",
    "4750735208405": "20840",
    "4750735208429": "20842",
    "4750735208436": "20843",
}

# warehouse_id → {barcode: qty}
WH_BARCODE_STOCKS: dict[int, dict[str, int]] = {
    wh["id"]: {bc: random.randint(5, 60) for bc in BARCODE_TO_SKU}
    for wh in WAREHOUSES
}

# warehouse_name → {vendorCode: qty}
SUPPLIER_STOCKS: dict[str, dict[str, int]] = {
    wh["name"]: {sku: random.randint(5, 60) for sku in PRODUCTS}
    for wh in WAREHOUSES
}


# ---------------------------------------------------------------------------
# Drift — ±2% prices, ±3 units stocks, runs every 60 s
# ---------------------------------------------------------------------------

def _drift() -> None:
    for product in PRODUCTS.values():
        product["price"] = max(100.0, round(product["price"] * random.uniform(0.98, 1.02), 2))

    for wh_stocks in SUPPLIER_STOCKS.values():
        for sku in wh_stocks:
            wh_stocks[sku] = max(0, wh_stocks[sku] + random.randint(-3, 3))

    for bc_stocks in WH_BARCODE_STOCKS.values():
        for bc in bc_stocks:
            bc_stocks[bc] = max(0, bc_stocks[bc] + random.randint(-3, 3))


async def _background_drift() -> None:
    while True:
        await asyncio.sleep(60)
        _drift()


@asynccontextmanager
async def lifespan(_: FastAPI):
    asyncio.create_task(_background_drift())
    yield


app = FastAPI(lifespan=lifespan)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.get("/open-utils/tokens/introspect-v2")
async def introspect():
    return {"Ok": True, "payload": {"type": "seller"}}


# ---------------------------------------------------------------------------
# Cards (content-api.wildberries.ru)
# ---------------------------------------------------------------------------

@app.post("/content/v2/get/cards/list")
async def get_cards_list(request: Request):
    body = await request.json()
    limit = body.get("settings", {}).get("cursor", {}).get("limit", 100)
    cards = list(PRODUCTS.values())
    page = cards[:limit]
    last = page[-1] if page else {}
    return {
        "cards": page,
        "cursor": {
            "total": len(page),
            "nmID": last.get("nmID", 0),
            "updatedAt": last.get("updatedAt", "2025-08-22T00:00:00"),
        },
    }


@app.post("/content/v2/cards/update")
async def update_cards(request: Request):
    body = await request.json()
    for item in body:
        sku = item.get("vendorCode")
        if sku in PRODUCTS:
            p = PRODUCTS[sku]
            p["title"] = item.get("title", p["title"])
            p["description"] = item.get("description", p["description"])
            p["dimensions"] = item.get("dimensions", p["dimensions"])
    return {}


@app.get("/content/v2/cards/error/list")
async def cards_error_list():
    return {"data": []}


# ---------------------------------------------------------------------------
# Prices (discounts-prices-api.wildberries.ru)
# ---------------------------------------------------------------------------

@app.get("/api/v2/list/goods/filter")
async def list_goods_filter(limit: int = 100, offset: int = 0):
    items = list(PRODUCTS.values())[offset: offset + limit]
    goods = [
        {
            "nmID": p["nmID"],
            "vendorCode": p["vendorCode"],
            "discount": p["discount"],
            "sizes": [
                {
                    "price": p["price"],
                    "discountedPrice": round(p["price"] * (1 - p["discount"] / 100), 2),
                }
            ],
        }
        for p in items
    ]
    return {"data": {"listGoods": goods}}


@app.post("/api/v2/upload/task")
async def upload_price_task(request: Request):
    body = await request.json()
    for item in body.get("data", []):
        nm_id = item.get("nmID")
        for p in PRODUCTS.values():
            if p["nmID"] == nm_id:
                if "price" in item:
                    p["price"] = float(item["price"])
                if "discount" in item:
                    p["discount"] = int(item["discount"])
    task_id = random.randint(10000, 99999)
    return {"data": {"id": task_id}}


@app.get("/api/v2/history/tasks")
async def history_tasks(uploadID: int = 0):
    return {
        "data": {
            "uploadID": uploadID,
            "status": "done",
            "overAllGoodsNumber": len(PRODUCTS),
            "successGoodsNumber": len(PRODUCTS),
        }
    }


# ---------------------------------------------------------------------------
# Warehouses (supplies-api.wildberries.ru)
# ---------------------------------------------------------------------------

@app.get("/api/v1/warehouses")
async def get_warehouses():
    return [{"ID": wh["id"], "name": wh["name"]} for wh in WAREHOUSES]


# ---------------------------------------------------------------------------
# Stocks (statistics-api.wildberries.ru)
# ---------------------------------------------------------------------------

@app.get("/api/v1/supplier/stocks")
async def get_supplier_stocks(dateFrom: str = "2000-01-01"):
    result = []
    for wh_name, wh_stocks in SUPPLIER_STOCKS.items():
        for sku, qty in wh_stocks.items():
            result.append(
                {
                    "supplierArticle": sku,
                    "warehouseName": wh_name,
                    "quantity": qty,
                    "quantityFull": qty,
                }
            )
    return result


@app.get("/api/v1/supplier/orders")
async def get_orders(dateFrom: str = "2024-08-01"):
    return []


# ---------------------------------------------------------------------------
# Per-warehouse stocks (marketplace-api.wildberries.ru)
# ---------------------------------------------------------------------------

@app.post("/api/v3/stocks/{warehouse_id}")
async def get_stocks_on_warehouse(warehouse_id: int = Path(...), request: Request = None):
    body = await request.json()
    barcodes: list[str] = body.get("skus", [])
    bc_stocks = WH_BARCODE_STOCKS.get(warehouse_id, {})
    stocks = [{"sku": bc, "amount": bc_stocks.get(bc, 0)} for bc in barcodes]
    return {"stocks": stocks}


# ---------------------------------------------------------------------------
# Analytics / Turnover (seller-analytics-api.wildberries.ru)
# ---------------------------------------------------------------------------

@app.post("/api/v2/stocks-report/products/groups")
async def stocks_report(request: Request):
    body = await request.json()
    nm_ids: list[int] = body.get("nmIDs", [])
    items = [
        {
            "nmID": nm_id,
            "metrics": {
                "avgStockTurnover": {"hours": round(random.uniform(24, 720), 1)},
                "saleRate": {"hours": round(random.uniform(1, 48), 1)},
            },
        }
        for nm_id in nm_ids
    ]
    return {"data": {"groups": [{"items": items}]}}
