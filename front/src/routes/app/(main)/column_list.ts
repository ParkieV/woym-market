import type { Column, ColumnGroup } from "$lib/components/datagrid/columns";
import type { Template } from "../templates/+page.svelte";

export default function columnList(templates: Template[]): (Column | ColumnGroup)[] {
    return [
        { header: "SKU", key: "sku", data_type: "string", pinned: true },
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
                    data_type: "string"
                },
                {
                    key: "name_of_shop",
                    header: "Название магазина",
                    data_type: "string"
                }
            ]
        },
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
                    header: "Авто мин. цена %",
                    data_type: "percent",
                    editable: true
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
                    tooltip: "Цена - закупка - FBY"
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
                }
            ]
        },
        {
            key: "remaining_stock",
            header: "Остатки на складах",
            data_type: "int"
        },
        { header: "Скрыт", key: "hidden", data_type: "boolean", editable: true }
    ];
}
