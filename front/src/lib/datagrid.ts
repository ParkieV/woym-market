import type { ColDef, ColGroupDef, GridOptions } from "ag-grid-community";

export function DataGridOptions(rowData: any): GridOptions {
    return {
        suppressDragLeaveHidesColumns: true,
        autoSizeStrategy: { type: "fitCellContents" },
        rowData,
        columnDefs: columnDefs(),
        rowHeight: 75
    };
}

function columnDefs(): (ColDef | ColGroupDef)[] {
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
                    cellClass: "product-photo-cell"
                },
                { field: "name", headerName: "Название" },
                {
                    field: "notation1",
                    headerName: "Прим. 1",
                    editable: true,
                    columnGroupShow: "open"
                },
                {
                    field: "notation2",
                    headerName: "Прим. 2",
                    editable: true,
                    columnGroupShow: "open"
                },
                {
                    field: "notation3",
                    headerName: "Прим. 3",
                    editable: true,
                    columnGroupShow: "open"
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
                        return `${p.data.length}x${p.data.width}x${p.data.height}`;
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
                        return (p.data.length * p.data.width * p.data.height).toFixed(4);
                    }
                },
                { field: "volume_from_yandex", headerName: "Объём (Яндекс)" }
            ]
        },
        {
            headerName: "Цена",
            children: [
                {
                    field: "settlement_price",
                    headerName: "Расчётная цена",
                    valueFormatter: params => `${params.value}₽`
                },
                {
                    field: "market_price",
                    headerName: "Цена на маркете",
                    valueFormatter: params => `${params.value}₽`
                },
                {
                    field: "parches",
                    headerName: "Закупка (у. е.)",
                    editable: true,
                    cellEditor: "agNumberCellEditor:",
                    columnGroupShow: "open"
                },
                {
                    field: "cost_price",
                    headerName: "Закупка",
                    valueFormatter: params => `${params.value}₽`,
                    columnGroupShow: "open"
                },
                {
                    field: "minimum_markup",
                    headerName: "Минимальная наценка",
                    wrapHeaderText: true,
                    editable: true,
                    valueFormatter: params => `${params.value}₽`,
                    cellEditor: "agNumberCellEditor:",
                    columnGroupShow: "open"
                },
                {
                    field: "settlement_price_factor",
                    headerName: "Коэффициент",
                    editable: true,
                    cellEditor: "agNumberCellEditor:",
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
                { field: "minimum_group_price", headerName: "Мин. цена в группе" },
                { field: "group_sellers_amount", headerName: "Продавцов в группе" }
            ]
        },
        { field: "name_of_shop", headerName: "Название магазина" },
        {
            field: "remaining_stock",
            headerName: "Остаток на складе",
            wrapHeaderText: true,
            width: 105,
        },
        {
            field: "automatic_price_management",
            headerName: "Автоматическое управление ценами",
            editable: true,
            wrapHeaderText: true
        },
        {
            field: "manual_control_min_price",
            headerName: "Ручное управление мин. ценой",
            editable: true,
            wrapHeaderText: true
        }
    ];
}
