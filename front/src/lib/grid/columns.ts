import type { ValueGetterParams } from "ag-grid-enterprise";
import type { Column, ColumnGroup } from "../components/datagrid/columns";
import type { Template } from "$lib/data/templates";
import type { FboStocks } from "$lib/data/fbo_storage";
import type { Offer } from "$lib/data/offers";
import type { Market } from "$lib/data/markets";
import type { OwnStorage } from "$lib/data/own_storage";

export function offerColumns(templates: Template[]): (Column | ColumnGroup)[] {
    return [
        ...baseOfferColumns(),
        {
            header: "Габариты (Собственные)",
            children: [
                { header: "Вес", key: "self_weight", data_type: "float", editable: true },
                { header: "Длина", key: "self_length", data_type: "float", editable: true },
                { header: "Ширина", key: "self_width", data_type: "float", editable: true },
                { header: "Высота", key: "self_height", data_type: "float", editable: true },
                {
                    key: "volume",
                    header: "Объём",
                    data_type: "float",
                    tooltip: "Длина * ширина * высота / 1000"
                }
            ]
        },
        {
            header: "Габариты (Маркет)",
            children: [
                { header: "Вес", key: "yandex_weight", data_type: "float" },
                { header: "Длина", key: "yandex_length", data_type: "float" },
                { header: "Ширина", key: "yandex_width", data_type: "float" },
                { header: "Высота", key: "yandex_height", data_type: "float" },
                {
                    key: "yandex_volume",
                    header: "Объём",
                    data_type: "float",
                    tooltip: "Длина * ширина * высота / 1000"
                },
                {
                    key: "volume_difference",
                    header: "Разница объемов",
                    data_type: "float"
                }
            ]
        },
        {
            header: "Ценообразование",
            children: [
                {
                    key: "use_manual_min_price",
                    header: "Использовать ручную мин. цену",
                    data_type: "boolean",
                    editable: true
                },
                {
                    key: "auto_min_price",
                    header: "Авто мин. цена (%)",
                    data_type: "percent",
                    editable: true
                },
                {
                    key: "auto_min_price_rubles",
                    header: "Авто мин. цена (руб)",
                    data_type: "ruble",
                    valueGetter: ({ data }: { data: Offer }) => {
                        if (data.total_price === null) return null;
                        return data.total_price * (data.auto_min_price / 100);
                    }
                },
                {
                    key: "manual_min_price",
                    header: "Ручная мин. цена",
                    data_type: "float",
                    editable: true
                },
                {
                    key: "auto_price_control",
                    header: "Авто контроль цен",
                    data_type: "boolean",
                    editable: true
                },
                {
                    key: "pricing_scheme_id",
                    header: "Схема ценообразования",
                    data_type: "combobox",
                    editable: true,
                    options: templates.map(t => ({ value: t.id, name: t.name }))
                },
                {
                    key: "your_price_for_buyers",
                    header: "Цена для покупателя",
                    data_type: "float"
                },
                {
                    key: "current_price",
                    header: "Текущая цена",
                    data_type: "float"
                },
                {
                    key: "dollar_cost_price",
                    header: "Закупка у. е.",
                    data_type: "dollar",
                    editable: true
                },
                {
                    key: "attractive_price_threshold",
                    header: "Порог для привлекательной цены",
                    data_type: "float"
                },
                {
                    key: "total_price_min_additional",
                    header: "Мин. наценка на расчетную цену",
                    data_type: "float",
                    editable: true
                },
                {
                    key: "discount_base_price",
                    header: "Цена до скидки",
                    data_type: "float",
                    tooltip: "Цена + 20%"
                },
                {
                    key: "profit",
                    header: "Прибыль",
                    data_type: "float",
                    tooltip: "Текущая цена - налог - FBY  - себестоимость"
                },
                {
                    key: "total_price_coeff",
                    header: "Коэффициент расчетной цены",
                    data_type: "float",
                    editable: true
                },
                {
                    key: "cost_price",
                    header: "Себестоимость",
                    data_type: "float",
                    tooltip: "Закупка у. е. * курс"
                },
                {
                    key: "best_place_wm",
                    header: "Площадка с лучшей ценой (без учета Маркета)",
                    data_type: "string"
                },
                {
                    key: "min_price_without_market",
                    header: "Цена площадки (без учета Маркета)",
                    data_type: "float"
                },
                {
                    key: "fby",
                    header: "Цена за FBY",
                    data_type: "float"
                },
                {
                    key: "total_price",
                    header: "Расчетная цена",
                    data_type: "float",
                    tooltip: "Закупка * коэф. ?+ мин. наценка"
                },
                {
                    key: "margin",
                    header: "Окупаемость",
                    data_type: "percent",
                    tooltip: "Прибыль / закупка * 100"
                },
                {
                    key: "moderately_attractive_price_threshold",
                    header: "Порог для умеренно привлекательной цены",
                    data_type: "float"
                },
                {
                    key: "best_place_im",
                    header: "Площадка с лучшей ценой (на Маркете)",
                    data_type: "string"
                },
                {
                    key: "min_price_in_market",
                    header: "Цена площадки (на Маркете)",
                    data_type: "float"
                },
                {
                    key: "min_general_markets_price",
                    header: "Минимальная цена в группе",
                    data_type: "float"
                },
                {
                    key: "target_price",
                    header: "Целевая цена",
                    data_type: "float"
                },
                {
                    key: "volume_profitability_ratio",
                    header: "Коэффициент прибыльности от объёма",
                    data_type: "float"
                },
                {
                    key: "days_to_zero_profit",
                    header: "Дней до нулевой прибыли",
                    data_type: "float"
                },
                {
                    key: "price_index",
                    header: "Индекс цены",
                    data_type: "string"
                }
            ]
        },
        {
            key: "remaining_stock",
            header: "Остатки на складах",
            data_type: "int"
        },
        {
            key: "content_rating",
            header: "Контент рейтинг",
            data_type: "float"
        },
        {
            key: "supplier_available",
            header: "Наличие у поставщика",
            data_type: "boolean",
            editable: true
        },
        { header: "Скрыт", key: "hidden", data_type: "boolean", editable: true }
    ];
}

