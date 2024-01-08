import type { Offer } from "$lib";
import type { CellClassParams, ColDef, ColGroupDef, GridOptions } from "ag-grid-community";
import { numberColumnDefinition } from "./util";

export function DataGridOptions(init: {
    search: () => string;
    onPhotoClicked: (src: string) => void;
    onOfferChanged?: (value: Offer) => void;
    isOfferChanged?: (sku: string) => boolean;
}): GridOptions<Offer> {
    const isOfferChanged = init.isOfferChanged ? init.isOfferChanged : () => false;
    const changedClass = (e: CellClassParams<Offer>) =>
        isOfferChanged(e.data!.sku) ? "changed" : [];

    return {
        suppressDragLeaveHidesColumns: true,
        autoSizeStrategy: { type: "fitCellContents" },
        columnDefs: columnDefs(),
        columnTypes: {
            editable: {
                cellClass: "editable",
                editable: true
            }
        },
        rowHeight: 75,
        isExternalFilterPresent: () => init.search.length == 0,
        doesExternalFilterPass: e => filter(init.search(), e.data!),
        onCellValueChanged: e => {
            if (init.onOfferChanged) init.onOfferChanged(e.data);
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
                cellClass: changedClass
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
                        onCellClicked: e => {
                            if (e.value) {
                                init.onPhotoClicked(e.value.toString());
                            }
                        }
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
                ]
            },
            {
                headerName: "Цена",
                children: [
                    {
                        ...numberColumnDefinition("total_price", { kind: "money", currency: "₽" }),
                        headerName: "Расчётная цена",
                        headerTooltip: "Закупка * коэф. + мин. наценка"
                    },
                    {
                        ...numberColumnDefinition("current_price", {
                            kind: "money",
                            currency: "₽"
                        }),
                        headerName: "Текущая цена"
                    },
                    {
                        ...numberColumnDefinition("cost_price", { kind: "money", currency: "₽" }),
                        headerName: "Закупка",
                        columnGroupShow: "open",
                        headerTooltip: "Закупка у. е. * курс"
                    },
                    {
                        ...numberColumnDefinition(
                            "dollar_cost_price",
                            { kind: "money", currency: "$" },
                            true
                        ),
                        headerName: "Закупка (у. е.)",
                        columnGroupShow: "open"
                    },
                    {
                        ...numberColumnDefinition(
                            "total_price_min_additional",
                            { kind: "money", currency: "₽" },
                            true
                        ),
                        headerName: "Минимальная наценка",
                        wrapHeaderText: true,
                        columnGroupShow: "open"
                    },
                    {
                        ...numberColumnDefinition(
                            "total_price_coeff",
                            { kind: "number", precision: 2 },
                            true
                        ),
                        headerName: "Коэффициент",
                        columnGroupShow: "open"
                    },
                    {
                        ...numberColumnDefinition("discount_base_price", {
                            kind: "money",
                            currency: "₽"
                        }),
                        headerName: "Цена до скидки",
                        columnGroupShow: "open",
                        headerTooltip: "Цена + 20%"
                    },
                    {
                        ...numberColumnDefinition("profit", { kind: "money", currency: "₽" }),
                        headerName: "Прибыль",
                        columnGroupShow: "open",
                        headerTooltip: "Цена - закупка - FBY"
                    },
                    {
                        ...numberColumnDefinition("margin", { kind: "percent" }),
                        headerName: "Окупаемость",
                        columnGroupShow: "open",
                        headerTooltip: "Прибыль / закупка * 100"
                    },
                    {
                        ...numberColumnDefinition("fby", { kind: "money", currency: "₽" }),
                        headerName: "FBY",
                        columnGroupShow: "open"
                    },
                    {
                        ...numberColumnDefinition("minimum_group_price", {
                            kind: "money",
                            currency: "₽"
                        }),
                        headerName: "Мин. цена в группе",
                        columnGroupShow: "open"
                    },
                    {
                        ...numberColumnDefinition(
                            "auto_min_price",
                            {
                                kind: "percent"
                            },
                            true
                        ),
                        headerName: "Авто мин. цена %",
                        columnGroupShow: "open"
                    },
                    {
                        ...numberColumnDefinition(
                            "manual_min_price",
                            { kind: "money", currency: "₽" },
                            true
                        ),
                        headerName: "Ручная мин. цена",
                        columnGroupShow: "open"
                    }
                ]
            },
            { field: "name_of_shop", headerName: "Название магазина" },
            {
                ...numberColumnDefinition("remaining_stock", { kind: "number", precision: 0 }),
                headerName: "Остаток на складе",
                wrapHeaderText: true,
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

function filter(search: string, offer: Offer): boolean {
    const normalize = (term: string | null | undefined) =>
        term ? term.trim().toLowerCase().replaceAll("ё", "е") : "";

    const _search = normalize(search);
    return (
        normalize(offer.name).includes(_search) ||
        normalize(offer.sku).includes(_search) ||
        normalize(offer.note_1).includes(_search) ||
        normalize(offer.note_2).includes(_search) ||
        normalize(offer.note_3).includes(_search) ||
        normalize(offer.name_of_shop).includes(_search)
    );
}
