import type { Offer } from "$lib";
import type { ColDef, ColGroupDef, GridOptions } from "ag-grid-community";
import { notNullFieldColumn } from "./util";

export function DataGridOptions(onPhotoClicked: (src: string) => void): GridOptions<Offer> {
    return {
        suppressDragLeaveHidesColumns: true,
        autoSizeStrategy: { type: "fitCellContents" },
        columnDefs: columnDefs(),
        columnTypes: {
            editable: {
                headerClass: "editable-column-header",
                editable: true
            }
        },
        rowHeight: 75
    };

    function columnDefs(): (ColDef<Offer> | ColGroupDef<Offer>)[] {
        return [
            {
                field: "sku",
                headerName: "SKU",
                lockPosition: "left",
                pinned: "left"
            },
            {
                headerName: "Информация",
                children: [
                    {
                        field: "photo",
                        headerName: "Фото",
                        width: 75,
                        cellRenderer: (params: any) =>
                            params.value != null ? `<img src="${params.value}" />` : "",
                        cellClass: "product-photo-cell",
                        onCellClicked: e => onPhotoClicked(e.value.toString())
                    },
                    { field: "name", headerName: "Название" },
                    {
                        field: "note_1",
                        headerName: "Прим. 1",
                        columnGroupShow: "open",
                        type: "editable"
                    },
                    {
                        field: "note_2",
                        headerName: "Прим. 2",
                        columnGroupShow: "open",
                        type: "editable"
                    },
                    {
                        field: "note_3",
                        headerName: "Прим. 3",
                        columnGroupShow: "open",
                        type: "editable"
                    }
                ]
            },
            {
                headerName: "Габариты",
                children: [
                    { field: "weight", headerName: "Вес" },
                    {
                        headerName: "Размеры",
                        valueGetter: p => {
                            return `${p.data!.length}x${p.data!.width}x${p.data!.height}`;
                        },
                        columnGroupShow: "closed",
                        sortable: false
                    },
                    { field: "length", headerName: "Длина", columnGroupShow: "open", width: 100 },
                    { field: "width", headerName: "Ширина", columnGroupShow: "open", width: 100 },
                    { field: "height", headerName: "Высота", columnGroupShow: "open", width: 100 },
                    {
                        headerName: "Объём",
                        valueGetter: p => {
                            return (p.data!.length * p.data!.width * p.data!.height).toFixed(4);
                        }
                    }
                    // TODO: Uncomment after backend fix lands.
                    // { field: "volume_yandex", headerName: "Объём (Яндекс)" }
                ]
            },
            {
                headerName: "Цена",
                children: [
                    {
                        field: "total_price",
                        headerName: "Расчётная цена",
                        valueFormatter: params => `${params.value}₽`
                    },
                    {
                        field: "current_price",
                        headerName: "Текущая цена",
                        valueFormatter: params => `${params.value}₽`
                    },
                    {
                        field: "cost_price",
                        headerName: "Закупка",
                        valueFormatter: params => `${params.value}₽`,
                        columnGroupShow: "open"
                    },
                    {
                        ...editable_money_column("dollar_cost_price", "$"),
                        headerName: "Закупка (у. е.)",
                        columnGroupShow: "open"
                    },
                    {
                        ...editable_money_column("total_price_min_additional", "₽"),
                        headerName: "Минимальная наценка",
                        wrapHeaderText: true,
                        columnGroupShow: "open"
                    },
                    {
                        field: "total_price_coeff",
                        headerName: "Коэффициент",
                        type: "editable",
                        cellEditor: "agNumberCellEditor",
                        columnGroupShow: "open"
                    },
                    {
                        field: "price_before_discount",
                        headerName: "Цена до скидки",
                        valueFormatter: params => `${params.value}₽`,
                        columnGroupShow: "open"
                    },
                    {
                        field: "profit",
                        headerName: "Прибыль",
                        valueFormatter: params => `${params.value}₽`,
                        columnGroupShow: "open"
                    },
                    {
                        field: "payback",
                        headerName: "Окупаемость",
                        columnGroupShow: "open"
                    },
                    {
                        field: "fby",
                        headerName: "FBY",
                        valueFormatter: params => `${params.value}₽`,
                        columnGroupShow: "open"
                    }
                ]
            },
            {
                headerName: "Группа",
                children: [
                    { field: "minimum_group_price", headerName: "Мин. цена в группе" }
                    // TODO: Uncomment after backend fix lands.
                    // { field: "group_sellers_amount", headerName: "Продавцов в группе" }
                ]
            },
            { field: "name_of_shop", headerName: "Название магазина" },
            {
                field: "remaining_stock",
                headerName: "Остаток на складе",
                wrapHeaderText: true,
                width: 105
            },
            {
                field: "auto_price_control",
                headerName: "Автоматическое управление ценами",
                wrapHeaderText: true,
                width: 200,
                type: "editable"
            },
            {
                field: "use_manual_min_price",
                headerName: "Ручное управление мин. ценой",
                wrapHeaderText: true,
                type: "editable"
            }
        ];
    }
}

function editable_money_column(field: keyof Offer, currency: string = ""): ColDef<Offer> {
    return {
        ...notNullFieldColumn(field),
        cellEditor: "agNumberCellEditor",
        cellEditorParams: {
            min: 0,
            step: 0.25,
            precision: 2
        },
        type: "editable",
        cellClass: "ag-right-aligned-cell",
        valueFormatter: params => `${params.value}${currency}`
    };
}
