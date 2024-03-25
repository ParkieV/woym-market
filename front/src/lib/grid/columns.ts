import type { ValueGetterParams } from "ag-grid-enterprise";
import type { Column, ColumnGroup } from "../components/datagrid/columns";
import type { Template } from "$lib/data/templates";
import type { FboStocks } from "$lib/data/fbo_storage";
import type { Offer } from "$lib/data/offers";
import type { Market } from "$lib/data/markets";
import type { OwnStorage } from "$lib/data/own_storage";
import {
    ComboboxColumn,
    GroupColumn,
    BooleanColumn,
    dollarColumn,
    floatColumn,
    imageColumn,
    intColumn,
    percentColumn,
    rubleColumn,
    stringColumn
} from "$lib/components/datagrid/column_types";

export function offerColumns(templates: Template[]): (Column | ColumnGroup)[] {
    return [
        ...baseOfferColumns(),
        {
            header: "Габариты (Собственные)",
            children: [
                { header: "Вес", key: "self_weight", base: floatColumn, editable: true },
                { header: "Длина", key: "self_length", base: floatColumn, editable: true },
                { header: "Ширина", key: "self_width", base: floatColumn, editable: true },
                { header: "Высота", key: "self_height", base: floatColumn, editable: true },
                {
                    key: "volume",
                    header: "Объём",
                    base: floatColumn,
                    tooltip: "Длина * ширина * высота / 1000"
                }
            ]
        },
        {
            header: "Габариты (Маркет)",
            children: [
                { header: "Вес", key: "yandex_weight", base: floatColumn },
                { header: "Длина", key: "yandex_length", base: floatColumn },
                { header: "Ширина", key: "yandex_width", base: floatColumn },
                { header: "Высота", key: "yandex_height", base: floatColumn },
                {
                    key: "yandex_volume",
                    header: "Объём",
                    base: floatColumn,
                    tooltip: "Длина * ширина * высота / 1000"
                },
                {
                    key: "volume_difference",
                    header: "Разница объемов",
                    base: floatColumn
                }
            ]
        },
        {
            header: "Ценообразование",
            children: [
                {
                    key: "use_manual_min_price",
                    header: "Использовать ручную мин. цену",
                    base: new BooleanColumn(),
                    editable: true
                },
                {
                    key: "auto_min_price",
                    header: "Авто мин. цена (%)",
                    base: percentColumn,
                    editable: true
                },
                {
                    key: "auto_min_price_rubles",
                    header: "Авто мин. цена (руб)",
                    base: rubleColumn,
                    valueGetter: ({ data }: { data: Offer }) => {
                        if (data.total_price === null) return null;
                        return data.total_price * (data.auto_min_price / 100);
                    }
                },
                {
                    key: "manual_min_price",
                    header: "Ручная мин. цена",
                    base: floatColumn,
                    editable: true
                },
                {
                    key: "auto_price_control",
                    header: "Авто контроль цен",
                    base: new BooleanColumn(),
                    editable: true
                },
                {
                    key: "pricing_scheme_name",
                    header: "Схема ценообразования",
                    base: new ComboboxColumn<string>(
                        templates.map(t => ({ value: t.name, name: t.name }))
                    ),
                    editable: true
                },
                {
                    key: "your_price_for_buyers",
                    header: "Цена для покупателя",
                    base: floatColumn
                },
                {
                    key: "current_price",
                    header: "Текущая цена",
                    base: floatColumn
                },
                {
                    key: "dollar_cost_price",
                    header: "Закупка у. е.",
                    base: dollarColumn,
                    editable: true
                },
                {
                    key: "attractive_price_threshold",
                    header: "Порог для привлекательной цены",
                    base: floatColumn
                },
                {
                    key: "total_price_min_additional",
                    header: "Мин. наценка на расчетную цену",
                    base: floatColumn,
                    editable: true
                },
                {
                    key: "discount_base_price",
                    header: "Цена до скидки",
                    base: floatColumn,
                    tooltip: "Цена + 20%"
                },
                {
                    key: "profit",
                    header: "Прибыль",
                    base: floatColumn,
                    tooltip: "Текущая цена - налог - FBO  - себестоимость"
                },
                {
                    key: "total_price_coeff",
                    header: "Коэффициент расчетной цены",
                    base: floatColumn,
                    editable: true
                },
                {
                    key: "cost_price",
                    header: "Себестоимость",
                    base: floatColumn,
                    tooltip: "Закупка у. е. * курс"
                },
                {
                    key: "best_place_wm",
                    header: "Площадка с лучшей ценой (без учета Маркета)",
                    base: stringColumn
                },
                {
                    key: "min_price_without_market",
                    header: "Цена площадки (без учета Маркета)",
                    base: floatColumn
                },
                {
                    key: "fbo",
                    header: "Цена за FBO",
                    base: floatColumn
                },
                {
                    key: "total_price",
                    header: "Расчетная цена",
                    base: floatColumn,
                    tooltip: "Себестоимость * коэф. + мин. наценка"
                },
                {
                    key: "margin",
                    header: "Окупаемость",
                    base: percentColumn,
                    tooltip: "Прибыль / себестоимость * 100"
                },
                {
                    key: "moderately_attractive_price_threshold",
                    header: "Порог для умеренно привлекательной цены",
                    base: floatColumn
                },
                {
                    key: "best_place_im",
                    header: "Площадка с лучшей ценой (на Маркете)",
                    base: stringColumn
                },
                {
                    key: "min_price_in_market",
                    header: "Цена площадки (на Маркете)",
                    base: floatColumn
                },
                {
                    key: "min_general_markets_price",
                    header: "Минимальная цена в группе",
                    base: floatColumn
                },
                {
                    key: "target_price",
                    header: "Целевая цена",
                    base: floatColumn
                },
                {
                    key: "volume_profitability_ratio",
                    header: "Коэффициент прибыльности от объёма",
                    base: floatColumn
                },
                {
                    key: "days_to_zero_profit",
                    header: "Дней до нулевой прибыли",
                    base: floatColumn
                },
                {
                    key: "price_index",
                    header: "Индекс цены",
                    base: stringColumn
                },
                {
                    key: "market_discount_in_percent",
                    header: "Скидка маркета в %",
                    base: floatColumn
                }
            ]
        },
        {
            key: "remaining_stock",
            header: "Остатки на складах",
            base: intColumn
        },
        {
            key: "can_be_delivered",
            header: "Можно поставить",
            base: new BooleanColumn()
        },
        {
            key: "content_rating",
            header: "Контент рейтинг",
            base: floatColumn
        },
        {
            key: "supplier_available",
            header: "Наличие у поставщика",
            base: new BooleanColumn(),
            editable: true
        },
        { header: "Скрыт", key: "hidden", base: new BooleanColumn(), editable: true }
    ];
}

