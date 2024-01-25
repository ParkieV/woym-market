import type { Offer } from "$lib/data/offers";
import type { ColDef, GridOptions } from "ag-grid-community";
import { getColumns } from "./columns";

export async function DataGridOptions(init: {
    onPhotoClicked: (src: string) => void;
    onOfferChanged?: (value: Offer) => void;
    isOfferChanged?: (sku: string) => boolean;
}): Promise<GridOptions<Offer>> {
    const isOfferChanged = init.isOfferChanged ? init.isOfferChanged : () => false;

    let columnDefs: ColDef<Offer>[] = await getColumns({
        onPhotoClicked: init.onPhotoClicked,
        isRowChanged: (offer: Offer) => isOfferChanged(offer.sku)
    });

    return {
        columnDefs,
        suppressDragLeaveHidesColumns: true,
        autoSizeStrategy: { type: "fitCellContents" },
        rowHeight: 75,
        onCellValueChanged: e => {
            if (init.onOfferChanged) init.onOfferChanged(e.data);
            e.api.redrawRows({ rowNodes: [e.node] });
        },
        tooltipShowDelay: 500
    };
}
