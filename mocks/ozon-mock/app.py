import asyncio
import random
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request


# ---------------------------------------------------------------------------
# State — 50 real products from SKRAB catalog, 43 Ozon warehouses from DB
# ---------------------------------------------------------------------------

WAREHOUSES = [
    {"id": 522, "name": "Спб Волхонка РФЦ Негабарит"},
    {"id": 525, "name": "Нижний Новгород 2 РФЦ"},
    {"id": 526, "name": "Волгоград РФЦ"},
    {"id": 521, "name": "Саратов РФЦ"},
    {"id": 467, "name": "Оренбург РФЦ"},
    {"id": 527, "name": "Воронеж РФЦ"},
    {"id": 375, "name": "Минск МПСЦ"},
    {"id": 439, "name": "Новороссийск МРФЦ"},
    {"id": 425, "name": "Хоругвино РФЦ"},
    {"id": 406, "name": "Домодедово РФЦ"},
    {"id": 435, "name": "Ярославль РФЦ"},
    {"id": 426, "name": "Тюмень РФЦ"},
    {"id": 424, "name": "Омск РФЦ"},
    {"id": 431, "name": "Казань РФЦ Новый"},
    {"id": 377, "name": "Тверь РФЦ"},
    {"id": 428, "name": "Астана РФЦ"},
    {"id": 407, "name": "Алматы 2 РФЦ"},
    {"id": 382, "name": "Софьино РФЦ"},
    {"id": 402, "name": "Пушкино 2 РФЦ"},
    {"id": 376, "name": "Жуковский РФЦ"},
    {"id": 379, "name": "Екатеринбург РФЦ"},
    {"id": 380, "name": "Новосибирск РФЦ"},
    {"id": 374, "name": "Краснодар РФЦ"},
    {"id": 378, "name": "Хабаровск МРФЦ"},
    {"id": 381, "name": "Ростов-на-Дону РФЦ"},
    {"id": 383, "name": "Уфа РФЦ"},
    {"id": 384, "name": "Самара РФЦ"},
    {"id": 385, "name": "Красноярск РФЦ"},
    {"id": 386, "name": "Пермь РФЦ"},
    {"id": 387, "name": "Воронеж РФЦ 2"},
    {"id": 388, "name": "Иркутск РФЦ"},
    {"id": 389, "name": "Челябинск РФЦ"},
    {"id": 390, "name": "Владивосток РФЦ"},
    {"id": 391, "name": "Тула РФЦ"},
    {"id": 392, "name": "Волгоград РФЦ 2"},
    {"id": 393, "name": "Тольятти РФЦ"},
    {"id": 394, "name": "Барнаул РФЦ"},
    {"id": 395, "name": "Кемерово РФЦ"},
    {"id": 396, "name": "Рязань РФЦ"},
    {"id": 397, "name": "Саратов РФЦ 2"},
    {"id": 398, "name": "Томск РФЦ"},
    {"id": 399, "name": "Нижний Тагил РФЦ"},
    {"id": 400, "name": "Ставрополь РФЦ"},
]