export function ownStorageColumns(markets: Market[]): (Column | ColumnGroup)[] {
    const noteCols = ([1, 2, 3] as const).map(i => {
        return {
            header: `Примечание ${i}`,
            key: `note_${i}`,
            valueGetter: ({ data }: { data: OwnStorage }) =>
                data[`note_${i}`].filter(x => x !== "").join("; "),
            base: stringColumn,
            columnGroupShow: "closed"
        } as Column;
    });
    const marketCols = markets.map(market => {
        return {
            header: `${market.name} (${market.type}), шт.`,
            key: `shops-${market.id}`,
            valueGetter: ({ data }: { data: OwnStorage }) => {
                let stock = data.stocks.find(
                    ({ market: type, name_of_shop }) =>
                        market.type === type && market.name === name_of_shop
                );
                return stock?.value;
            },
            base: intColumn
        } as Column;
    });

    return [
        {
            header: "SKU",
            key: "sku",
            base: new GroupColumn(),
            pinned: true
        },
        {
            header: "Информация",
            children: [
                {
                    header: "Фото",
                    key: "photo",
                    base: imageColumn,
                    valueGetter: ({ data }: { data: OwnStorage }) => {
                        if (data.photo === undefined || data.photo.length === 0) return null;
                        let photo = data.photo
                            .map(x => x ?? "")
                            .filter(x => x !== "")
                            .at(0);
                        return photo ?? null;
                    }
                },
                { header: "Название", key: "name.0", base: stringColumn },
                ...noteCols
            ]
        },
        {
            header: "Мой склад",
            key: "own_storage.value",
            base: intColumn,
            editable: true
        },
        ...marketCols
    ];
}

