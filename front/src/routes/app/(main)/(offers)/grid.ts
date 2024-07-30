import { BASE_GRID_OPTIONS } from "$lib/grid/base";
import { GridDefinition } from "$lib/datagrid";
import type { Column, ColumnGroup } from "$lib/datagrid/columns";
import type { Template } from "$lib/data/templates";
import type { Offer } from "$lib/data/offers";
import {
    ComboboxColumn,
    BooleanColumn,
    StringColumn,
    DateColumn,
    dollarColumn,
    floatColumn,
    intColumn,
    percentColumn,
    rubleColumn,
    GroupColumn,
    ImageColumn
} from "$lib/datagrid/columns/types";

export default function offerGrid(templates: Template[]): GridDefinition<Offer> {
    return new GridDefinition(BASE_GRID_OPTIONS, columns(templates));
}

function columns(templates: Template[]): (Column | ColumnGroup)[] {
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
                    base: new ImageColumn(),
                    header: "Фото",
                    key: "photo"
                },
                {
                    base: new StringColumn(),
                    header: "Название",
                    key: "name"
                },
                {
                    base: new StringColumn(),
                    key: "barcodes",
                    header: "Штрихкоды",
                    columnGroupShow: "closed"
                },
                {
                    base: new StringColumn(),
                    header: "Примечание 1",
                    key: "note_1",
                    editable: true,
                    columnGroupShow: "closed"
                },
                {
                    base: new StringColumn(),
                    header: "Примечание 2",
                    key: "note_2",
                    editable: true,
                    columnGroupShow: "closed"
                },
                {
                    base: new StringColumn(),
                    header: "Примечание 3",
                    key: "note_3",
                    editable: true,
                    columnGroupShow: "closed"
                },
                {
                    base: new StringColumn({
                        kind: "agLargeTextCellEditor",
                        cols: 80,
                        rows: 4,
                        maxLength: 255
                    }),
                    header: "Поисковые слова",
                    key: "search_words",
                    editable: true,
                    columnGroupShow: "closed"
                },
                {
                    base: new StringColumn(),
                    key: "market",
                    header: "Площадка",
                    columnGroupShow: "closed"
                },
                {
                    base: new StringColumn(),
                    key: "name_of_shop",
                    header: "Название магазина",
                    columnGroupShow: "closed"
                }
            ]
        },
        {
            header: "Габариты (Собственные)",
            children: [
                { header: "Вес, кг", key: "self_weight", base: floatColumn, editable: true },
                { header: "Длина, см", key: "self_length", base: floatColumn, editable: true },
                { header: "Ширина, см", key: "self_width", base: floatColumn, editable: true },
                { header: "Высота, см", key: "self_height", base: floatColumn, editable: true },
                {
                    key: "volume",
                    header: "Объём, л",
                    base: floatColumn,
                    tooltip: "Длина * ширина * высота / 1000"
                }
            ]
        },
        {
            header: "Габариты (Маркет)",
            children: [
                { header: "Вес, кг", key: "yandex_weight", base: floatColumn },
                { header: "Длина, см", key: "yandex_length", base: floatColumn },
                { header: "Ширина, см", key: "yandex_width", base: floatColumn },
                { header: "Высота, см", key: "yandex_height", base: floatColumn },
                {
                    key: "yandex_volume",
                    header: "Объём, л",
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
                    base: rubleColumn,
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
                    base: rubleColumn
                },
                {
                    key: "current_price",
                    header: "Текущая цена",
                    base: rubleColumn
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
                    base: rubleColumn
                },
                {
                    key: "total_price_min_additional",
                    header: "Мин. наценка на расчетную цену",
                    base: rubleColumn,
                    editable: true
                },
                {
                    key: "discount_base_price",
                    header: "Цена до скидки",
                    base: rubleColumn,
                    tooltip: "Цена + 20%"
                },
                {
                    key: "profit",
                    header: "Прибыль",
                    base: rubleColumn,
                    tooltip: "Ваша цена по акции - налог - FBO - себестоимость"
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
                    base: rubleColumn,
                    tooltip: "Закупка у. е. * курс"
                },
                {
                    key: "best_place_wm",
                    header: "Площадка с лучшей ценой (без учета Маркета)",
                    base: new StringColumn()
                },
                {
                    key: "min_price_without_market",
                    header: "Цена площадки (без учета Маркета)",
                    base: rubleColumn
                },
                {
                    key: "fbo",
                    header: "Цена за FBO",
                    tooltip:
                        "Комиссия за продажу в FBO (%) + Цена доп. логистики за превышение порога хранения",
                    base: rubleColumn
                },
                {
                    key: "total_price",
                    header: "Расчетная цена",
                    base: rubleColumn,
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
                    base: rubleColumn
                },
                {
                    key: "best_place_im",
                    header: "Площадка с лучшей ценой (на Маркете)",
                    base: new StringColumn()
                },
                {
                    key: "min_price_in_market",
                    header: "Цена площадки (на Маркете)",
                    base: rubleColumn
                },
                {
                    key: "min_general_markets_price",
                    header: "Минимальная цена в группе",
                    base: rubleColumn
                },
                {
                    key: "target_price",
                    header: "Целевая цена",
                    base: rubleColumn
                },
                {
                    key: "volume_profitability_ratio",
                    header: "Коэффициент прибыльности от объёма",
                    tooltip: "Прибыль / объём",
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
                    base: new StringColumn()
                },
                {
                    key: "market_discount_in_percent",
                    header: "Скидка маркета в %",
                    tooltip: '100 - "цена для покупателей" * 100 / "текущая цена"',
                    base: floatColumn
                },
                {
                    key: "dollar_cost_price_updated_at",
                    header: "Дата обновления цены закупки (у. е.)",
                    base: new DateColumn()
                },
                {
                    key: "use_promotion_price",
                    header: "Акция",
                    base: new BooleanColumn(),
                    editable: true
                },
                {
                    key: "wholesale_dollar_cost_price",
                    header: "ОПТ у. е.",
                    base: dollarColumn
                },
                {
                    key: "vendor_code",
                    header: "ID Артикул",
                    base: intColumn
                },
                {
                    key: "recommended_retail_price",
                    header: "РРЦ",
                    base: rubleColumn
                },
                {
                    key: "stop_price",
                    header: "Стоп цена",
                    base: rubleColumn
                },
                {
                    key: "difference_from_recommended_retail_price",
                    header: "Разница с РРЦ",
                    base: rubleColumn
                },
                {
                    key: "violator",
                    header: "Нарушители РРЦ",
                    base: new StringColumn()
                },
                {
                    key: "your_promotion_price",
                    header: "Ваша цена по акции",
                    base: rubleColumn
                },
                {
                    key: "auto_participation_in_promotions",
                    header: "Автоучастие в акциях",
                    base: new BooleanColumn(),
                    editable: true
                }
            ]
        },
        {
            key: "remaining_stock",
            header: "Остатки на складах",
            base: intColumn
        },
        {
            key: "content_rating",
            header: "Контент-рейтинг",
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