PRODUCTS: dict[str, dict] = {
    "20841": {
        "product_id": 1328,
        "offer_id": "20841",
        "name": "Пилки для лобзика (дерево/металл/пластик) SKRAB 20841",
        "description": "Пилки для электролобзика дерево-металл-пластик 3шт. SKRAB 20841. Тип: универсальные. Назначение: прямой рез. Хвостовик Т. Рабочая длина 74 мм, общая длина 100 мм.",
        "price": 614.0,
        "marketing_price": 675.4,
        "old_price": 736.8,
        "min_price": 429.8,
        "barcodes": ["4750735208412"],
        "search_words": "пилки для электролобзика; пилки для электролобзика по дереву; пилка для лобзика; набор пилок для электролобзика",
        "market_sku": 1328,
        "weight": 0.026,
        "length": 16.0,
        "width": 6.0,
        "height": 1.0,
    },
    "20101": {
        "product_id": 3693,
        "offer_id": "20101",
        "name": "Киянка,белая резина, с фиберглассовой ручкой SKRAB 20101",
        "description": "Киянка 340 г (белая резина) с фиберглассовой ручкой Skrab 20101. Головка из белой резины, спрессованной под давлением. Ручка из фибергласса.",
        "price": 1007.0,
        "marketing_price": 1107.7,
        "old_price": 1208.4,
        "min_price": 704.9,
        "barcodes": ["4750735201017"],
        "search_words": "киянка резиновая; киянка",
        "market_sku": 3693,
        "weight": 0.5,
        "length": 30.0,
        "width": 9.0,
        "height": 5.0,
    },
    "20152": {
        "product_id": 3703,
        "offer_id": "20152",
        "name": "Кувалда с защитой 1250г дер.ручка SKRAB 20152",
        "description": "Кувалда с защитой 1250г SKRAB 20152. Деревянная ручка защищена металлической защитой от излома. Инструмент из кованой стали.",
        "price": 1215.0,
        "marketing_price": 1336.5,
        "old_price": 1458.0,
        "min_price": 850.5,
        "barcodes": ["4750735201529"],
        "search_words": "кувалда",
        "market_sku": 3703,
        "weight": 1.3,
        "length": 26.0,
        "width": 10.0,
        "height": 4.0,
    },
    "20245": {
        "product_id": 2214,
        "offer_id": "20245",
        "name": "Молоток 500г с фибер. ручкой оранж. SKRAB 20245",
        "description": "Молоток 500г с фиберглассовой ручкой SKRAB 20245. Инструмент из ковки. Боек квадратный. Рукоятка из стеклопластика с антискольжением.",
        "price": 1556.0,
        "marketing_price": 1711.6,
        "old_price": 1867.2,
        "min_price": 1089.2,
        "barcodes": ["4750735202458"],
        "search_words": "молоток; молоток строительный; молоток слесарный; молоток с фиберглассовой ручкой",
        "market_sku": 2214,
        "weight": 0.683,
        "length": 33.0,
        "width": 11.0,
        "height": 3.0,
    },
    "20507": {
        "product_id": 1399,
        "offer_id": "20507",
        "name": "Ножовка по гипсокартону выкружная 180мм. SKRAB. 20507",
        "description": "Ножовка по гипсокартону выкружная 180мм 7 TPI SKRAB 20507. Толщина полотна 1,25мм. Пластиковая ручка.",
        "price": 826.0,
        "marketing_price": 908.6,
        "old_price": 991.2,
        "min_price": 578.2,
        "barcodes": ["4750735205077"],
        "search_words": "ножовка универсальная; ножовка по гипсокартону; ножовки по гипсокартону",
        "market_sku": 1399,
        "weight": 0.1,
        "length": 33.0,
        "width": 10.0,
        "height": 2.0,
    },
    "20069": {
        "product_id": 2215,
        "offer_id": "20069",
        "name": "Молоток-гвоздодер с фибер.ручкой оранж. 560г SKRAB 20069",
        "description": "Молоток-гвоздодер 560г с фиберглассовой оранжевой ручкой SKRAB. Головка из закаленной стали.",
        "price": 1892.0,
        "marketing_price": 2081.2,
        "old_price": 2270.4,
        "min_price": 1324.4,
        "barcodes": ["4750735200690"],
        "search_words": "молоток; молоток строительный; гвоздодер; молоток слесарный; молоток гвоздодер; молоток с фиберглассовой ручкой",
        "market_sku": 2215,
        "weight": 0.789,
        "length": 34.0,
        "width": 14.0,
        "height": 3.0,
    },
    "20075": {
        "product_id": 2211,
        "offer_id": "20075",
        "name": "Молоток-гвоздодер Fiber 450 г. Сталь 40Cr SKRAB 20075",
        "description": "Молоток-гвоздодер Skrab 20075. Вес бойка 450 г. Из высококачественной легированной стали GB 40CR.",
        "price": 3483.0,
        "marketing_price": 3831.3,
        "old_price": 4179.6,
        "min_price": 2438.1,
        "barcodes": ["4750735200751"],
        "search_words": "молоток; молоток строительный; гвоздодер; молоток слесарный; молоток с фиберглассовой ручкой",
        "market_sku": 2211,
        "weight": 0.6,
        "length": 34.0,
        "width": 14.0,
        "height": 3.0,
    },
    "20086": {
        "product_id": 1819,
        "offer_id": "20086",
        "name": "Молоток кровельщика с фибер.ручкой оранж.600г SKRAB 20086",
        "description": "Молоток кровельщика SKRAB 20086. Из прочной инструментальной стали. Двухкомпонентное покрытие ручки поглощает вибрации.",
        "price": 1776.0,
        "marketing_price": 1953.6,
        "old_price": 2131.2,
        "min_price": 1243.2,
        "barcodes": ["4750735200867"],
        "search_words": "молоток; молоток строительный; молоток кровельщика; молоток с фиберглассовой ручкой",
        "market_sku": 1819,
        "weight": 0.82,
        "length": 34.0,
        "width": 17.0,
        "height": 3.0,
    },
    "20100": {
        "product_id": 3697,
        "offer_id": "20100",
        "name": "Киянка резиновая с фиберглассовой ручкой SKRAB 20100",
        "description": "Киянка резиновая с фиберглассовой ручкой SKRAB 20100. Для укладки плитки, газобетонных блоков.",
        "price": 1047.0,
        "marketing_price": 1151.7,
        "old_price": 1256.4,
        "min_price": 732.9,
        "barcodes": ["4750735201000"],
        "search_words": "киянка резиновая; киянка",
        "market_sku": 3697,
        "weight": 0.39,
        "length": 29.0,
        "width": 8.0,
        "height": 5.0,
    },
    "20108": {
        "product_id": 3692,
        "offer_id": "20108",
        "name": "Киянка 65 ММ 680г белая деревянная ручка SKRAB 20108",
        "description": "Киянка 65 ММ 680г белая деревянная ручка SKRAB 20108. Резиновая ударная часть. Деревянная ручка.",
        "price": 1428.0,
        "marketing_price": 1570.8,
        "old_price": 1713.6,
        "min_price": 999.6,
        "barcodes": ["4750735201086"],
        "search_words": "киянка резиновая; киянка",
        "market_sku": 3692,
        "weight": 0.68,
        "length": 34.0,
        "width": 11.0,
        "height": 6.0,
    },
    "20109": {
        "product_id": 3698,
        "offer_id": "20109",
        "name": "Киянка 75 мм 900г. белая, деревянная ручка SKRAB 20109",
        "description": "Киянка 75 ММ 900г белая деревянная ручка SKRAB 20109. Резиновая ударная часть. Удобная деревянная ручка.",
        "price": 1734.0,
        "marketing_price": 1907.4,
        "old_price": 2080.8,
        "min_price": 1213.8,
        "barcodes": ["4750735201093"],
        "search_words": "киянка резиновая; киянка",
        "market_sku": 3698,
        "weight": 0.9,
        "length": 36.0,
        "width": 11.0,
        "height": 7.0,
    },
    "20110": {
        "product_id": 2202,
        "offer_id": "20110",
        "name": "Топор кованый 520 г с деревянной ручкой УДАЛЕЦ SKRAB 20110",
        "description": "Топор кованый УДАЛЕЦ Skrab 20110. Вес 520 г. Голова из инструментальной стали, деревянная ручка.",
        "price": 2253.0,
        "marketing_price": 2478.3,
        "old_price": 2703.6,
        "min_price": 1577.1,
        "barcodes": ["4750735201109"],
        "search_words": "топор; топор для дров; топор кованый; топор с деревянной ручкой; топор для плотника",
        "market_sku": 2202,
        "weight": 0.67,
        "length": 21.0,
        "width": 25.0,
        "height": 4.0,
    },
    "20111": {
        "product_id": 2209,
        "offer_id": "20111",
        "name": 'Топор 600г с деревянной ручкой "ПЛОТНИК" SKRAB 20111',
        "description": "Кованый топор ПЛОТНИК Skrab 20111. Голова из инструментальной стали. Для колки дров и плотничных работ.",
        "price": 2003.0,
        "marketing_price": 2203.3,
        "old_price": 2403.6,
        "min_price": 1402.1,
        "barcodes": ["4750735201116"],
        "search_words": "топор; топор для дров; топор кованый; топор с деревянной ручкой; топор для плотника",
        "market_sku": 2209,
        "weight": 0.84,
        "length": 36.0,
        "width": 15.0,
        "height": 3.0,
    },
    "20112": {
        "product_id": 1822,
        "offer_id": "20112",
        "name": 'Топор 800г с деревянной ручкой "ПЛОТНИК" SKRAB 20112',
        "description": "Кованый топор ПЛОТНИК Skrab 20112. Голова из инструментальной стали. Для колки дров и плотничных работ.",
        "price": 1971.0,
        "marketing_price": 2168.1,
        "old_price": 2365.2,
        "min_price": 1379.7,
        "barcodes": ["4750735201123"],
        "search_words": "топор; топор для дров; топор кованый; топор с деревянной ручкой; топор для плотника",
        "market_sku": 1822,
        "weight": 1.0,
        "length": 38.0,
        "width": 17.0,
        "height": 3.0,
    },
    "20113": {
        "product_id": 1821,
        "offer_id": "20113",
        "name": 'Топор 1000г с деревянной ручкой "ПЛОТНИК" SKRAB 20113',
        "description": "Кованый топор ПЛОТНИК Skrab 20113. Голова из инструментальной стали. Для колки дров и плотничных работ.",
        "price": 2457.0,
        "marketing_price": 2702.7,
        "old_price": 2948.4,
        "min_price": 1719.9,
        "barcodes": ["4750735201130"],
        "search_words": "топор; топор для дров; топор кованый; топор с деревянной ручкой; топор для плотника",
        "market_sku": 1821,
        "weight": 1.27,
        "length": 40.0,
        "width": 18.0,
        "height": 3.0,
    },
    "20118": {
        "product_id": 1827,
        "offer_id": "20118",
        "name": 'Топор 1250г с деревянной ручкой "ПЛОТНИК" SKRAB 20118',
        "description": "Кованый топор ПЛОТНИК Skrab 20118. Голова из инструментальной стали. Для колки дров и плотничных работ.",
        "price": 3432.0,
        "marketing_price": 3775.2,
        "old_price": 4118.4,
        "min_price": 2402.4,
        "barcodes": ["4750735201185"],
        "search_words": "топор; топор для дров; топор кованый; топор с деревянной ручкой; топор для плотника",
        "market_sku": 1827,
        "weight": 1.59,
        "length": 50.0,
        "width": 21.0,
        "height": 4.0,
    },
    "20141": {
        "product_id": 2205,
        "offer_id": "20141",
        "name": "Топор 600г с фибр.ручкой зелено-черный SKRAB 20141",
        "description": "Топор с фиберглассовой ручкой Skrab 20141 для заготовки древесины и плотницких работ.",
        "price": 1863.0,
        "marketing_price": 2049.3,
        "old_price": 2235.6,
        "min_price": 1304.1,
        "barcodes": ["4750735201413"],
        "search_words": "топор; топор для дров; топор кованый; топор для плотника; топор с фиберглассовой ручкой",
        "market_sku": 2205,
        "weight": 0.94,
        "length": 35.0,
        "width": 15.0,
        "height": 2.0,
    },
    "20149": {
        "product_id": 2203,
        "offer_id": "20149",
        "name": "Топор-колун 2000г с фибр. ручкой удлиненый SKRAB 20149",
        "description": "Топор-колун SKRAB 20149. Удлиненная ручка из стеклопластика 800 мм. Обрезиненная ручка.",
        "price": 4520.0,
        "marketing_price": 4972.0,
        "old_price": 5424.0,
        "min_price": 3164.0,
        "barcodes": ["4750735201499"],
        "search_words": "топор; топор для дров; топор колун; топор с фиберглассовой ручкой",
        "market_sku": 2203,
        "weight": 2.86,
        "length": 85.0,
        "width": 20.0,
        "height": 4.0,
    },
    "20256": {
        "product_id": 3704,
        "offer_id": "20256",
        "name": "Кувалда 1250г с фибер. ручкой оранж. SKRAB 20256",
        "description": "Кувалда 1250г с фибер. ручкой оранж. SKRAB 20256. Инструмент из закалённой стали. Рукоятка из стеклопластика с антискольжением.",
        "price": 1568.0,
        "marketing_price": 1724.8,
        "old_price": 1881.6,
        "min_price": 1097.6,
        "barcodes": ["4750735202564"],
        "search_words": "кувалда",
        "market_sku": 3704,
        "weight": 1.4,
        "length": 26.0,
        "width": 10.0,
        "height": 4.0,
    },
    "20153": {
        "product_id": 3701,
        "offer_id": "20153",
        "name": "Кувалда с защитой 1500г дер.ручка SKRAB 20153",
        "description": "Кувалда с защитой 1500г SKRAB 20153. Деревянная ручка с металлической защитой от излома. Обрезиненная ручка.",
        "price": 1360.0,
        "marketing_price": 1496.0,
        "old_price": 1632.0,
        "min_price": 952.0,
        "barcodes": ["4750735201536"],
        "search_words": "кувалда",
        "market_sku": 3701,
        "weight": 1.6,
        "length": 27.0,
        "width": 10.0,
        "height": 4.0,
    },
    "20248": {
        "product_id": 2216,
        "offer_id": "20248",
        "name": "Молоток 800г с фибер. ручкой оранж. SKRAB 20248",
        "description": "Молоток 800г с фиберглассовой ручкой SKRAB 20248. Инструмент из ковки. Боек квадратный. Рукоятка с антискольжением.",
        "price": 2024.0,
        "marketing_price": 2226.4,
        "old_price": 2428.8,
        "min_price": 1416.8,
        "barcodes": ["4750735202489"],
        "search_words": "молоток; молоток строительный; молоток слесарный; молоток с фиберглассовой ручкой",
        "market_sku": 2216,
        "weight": 1.057,
        "length": 36.0,
        "width": 13.0,
        "height": 3.0,
    },
    "20341": {
        "product_id": 1828,
        "offer_id": "20341",
        "name": "Топор 630 гр фиберглассовая ручка SKRAB 20341",
        "description": "Топор универсальный с фиберглассовой ручкой SKRAB 20341. Материал лезвия: кованая углеродистая сталь с тефлоновым покрытием.",
        "price": 5087.0,
        "marketing_price": 5595.7,
        "old_price": 6104.4,
        "min_price": 3560.9,
        "barcodes": ["4750735203417"],
        "search_words": "топор; топор для дров; топор туристический; топор кованый; топор для плотника; топор с фиберглассовой ручкой",
        "market_sku": 1828,
        "weight": 1.08,
        "length": 53.0,
        "width": 20.0,
        "height": 2.0,
    },
    "20346": {
        "product_id": 3706,
        "offer_id": "20346",
        "name": 'Топор-колун кованый Fiber 1000г 28" 720мм SKRAB 20346',
        "description": "Топор-колун кованый Fiber 1000г SKRAB 20346. Лезвие из углеродистой стали с тефлоновым покрытием PTFE. Рукоятка из стекловолокна.",
        "price": 6150.0,
        "marketing_price": 6765.0,
        "old_price": 7380.0,
        "min_price": 4305.0,
        "barcodes": ["4750735203462"],
        "search_words": "топор; топор для дров; топор колун; топор кованый; топор для плотника",
        "market_sku": 3706,
        "weight": 1.81,
        "length": 80.0,
        "width": 21.0,
        "height": 4.0,
    },
    "20501": {
        "product_id": 2338,
        "offer_id": "20501",
        "name": "Ножовка по дереву SKRAB, с меняющимся углом 20501",
        "description": "Ножовка по дереву Skrab 20501. Сменное полотно устанавливается под 5-ю углами. Обрезиненная рукоятка.",
        "price": 1719.0,
        "marketing_price": 1890.9,
        "old_price": 2062.8,
        "min_price": 1203.3,
        "barcodes": ["4750735205015"],
        "search_words": "ножовка по дереву; ножовка; ножовка по дереву ручная; ножовки по дереву",
        "market_sku": 2338,
        "weight": 0.49,
        "length": 48.0,
        "width": 14.0,
        "height": 2.0,
    },
    "20525": {
        "product_id": 2335,
        "offer_id": "20525",
        "name": "Ножовка по дереву 400мм каленый зуб GREEN SK5 SKRAB 20525",
        "description": "Ножовка SKRAB 20525. Полотно длиной 40 см из японской стали SK-5 с антикоррозийным покрытием.",
        "price": 1927.0,
        "marketing_price": 2119.7,
        "old_price": 2312.4,
        "min_price": 1348.9,
        "barcodes": ["4750735205251"],
        "search_words": "ножовка по дереву; ножовка; ножовка по дереву ручная; ножовки по дереву",
        "market_sku": 2335,
        "weight": 0.35,
        "length": 47.0,
        "width": 13.0,
        "height": 13.0,
    },
    "20526": {
        "product_id": 2336,
        "offer_id": "20526",
        "name": "Ножовка по дереву 450мм каленый зуб GREEN SK5 SKRAB 20526",
        "description": "Ножовка SKRAB 20526. Полотно длиной 45 см из японской стали SK-5 с антикоррозийным покрытием.",
        "price": 1537.0,
        "marketing_price": 1690.7,
        "old_price": 1844.4,
        "min_price": 1075.9,
        "barcodes": ["4750735205268"],
        "search_words": "ножовка по дереву; ножовка; ножовка по дереву ручная; ножовки по дереву",
        "market_sku": 2336,
        "weight": 0.5,
        "length": 50.0,
        "width": 13.0,
        "height": 2.0,
    },
    "20771": {
        "product_id": 2344,
        "offer_id": "20771",
        "name": "Полотно по металлу 150мм 10шт. MGH SKRAB 20771",
        "description": "Полотно по металлу 150мм 24TPI 10шт. SKRAB 20771. Длина 150 мм. Количество в наборе 10 шт.",
        "price": 760.0,
        "marketing_price": 836.0,
        "old_price": 912.0,
        "min_price": 532.0,
        "barcodes": ["4750735207712"],
        "search_words": "пилки для лобзика; пилки для лобзика по металлу; полотно по металлу; полотно для лобзика",
        "market_sku": 2344,
        "weight": 0.03,
        "length": 20.0,
        "width": 4.0,
        "height": 1.0,
    },
    "20781": {
        "product_id": 2342,
        "offer_id": "20781",
        "name": "Полотно по металлу (10 шт; 300 мм; 18TPI/С300) SKRAB 20781",
        "description": "Полотно по металлу 300 мм 18TPI 10 шт. SKRAB 20781. Из быстрорежущей стали. Шаг зубьев 18 TPI.",
        "price": 1141.0,
        "marketing_price": 1255.1,
        "old_price": 1369.2,
        "min_price": 798.7,
        "barcodes": ["4750735207811"],
        "search_words": "пилки для лобзика; пилки для лобзика по металлу; полотно по металлу; полотно для лобзика",
        "market_sku": 2342,
        "weight": 0.17,
        "length": 31.0,
        "width": 1.0,
        "height": 1.0,
    },
    "20782": {
        "product_id": 2343,
        "offer_id": "20782",
        "name": "Полотна для ручной ножовки SKRAB 20782",
        "description": "Полотна для ручной ножовки Skrab 20782. Шаг зубьев 24 TPI. В комплекте 10 штук. Из биметалла.",
        "price": 2277.0,
        "marketing_price": 2504.7,
        "old_price": 2732.4,
        "min_price": 1593.9,
        "barcodes": ["4750735207828"],
        "search_words": "полотно для ножовки по металлу; полотно по металлу для ножовки; полотно для ножовки",
        "market_sku": 2343,
        "weight": 0.2,
        "length": 31.0,
        "width": 1.0,
        "height": 1.0,
    },
    "20783": {
        "product_id": 2341,
        "offer_id": "20783",
        "name": "Полотно по металлу, биметаллическая сталь HSS SKRAB 20783",
        "description": "Полотна по металлу 300мм 32TPI/S500 Bi-Metal 20783 от SKRAB. Биметаллическая конструкция для долгого срока службы.",
        "price": 2432.0,
        "marketing_price": 2675.2,
        "old_price": 2918.4,
        "min_price": 1702.4,
        "barcodes": ["4750735207835"],
        "search_words": "полотно по металлу; полотна по металлу; полотно для лобзика; пилки по металлу",
        "market_sku": 2341,
        "weight": 0.176,
        "length": 32.0,
        "width": 1.0,
        "height": 1.0,
    },
    "20784": {
        "product_id": 2345,
        "offer_id": "20784",
        "name": 'Полотно по металлу 12"/300 мм 24 TPI, 10 штук SKRAB 20784',
        "description": "Полотно по металлу SKRAB 20784. Шаг зубьев 24 TPI. В комплекте 10 штук. Рабочая длина 300 мм.",
        "price": 760.0,
        "marketing_price": 836.0,
        "old_price": 912.0,
        "min_price": 532.0,
        "barcodes": ["4750735207842"],
        "search_words": "пилки для лобзика; пилки для лобзика по металлу; полотно по металлу; полотно для лобзика",
        "market_sku": 2345,
        "weight": 0.15,
        "length": 31.0,
        "width": 2.0,
        "height": 1.0,
    },
    "20786": {
        "product_id": 2346,
        "offer_id": "20786",
        "name": "Полотно для ручного лобзика 150мм 10шт. SKRAB 20786",
        "description": "Полотна для ручного лобзика 150мм 10шт. SKRAB 20786. Для распиливания металла, твердой древесины и жесткого пластика.",
        "price": 902.0,
        "marketing_price": 992.2,
        "old_price": 1082.4,
        "min_price": 631.4,
        "barcodes": ["4750735207866"],
        "search_words": "пилки для лобзика; пилки для лобзика по металлу; полотно по металлу; пилки для ручного лобзика по дереву",
        "market_sku": 2346,
        "weight": 0.023,
        "length": 23.0,
        "width": 5.0,
        "height": 1.0,
    },
    "20241": {
        "product_id": 2212,
        "offer_id": "20241",
        "name": "Молоток 100г с фибер. ручкой оранж. SKRAB 20241",
        "description": "Молоток 100г с фиберглассовой ручкой SKRAB 20241. Инструмент из ковки. Боек квадратный. Рукоятка из стеклопластика с антискольжением.",
        "price": 1096.0,
        "marketing_price": 1205.6,
        "old_price": 1315.2,
        "min_price": 767.2,
        "barcodes": ["4750735202410"],
        "search_words": "молоток; молоток строительный; молоток слесарный; молоток с фиберглассовой ручкой",
        "market_sku": 2212,
        "weight": 0.237,
        "length": 28.0,
        "width": 8.0,
        "height": 2.0,
    },
    "20347": {
        "product_id": 1820,
        "offer_id": "20347",
        "name": "Топор 1650 гр фиберглассовая ручка SKRAB 20347",
        "description": "Топор 1650 гр фиберглассовая ручка SKRAB 20347. Лезвие из углеродистой стали методом ковки. Фиберглассовая ручка.",
        "price": 7674.0,
        "marketing_price": 8441.4,
        "old_price": 9208.8,
        "min_price": 5371.8,
        "barcodes": ["4750735203479"],
        "search_words": "топор; топор для дров; топор туристический; топор кованый; топор для плотника; топор с фиберглассовой ручкой",
        "market_sku": 1820,
        "weight": 2.95,
        "length": 103.0,
        "width": 23.0,
        "height": 4.0,
    },
    "20780": {
        "product_id": 2346,
        "offer_id": "20780",
        "name": "Полотно по металлу 300 мм С200 24TPI, 10 шт. SKRAB 20780",
        "description": "Полотно по металлу 300 мм С200 24TPI 10 шт. SKRAB 20780. Из быстрорежущей стали. Шаг зубьев 24 TPI.",
        "price": 1168.0,
        "marketing_price": 1284.8,
        "old_price": 1401.6,
        "min_price": 817.6,
        "barcodes": ["4750735207804"],
        "search_words": "полотно по металлу; полотна по металлу; полотно для лобзика; пилки по металлу",
        "market_sku": 2346,
        "weight": 0.167,
        "length": 32.0,
        "width": 1.0,
        "height": 1.0,
    },
    "20840": {
        "product_id": 1327,
        "offer_id": "20840",
        "name": "Пилки для лобзика 3пр. по дереву Т144D SKRAB 20840",
        "description": "Пилки для лобзика 3 шт. по дереву Т144D SKRAB 20840. Хвостовик Т. Для прямого реза по дереву.",
        "price": 599.0,
        "marketing_price": 658.9,
        "old_price": 718.8,
        "min_price": 419.3,
        "barcodes": ["4750735208405"],
        "search_words": "пилки для электролобзика; пилки для электролобзика по дереву; пилка для лобзика; набор пилок для электролобзика",
        "market_sku": 1327,
        "weight": 0.027,
        "length": 16.0,
        "width": 6.0,
        "height": 1.0,
    },
    "20842": {
        "product_id": 1324,
        "offer_id": "20842",
        "name": "Пилки для лобзика по дереву Cr-V,2 шт SKRAB 20842",
        "description": "Пилки для лобзика по дереву Cr-V 2 шт. SKRAB 20842. Хвостовик Т. Для прямого реза по дереву.",
        "price": 540.0,
        "marketing_price": 594.0,
        "old_price": 648.0,
        "min_price": 378.0,
        "barcodes": ["4750735208429"],
        "search_words": "пилки для электролобзика; пилки для электролобзика по дереву; пилка для лобзика; набор пилок для электролобзика",
        "market_sku": 1324,
        "weight": 0.011,
        "length": 14.0,
        "width": 5.0,
        "height": 1.0,
    },
    "20843": {
        "product_id": 1325,
        "offer_id": "20843",
        "name": "Пилки для лобзика SKRAB Т-101 B п/дер Cr-V 2 шт 20843",
        "description": "Пилки для лобзика SKRAB Т-101 B п/дер Cr-V 2 шт 20843. Хвостовик Т. Для чистого реза по дереву.",
        "price": 551.0,
        "marketing_price": 606.1,
        "old_price": 661.2,
        "min_price": 385.7,
        "barcodes": ["4750735208436"],
        "search_words": "пилки для электролобзика; пилки для электролобзика по дереву; пилка для лобзика; набор пилок для электролобзика",
        "market_sku": 1325,
        "weight": 0.016,
        "length": 17.0,
        "width": 5.0,
        "height": 1.0,
    },
    "20068": {
        "product_id": 1818,
        "offer_id": "20068",
        "name": "Молоток-гвоздодер с фибер.ручкой оранж. 450г SKRAB 20068",
        "description": "Молоток-гвоздодер 450г с фиберглассовой оранжевой ручкой SKRAB. Головка из закаленной высококачественной стали.",
        "price": 1529.0,
        "marketing_price": 1681.9,
        "old_price": 1834.8,
        "min_price": 1070.3,
        "barcodes": ["4750735200683"],
        "search_words": "молоток; молоток строительный; гвоздодер; молоток слесарный; молоток гвоздодер; молоток с фиберглассовой ручкой",
        "market_sku": 1818,
        "weight": 0.72,
        "length": 34.0,
        "width": 14.0,
        "height": 3.0,
    },
    "20714": {
        "product_id": 1398,
        "offer_id": "20714",
        "name": "Ножовка Libman универсальная, рамка 150мм SKRAB 20714",
        "description": "Ножовка SKRAB рамка 150мм 20714. Лезвие из прочной инструментальной стали. Рукоятка из алюминия. Тип: лучковая пила.",
        "price": 455.0,
        "marketing_price": 500.5,
        "old_price": 546.0,
        "min_price": 318.5,
        "barcodes": ["4750735207149"],
        "search_words": "ножовка по металлу ручная; ножовка универсальная; мини ножовка по металлу",
        "market_sku": 1398,
        "weight": 0.075,
        "length": 24.0,
        "width": 7.0,
        "height": 1.0,
    },
    "20724": {
        "product_id": 1396,
        "offer_id": "20724",
        "name": "Ножовка Libman по металлу 300мм SKRAB 20724",
        "description": "Ножовка по металлу SKRAB 300мм 20724. Полотно из прочной стали. Рукоятка не скользит в руке.",
        "price": 908.0,
        "marketing_price": 998.8,
        "old_price": 1089.6,
        "min_price": 635.6,
        "barcodes": ["4750735207248"],
        "search_words": "ножовка по металлу ручная; ножовка универсальная; мини ножовка по металлу",
        "market_sku": 1396,
        "weight": 0.3,
        "length": 40.0,
        "width": 14.0,
        "height": 3.0,
    },
    "20844": {
        "product_id": 1330,
        "offer_id": "20844",
        "name": "Пилки для лобзика SKRAB Т-344 D п/дер Cr-V 2 шт SKRAB 20844",
        "description": "Пилки для лобзика SKRAB Т-344 D п/дер Cr-V 2 шт. Общая длина 125 мм. TPI 6. Хвостовик Т.",
        "price": 707.0,
        "marketing_price": 777.7,
        "old_price": 848.4,
        "min_price": 494.9,
        "barcodes": ["4750735208443"],
        "search_words": "пилки для электролобзика; пилки для электролобзика по дереву; пилка для лобзика; набор пилок для электролобзика",
        "market_sku": 1330,
        "weight": 0.022,
        "length": 19.0,
        "width": 5.0,
        "height": 1.0,
    },
    "20845": {
        "product_id": 1331,
        "offer_id": "20845",
        "name": "Пилки для электролобзика по дереву/металлу 5 шт. SKRAB 20845",
        "description": "Набор полотен для электролобзика 5 шт. Skrab 20845. Подходят для прямого и фигурного реза по дереву, металлу и пластику.",
        "price": 900.0,
        "marketing_price": 990.0,
        "old_price": 1080.0,
        "min_price": 630.0,
        "barcodes": ["4750735208450"],
        "search_words": "пилки для электролобзика; пилки для электролобзика по дереву; пилка для лобзика; набор пилок для электролобзика",
        "market_sku": 1331,
        "weight": 0.038,
        "length": 15.0,
        "width": 6.0,
        "height": 1.0,
    },
    "20846": {
        "product_id": 1332,
        "offer_id": "20846",
        "name": "Пилки для лобзика набор 5пр. Ламинат/Дерево SKRAB 20846",
        "description": "Набор пилок для лобзика SKRAB 20846. Для обработки дерева, ламината, пластика и ДСП. 5 пилок с T-образным хвостовиком.",
        "price": 960.0,
        "marketing_price": 1056.0,
        "old_price": 1152.0,
        "min_price": 672.0,
        "barcodes": ["4750735208467"],
        "search_words": "пилки для электролобзика; пилки для электролобзика по дереву; пилка для лобзика; набор пилок для электролобзика",
        "market_sku": 1332,
        "weight": 0.15,
        "length": 20.0,
        "width": 10.0,
        "height": 1.0,
    },
    "20860": {
        "product_id": 1335,
        "offer_id": "20860",
        "name": "Полотно для сабельной пилы п/газобетону SKRAB 20860",
        "description": "HCS — высокоуглеродистая сталь. 13 зубьев с твердосплавными напайками (TCT). Длина 215 мм.",
        "price": 1156.0,
        "marketing_price": 1271.6,
        "old_price": 1387.2,
        "min_price": 809.2,
        "barcodes": ["4750735208603"],
        "search_words": "полотно для сабельной пилы; полотно для сабельной пилы по газобетону; полотна для сабельной пилы",
        "market_sku": 1335,
        "weight": 0.07,
        "length": 30.0,
        "width": 8.0,
        "height": 1.0,
    },
    "20862": {
        "product_id": 1337,
        "offer_id": "20862",
        "name": "Полотно для сабельной пилы п/газобетону 14TСТ SKRAB 20862",
        "description": "Пилка для сабельной пилы по газобетону 320х47х2мм 14TCT Skrab 20862. HCS — высокоуглеродистая сталь.",
        "price": 1502.0,
        "marketing_price": 1652.2,
        "old_price": 1802.4,
        "min_price": 1051.4,
        "barcodes": ["4750735208627"],
        "search_words": "полотно для сабельной пилы; полотно для сабельной пилы по газобетону; полотна для сабельной пилы",
        "market_sku": 1337,
        "weight": 0.21,
        "length": 42.0,
        "width": 10.0,
        "height": 1.0,
    },
    "20863": {
        "product_id": 1338,
        "offer_id": "20863",
        "name": "Полотно для сабельной пилы по газобетону 462 мм SKRAB 20863",
        "description": "Полотно по газобетону 462х47х2мм 20 TCT SKRAB 20863. Хвостовик универсальный. Для пиления газобетонных блоков.",
        "price": 1753.0,
        "marketing_price": 1928.3,
        "old_price": 2103.6,
        "min_price": 1227.1,
        "barcodes": ["4750735208634"],
        "search_words": "полотно для сабельной пилы; полотно для сабельной пилы по газобетону; полотна для сабельной пилы",
        "market_sku": 1338,
        "weight": 0.2,
        "length": 58.0,
        "width": 3.0,
        "height": 1.0,
    },
    "20340": {
        "product_id": 2207,
        "offer_id": "20340",
        "name": "Топор 440 гр фиберглассовая ручка SKRAB 20340",
        "description": "Топор туристический кованый 230 мм с фиберглассовой ручкой. Из высокоуглеродистой стали с тефлоновым покрытием.",
        "price": 3219.0,
        "marketing_price": 3540.9,
        "old_price": 3862.8,
        "min_price": 2253.3,
        "barcodes": ["4750735203400"],
        "search_words": "топор; топор для дров; топор туристический; топор кованый; топор с фиберглассовой ручкой",
        "market_sku": 2207,
        "weight": 0.67,
        "length": 30.0,
        "width": 17.0,
        "height": 2.0,
    },
    "20342": {
        "product_id": 2208,
        "offer_id": "20342",
        "name": 'Топор кованый Fiber 820г 23,5" 610мм SKRAB 20342',
        "description": "Топор кованый Fiber 820г SKRAB 20342. Из углеродистой стали методом ковки. Тефлоновое покрытие. Рукоятка из стекловолокна.",
        "price": 5246.0,
        "marketing_price": 5770.6,
        "old_price": 6295.2,
        "min_price": 3672.2,
        "barcodes": ["4750735203424"],
        "search_words": "топор; топор для дров; топор туристический; топор кованый; топор для плотника",
        "market_sku": 2208,
        "weight": 0.82,
        "length": 67.0,
        "width": 20.0,
        "height": 3.0,
    },
    "20593": {
        "product_id": 2339,
        "offer_id": "20593",
        "name": "Ножовка по газобетону с закаленными зубьями SKRAB 20593",
        "description": "Ножовка по газобетону 600мм SKRAB 20593. Длина полотна 600мм. Закаленные зубья. Двухкомпонентная рукоять.",
        "price": 1614.0,
        "marketing_price": 1775.4,
        "old_price": 1936.8,
        "min_price": 1129.8,
        "barcodes": ["4757305205930"],
        "search_words": "ножовка по газобетону; ножовка; ножовка для газобетона; ножовки по газобетону",
        "market_sku": 2339,
        "weight": 0.85,
        "length": 73.0,
        "width": 15.0,
        "height": 3.0,
    },
}