export function fboStocksColumns(): (Column | ColumnGroup)[] {
    return [
        ...baseOfferColumns(),
        {
            header: "Остатки",
            children: [
                {
                    header: "В наличии",
                    key: "current_stock",
                    base: intColumn,
                    valueGetter: (params: ValueGetterParams<FboStocks>) => {
                        if (!params.data) return 0;
                        return params.data.stocks
                            .map(x => x.current_stock)
                            .reduce((a, b) => a + b, 0);
                    }
                },
                {
                    header: "Мин. остаток",
                    key: "min_stock",
                    base: intColumn,
                    valueGetter: (params: ValueGetterParams<FboStocks>) => {
                        if (!params.data) return 0;
                        return params.data.stocks.map(x => x.min_stock).reduce((a, b) => a + b, 0);
                    }
                },
                {
                    header: "К поставке",
                    key: "to_deliver",
                    base: intColumn,
                    valueGetter: (params: ValueGetterParams<FboStocks>) => {
                        if (!params.data) return 0;
                        return params.data.stocks
                            .map(x => Math.max(0, x.min_stock - x.current_stock))
                            .reduce((a, b) => a + b, 0);
                    }
                },
                {
                    key: "can_be_delivered",
                    header: "Можно поставить",
                    base: new BooleanColumn()
                }
            ]
        },
        { header: "Скрыт", key: "hidden", base: new BooleanColumn(), editable: true }
    ];
}

export function fboStorageColumns(): (Column | ColumnGroup)[] {
    return [
        { header: "Склад", key: "warehouse.name", base: stringColumn },
        {
            header: "В наличии",
            key: "current_stock",
            base: intColumn
        },
        {
            header: "Мин. остаток",
            key: "min_stock",
            base: intColumn,
            editable: true
        },
        {
            header: "К поставке",
            key: "to_deliver",
            base: intColumn,
            valueGetter: params => {
                if (params.data) {
                    return Math.max(0, params.data.min_stock - params.data.current_stock);
                } else {
                    return 0;
                }
            }
        }
    ];
}

function baseOfferColumns(): (Column | ColumnGroup)[] {
    return [
        {
            base: new GroupColumn(),
            header: "SKU",
            key: "sku",
            pinned: true
        },
        {
            header: "Информация",
            children: [
                {
                    base: imageColumn,
                    header: "Фото",
                    key: "photo"
                },
                {
                    base: stringColumn,
                    header: "Название",
                    key: "name"
                },
                {
                    base: stringColumn,
                    header: "Примечание 1",
                    key: "note_1",
                    editable: true,
                    columnGroupShow: "closed"
                },
                {
                    base: stringColumn,
                    header: "Примечание 2",
                    key: "note_2",
                    editable: true,
                    columnGroupShow: "closed"
                },
                {
                    base: stringColumn,
                    header: "Примечание 3",
                    key: "note_3",
                    editable: true,
                    columnGroupShow: "closed"
                },
                {
                    base: stringColumn,
                    key: "market",
                    header: "Площадка",
                    columnGroupShow: "closed"
                },
                {
                    base: stringColumn,
                    key: "name_of_shop",
                    header: "Название магазина",
                    columnGroupShow: "closed"
                }
            ]
        }
    ];
}