export function ownStorageColumns(markets: Market[]): (Column | ColumnGroup)[] {
    const noteCols = ([1, 2, 3] as const).map(i => {
        return {
            header: `Примечание ${i}`,
            key: `note_${i}`,
            valueGetter: ({ data }: { data: OwnStorage }) =>
                data[`note_${i}`].filter(x => x !== "").join("; "),
            data_type: "string",
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
            data_type: "int"
        } as Column;
    });

    return [
        {
            header: "SKU",
            key: "sku",
            data_type: "string",
            pinned: true,
            cellRenderer: "agGroupCellRenderer"
        },
        {
            header: "Информация",
            children: [
                {
                    header: "Фото",
                    key: "photo",
                    data_type: "image",
                    valueGetter: ({ data }: { data: OwnStorage }) => {
                        if (data.photo === undefined || data.photo.length === 0) return null;
                        let photo = data.photo
                            .map(x => x ?? "")
                            .filter(x => x !== "")
                            .at(0);
                        return photo ?? null;
                    }
                },
                { header: "Название", key: "name.0", data_type: "string" },
                ...noteCols
            ]
        },
        {
            header: "Мой склад",
            key: "own_storage.value",
            data_type: "int",
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
                    data_type: "int",
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
                    data_type: "int",
                    valueGetter: (params: ValueGetterParams<FboStocks>) => {
                        if (!params.data) return 0;
                        return params.data.stocks.map(x => x.min_stock).reduce((a, b) => a + b, 0);
                    }
                },
                {
                    header: "К поставке",
                    key: "to_deliver",
                    data_type: "int",
                    valueGetter: (params: ValueGetterParams<FboStocks>) => {
                        if (!params.data) return 0;
                        return params.data.stocks
                            .map(x => Math.max(0, x.min_stock - x.current_stock))
                            .reduce((a, b) => a + b, 0);
                    }
                }
            ]
        },
        { header: "Скрыт", key: "hidden", data_type: "boolean", editable: true }
    ];
}

export function fboStorageColumns(): (Column | ColumnGroup)[] {
    return [
        { header: "Склад", key: "warehouse.name", data_type: "string" },
        {
            header: "В наличии",
            key: "current_stock",
            data_type: "int"
        },
        {
            header: "Мин. остаток",
            key: "min_stock",
            data_type: "int",
            editable: true
        },
        {
            header: "К поставке",
            key: "to_deliver",
            data_type: "int",
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
            header: "SKU",
            key: "sku",
            data_type: "string",
            pinned: true,
            cellRenderer: "agGroupCellRenderer"
        },
        {
            header: "Информация",
            children: [
                { header: "Фото", key: "photo", data_type: "image" },
                { header: "Название", key: "name", data_type: "string" },
                {
                    header: "Примечание 1",
                    key: "note_1",
                    data_type: "string",
                    editable: true,
                    columnGroupShow: "closed"
                },
                {
                    header: "Примечание 2",
                    key: "note_2",
                    data_type: "string",
                    editable: true,
                    columnGroupShow: "closed"
                },
                {
                    header: "Примечание 3",
                    key: "note_3",
                    data_type: "string",
                    editable: true,
                    columnGroupShow: "closed"
                },
                {
                    key: "market",
                    header: "Площадка",
                    data_type: "string",
                    columnGroupShow: "closed"
                },
                {
                    key: "name_of_shop",
                    header: "Название магазина",
                    data_type: "string",
                    columnGroupShow: "closed"
                }
            ]
        }
    ];
}
