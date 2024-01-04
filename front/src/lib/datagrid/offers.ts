import type { Offer } from "$lib";
import type { ColDef, ColGroupDef, GridOptions, IRowNode } from "ag-grid-community";
import { notNullFieldColumn } from "./util";

export function DataGridOptions(init: {
    onPhotoClicked: (src: string) => void;
    changed: Map<string, Offer>;
    isFilterEnabled: () => boolean;
    filter: (offer: IRowNode<Offer>) => boolean;
}): GridOptions<Offer> {
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
        rowHeight: 75,
        isExternalFilterPresent: init.isFilterEnabled,
        doesExternalFilterPass: init.filter,
        onCellValueChanged: e => {
            init.changed.set(e.data.sku, e.data);
            e.api.redrawRows({ rowNodes: [e.node] });
        }
    };

    function columnDefs(): (ColDef<Offer> | ColGroupDef<Offer>)[] {
        return [
            {
                field: "sku",
                headerName: "SKU",
                lockPosition: "left",
                pinned: "left",
                cellClass: params => {
                    if (init.changed.has(params.value)) {
                        return ["changed"];
                    } else {
                        return [];
                    }
                }
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
                        onCellClicked: e => init.onPhotoClicked(e.value.toString())
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
                        ...money_column("total_price", "₽"),
                        headerName: "Расчётная цена"
                    },
                    {
                        ...money_column("current_price", "₽"),
                        headerName: "Текущая цена"
                    },
                    {
                        ...money_column("cost_price", "₽"),
                        headerName: "Закупка",
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
                        ...notNullFieldColumn("total_price_coeff"),
                        headerName: "Коэффициент",
                        type: "editable",
                        cellEditor: "agNumberCellEditor",
                        cellEditorParams: {
                            min: 0
                        },
                        cellClass: "ag-right-aligned-cell",
                        columnGroupShow: "open"
                    },
                    {
                        ...money_column("discount_base_price", "₽"),
                        headerName: "Цена до скидки",
                        columnGroupShow: "open"
                    },
                    {
                        ...money_column("profit", "₽"),
                        headerName: "Прибыль",
                        columnGroupShow: "open"
                    },
                    {
                        field: "payback",
                        headerName: "Окупаемость",
                        columnGroupShow: "open",
                        cellClass: "ag-right-aligned-cell"
                    },
                    {
                        ...money_column("fby", "₽"),
                        headerName: "FBY",
                        columnGroupShow: "open"
                    }
                ]
            },
            {
                headerName: "Группа",
                children: [
                    {
                        ...money_column("minimum_group_price", "₽"),
                        headerName: "Мин. цена в группе"
                    }
                    // TODO: Uncomment after backend fix lands.
                    // { field: "group_sellers_amount", headerName: "Продавцов в группе" }
                ]
            },
            { field: "name_of_shop", headerName: "Название магазина" },
            {
                field: "remaining_stock",
                headerName: "Остаток на складе",
                wrapHeaderText: true,
                cellClass: "ag-right-aligned-cell",
                initialWidth: 120
            },
            {
                field: "auto_price_control",
                headerName: "Автоматическое управление ценами",
                wrapHeaderText: true,
                initialWidth: 200,
                type: "editable"
            },
            {
                field: "use_manual_min_price",
                headerName: "Ручное управление мин. ценой",
                wrapHeaderText: true,
                initialWidth: 200,
                type: "editable"
            }
        ];
    }
}

function money_column(field: keyof Offer, currency: string): ColDef<Offer> {
    return {
        field,
        cellClass: "ag-right-aligned-cell",
        valueFormatter: params =>
            params.value === null ? "N/A" : `${params.value.toFixed(2)} ${currency}`
    };
}

function editable_money_column(field: keyof Offer, currency: string): ColDef<Offer> {
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
        valueFormatter: params => `${params.value.toFixed(2)} ${currency}`
    };
}
