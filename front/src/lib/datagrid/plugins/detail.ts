import type { GridDefinition, MyGridOptions } from "$lib/datagrid";
import type { GridPlugin } from "$lib/datagrid/plugins";
import type { GridReadyEvent, IDetailCellRendererParams } from "ag-grid-enterprise";

/** Adds provided `GridDefinition` as a detail grid. */
export default class DetailGridPlugin<TData, TDetail> implements GridPlugin<TData> {
    constructor(
        private detail: GridDefinition<TDetail>,
        private map: (data: TData) => TDetail[] | Promise<TDetail[]>,
        private apiMap?: Map<number, any>
    ) {}

    async init(opts: MyGridOptions<TData>): Promise<void> {
        for (const plugin of this.detail.plugins) {
            plugin.init?.(this.detail.options);
        }

        opts.masterDetail = true;
        opts.detailCellRendererParams = (params: IDetailCellRendererParams<TData, TDetail>) => {
            const { api: api, data } = params;
            const onCellChanged = this.detail.options.onCellValueChanged;
            const onReadyOriginal = this.detail.options.onGridReady;
            const onRowSelectedOriginal = this.detail.options.onRowSelected;
            const onSelectionChangedOriginal = this.detail.options.onSelectionChanged;
            return {
                detailGridOptions: {
                    ...this.detail.options,
                    onGridReady: (e: GridReadyEvent) => {
                        if (data !== null && typeof data === 'object' && 'id' in (data as object)) {
                            this.apiMap?.set((data as any)?.id as number, e.api);
                        }
                        onReadyOriginal?.(e);
                    },
                    onSelectionChanged: e => {
                        onSelectionChangedOriginal?.(e);
                        // When selection in any detail grid changes, refresh master summary
                        api.dispatchEvent({ type: "refreshSummary" });
                    },
                    onRowSelected: e => {
                        onRowSelectedOriginal?.(e);
                        // reflect selection changes in master summary
                        api.dispatchEvent({ type: "refreshSummary" });
                    },
                    onCellValueChanged: e => {
                        onCellChanged?.(e);
                        api.dispatchEvent({ type: "refreshSummary" });
                        api.refreshCells({ force: true });
                    }
                },
                getDetailRowData: async params =>
                    params.successCallback(await this.map(params.data))
            } satisfies Partial<IDetailCellRendererParams<TData, TDetail>>;
        };
    }
}