STOCKS: dict[str, int] = {sku: random.randint(5, 80) for sku in PRODUCTS}

WAREHOUSE_NAME = WAREHOUSES[0]["name"]


# ---------------------------------------------------------------------------
# Drift — ±2% prices, ±3 units stocks, every 60 s
# ---------------------------------------------------------------------------

def _drift() -> None:
    for p in PRODUCTS.values():
        p["price"] = max(100.0, round(p["price"] * random.uniform(0.98, 1.02), 2))

    for sku in STOCKS:
        STOCKS[sku] = max(0, STOCKS[sku] + random.randint(-3, 3))


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
# Product list  (pagination: return all on first call, empty on second)
# ---------------------------------------------------------------------------

@app.post("/v3/product/list")
async def product_list(request: Request):
    body = await request.json()
    last_id = body.get("last_id", None)
    if last_id:
        return {"result": {"items": [], "last_id": "", "total": 0}}
    items = [{"product_id": p["product_id"], "offer_id": p["offer_id"]} for p in PRODUCTS.values()]
    return {"result": {"items": items, "last_id": "end", "total": len(items)}}


# ---------------------------------------------------------------------------
# Product info list (v3/product/info/list)
# ---------------------------------------------------------------------------

@app.post("/v3/product/info/list")
async def product_info_list(request: Request):
    body = await request.json()
    offer_ids: list[str] = body.get("offer_id", list(PRODUCTS.keys()))
    items = []
    for oid in offer_ids:
        p = PRODUCTS.get(oid)
        if not p:
            continue
        items.append(
            {
                "offer_id": p["offer_id"],
                "name": p["name"],
                "primary_image": [f"https://cdn.ozon.ru/img/{p['product_id']}.jpg"],
                "price": str(p["price"]),
                "statuses": {"status_description": "Активен", "validation_status": "ok"},
                "price_indexes": {
                    "price_index": "PROFIT",
                    "external_index_data": {"minimal_price": str(p["min_price"])},
                },
                "ozon_index_price": {"minimal_price": str(p["min_price"])},
                "barcodes": p["barcodes"],
                "sources": [{"sku": p["market_sku"]}],
            }
        )
    return {"items": items}


