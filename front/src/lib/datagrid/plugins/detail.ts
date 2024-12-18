import type { GridDefinition, MyGridOptions } from "$lib/datagrid";
import type { GridPlugin } from "$lib/datagrid/plugins";
import type { IDetailCellRendererParams } from "ag-grid-enterprise";

/** Adds provided `GridDefinition` as a detail grid. */
export default class DetailGridPlugin<TData, TDetail> implements GridPlugin<TData> {
    constructor(
        private detail: GridDefinition<TDetail>,
        private map: (data: TData) => TDetail[] | Promise<TDetail[]>
    ) {}

    async init(opts: MyGridOptions<TData>): Promise<void> {
        for (const plugin of this.detail.plugins) {
            plugin.init?.(this.detail.options);
        }

        opts.masterDetail = true;
        opts.detailCellRendererParams = ({ api }: IDetailCellRendererParams<TData, TDetail>) => {
            let func = this.detail.options.onCellValueChanged;
            return {
                detailGridOptions: {
                    ...this.detail.options,
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
