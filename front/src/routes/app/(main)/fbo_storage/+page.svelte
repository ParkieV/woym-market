<script lang="ts">
    import { ChangeList } from "$lib/components/datagrid/changes";
    import {
        fetchFboStocks,
        patchFboStocks,
        type FboStocks,
        type FboStorage
    } from "$lib/data/fbo_storage";
    import type { OfferBase } from "$lib/data/offers";
    import type { GridOptions, IDetailCellRendererParams, GridApi } from "ag-grid-enterprise";
    import Footer from "../Footer.svelte";
    import Toolbar from "../Toolbar.svelte";
    import { fboStocksColumns, fboStorageColumns } from "$lib/columns";
    import { getContext, onMount } from "svelte";
    import { getColumns } from "$lib/components/datagrid/columns";
    import Grid from "$lib/components/datagrid/Grid.svelte";
    import type { Writable } from "svelte/store";
    import { userCanModify } from "$lib/user";

    let data: FboStocks[] = [];
    let changes = new ChangeList<FboStocks, "id">();
    let filter: (storage: OfferBase) => boolean = () => true;

    const columns = fboStocksColumns();
    const detailColumns = fboStorageColumns();

    const options: GridOptions = {
        masterDetail: true,
        detailCellRendererParams: (params: { api: GridApi; data: FboStocks }) => {
            let { api, data } = params;
            return {
                detailGridOptions: {
                    columnDefs: getColumns(detailColumns, {
                        onPhotoClicked: () => {},
                        isRowChanged: () => false,
                        readonly: !$userCanModify
                    }),
                    autoSizeStrategy: { type: "fitCellContents" },
                    suppressMovableColumns: true,
                    enableRangeSelection: true,
                    enableRangeHandle: true,
                    getContextMenuItems: () => ["cut", "copy", "paste"],
                    onCellValueChanged: _ => {
                        changes.add(data.id);
                        changes = changes;
                        api.redrawRows();
                    }
                },
                getDetailRowData: params => {
                    params.successCallback(params.data.stocks);
                }
            } satisfies Partial<IDetailCellRendererParams<FboStocks, FboStorage>>;
        }
    };

    async function refreshData() {
        changes.clear();
        changes = changes;
        data = await fetchFboStocks();
    }

    async function save() {
        let ok = await patchFboStocks(data.filter(x => changes.isChanged(x.id)));
        if (ok) await refreshData();
    }

    let refresh = getContext<Writable<() => {}>>("refresh");
    $refresh = refreshData;

    onMount(async () => {
        data = await fetchFboStocks();
    });
</script>

<Toolbar on:filterChanged={f => (filter = f.detail)} />
<Grid
    key="id"
    grid_name="fbo_storage"
    {columns}
    bind:data
    bind:changes
    bind:filter
    otherGridOptions={options}
/>
<Footer bind:changes on:reload={refreshData} on:save={save} />