# ---------------------------------------------------------------------------
# Product attributes (v4/product/info/attributes)
# ---------------------------------------------------------------------------

@app.post("/v4/product/info/attributes")
async def product_info_attributes(request: Request):
    body = await request.json()
    offer_ids: list[str] = body.get("filter", {}).get("offer_id") or list(PRODUCTS.keys())
    result = []
    for oid in offer_ids:
        p = PRODUCTS.get(oid)
        if not p:
            continue
        result.append(
            {
                "offer_id": oid,
                "attributes": [
                    {"id": 4191, "values": [{"value": p["description"]}]},
                    {"id": 22336, "values": [{"value": p.get("search_words", "")}]},
                ],
                "height": int(p["height"] * 10),
                "depth": int(p["length"] * 10),
                "width": int(p["width"] * 10),
                "weight": int(p["weight"] * 1000),
                "dimension_unit": "mm",
                "weight_unit": "g",
            }
        )
    return {"result": result}


# ---------------------------------------------------------------------------
# Prices (v5/product/info/prices) — used by both price methods
# ---------------------------------------------------------------------------

@app.post("/v5/product/info/prices")
async def product_info_prices(request: Request):
    body = await request.json()
    offer_ids: list[str] = body.get("filter", {}).get("offer_id") or list(PRODUCTS.keys())
    items = []
    for oid in offer_ids:
        p = PRODUCTS.get(oid)
        if not p:
            continue
        items.append(
            {
                "offer_id": oid,
                "product_id": p["product_id"],
                "price": {
                    "price": str(p["price"]),
                    "marketing_price": str(p["marketing_price"]),
                    "marketing_seller_price": str(p["marketing_price"]),
                    "old_price": str(p["old_price"]),
                    "min_price": str(p["min_price"]),
                    "auto_action_enabled": "UNKNOWN",
                    "price_index": "WITHOUT_INDEX",
                    "retail_price": str(p["price"]),
                },
                "commissions": {
                    "sales_percent_fbo": 0.08,
                    "fbo_direct_flow_trans_min_amount": 50.0,
                },
            }
        )
    return {"items": items, "cursor": None, "total": len(items)}


