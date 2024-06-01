import type { Column, ColumnGroup } from "$lib/components/datagrid/columns";
import type { ValueGetterParams } from "ag-grid-enterprise";
import type { FboStocks } from "$lib/data/fbo_storage";

import { BooleanColumn, intColumn } from "$lib/components/datagrid/columns/types";
import baseOfferColumns from "../base";

export default function fboOffersColumns(): (Column | ColumnGroup)[] {
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
                }
            ]
        },
        { header: "Скрыт", key: "hidden", base: new BooleanColumn(), editable: true }
    ];
}
