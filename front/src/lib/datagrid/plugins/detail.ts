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
            const func = this.detail.options.onCellValueChanged;
            return {
                detailGridOptions: {
                    ...this.detail.options,
                    onGridReady: (e: GridReadyEvent) => {
                        if (data !== null && data !== undefined && ('id' in data)) {
                            this.apiMap?.set(data?.id as number, e.api);
                        }
                    },
                    onCellValueChanged: e => {
                        func?.(e);
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