# ---------------------------------------------------------------------------
# Import prices (v1/product/import/prices)
# ---------------------------------------------------------------------------

@app.post("/v1/product/import/prices")
async def import_prices(request: Request):
    body = await request.json()
    result = []
    for item in body.get("prices", []):
        oid = item.get("offer_id")
        if oid and oid in PRODUCTS:
            new_price = item.get("price")
            if new_price is not None:
                PRODUCTS[oid]["price"] = float(new_price)
            new_min = item.get("min_price")
            if new_min is not None:
                PRODUCTS[oid]["min_price"] = float(new_min)
            new_old = item.get("old_price")
            if new_old is not None:
                PRODUCTS[oid]["old_price"] = float(new_old)
        result.append({"offer_id": oid, "updated": True, "errors": []})
    return {"result": result}


# ---------------------------------------------------------------------------
# Import (update offers)  v3/product/import
# ---------------------------------------------------------------------------

@app.post("/v3/product/import")
async def product_import(request: Request):
    body = await request.json()
    for item in body.get("items", []):
        oid = item.get("offer_id")
        if oid and oid in PRODUCTS:
            p = PRODUCTS[oid]
            if item.get("name"):
                p["name"] = item["name"]
            if item.get("description"):
                p["description"] = item["description"]
    task_id = random.randint(100000, 999999)
    return {"result": {"task_id": task_id}}


@app.post("/v1/product/import/info")
async def import_info(request: Request):
    body = await request.json()
    task_id = body.get("task_id", 0)
    return {"result": {"task_id": task_id, "status": "imported", "items": []}}


# ---------------------------------------------------------------------------
# Stocks on warehouses (v2/analytics/stock_on_warehouses)
# ---------------------------------------------------------------------------

@app.post("/v2/analytics/stock_on_warehouses")
async def stock_on_warehouses(request: Request):
    rows = [
        {
            "warehouse_id": WAREHOUSES[0]["id"],
            "warehouse_name": WAREHOUSE_NAME,
            "item_code": sku,
            "item_name": PRODUCTS[sku]["name"],
            "promised_amount": 0,
            "free_to_sell_amount": STOCKS[sku],
            "reserved_amount": 0,
            "sku": PRODUCTS[sku]["market_sku"],
        }
        for sku in PRODUCTS
    ]
    return {"result": {"rows": rows}}


# ---------------------------------------------------------------------------
# Clusters (v1/cluster/list)
# ---------------------------------------------------------------------------

@app.post("/v1/cluster/list")
async def cluster_list():
    return {
        "clusters": [
            {
                "name": "Москва и область",
                "logistic_clusters": [
                    {
                        "warehouses": [
                            {"name": WAREHOUSE_NAME, "type": "FULL_FILLMENT"}
                        ]
                    }
                ],
            }
        ]
    }


# ---------------------------------------------------------------------------
# Content ratings (v1/product/rating-by-sku)
# ---------------------------------------------------------------------------

@app.post("/v1/product/rating-by-sku")
async def rating_by_sku(request: Request):
    body = await request.json()
    skus: list[int] = body.get("skus", [])
    return {
        "products": [
            {"sku": sku, "rating": round(random.uniform(3.5, 5.0), 1)}
            for sku in skus
        ]
    }


# ---------------------------------------------------------------------------
# Orders (v2/posting/fbo/list)
# ---------------------------------------------------------------------------

@app.post("/v2/posting/fbo/list")
async def fbo_orders():
    return {"result": []}


# ---------------------------------------------------------------------------
# Turnover (v1/analytics/turnover/stocks)
# ---------------------------------------------------------------------------

@app.post("/v1/analytics/turnover/stocks")
async def turnover_stocks(request: Request):
    body = await request.json()
    offer_ids: list[str] = body.get("sku", [])
    return {
        "items": [
            {
                "sku": oid,
                "turnover": round(random.uniform(5.0, 90.0), 1),
                "idc": round(random.uniform(1.0, 30.0), 1),
            }
            for oid in offer_ids
        ]
    }
