<script lang="ts">
    import { ChangeList } from "$lib/components/datagrid/changes";
    import { fetchFboStocks, type FboStocks, type FboStorage } from "$lib/data/fbo_storage";
    import type { OfferBase } from "$lib/data/offers";
    import type { GridOptions, IDetailCellRendererParams, GridApi } from "ag-grid-enterprise";
    import Footer from "../Footer.svelte";
    import Toolbar from "../Toolbar.svelte";
    import { fboStocksColumns, fboStorageColumns } from "$lib/columns";
    import { onMount } from "svelte";
    import { getColumns } from "$lib/components/datagrid/columns";
    import Grid from "$lib/components/datagrid/Grid.svelte";

    let data: FboStocks[] = [];
    let changes = new ChangeList<FboStocks, "sku">();
    let filter: (storage: OfferBase) => boolean = () => true;

    const columns = fboStocksColumns();
    const detailColumns = fboStorageColumns();

    const options: GridOptions = {
        masterDetail: true,
        detailCellRendererParams: (params: { api: GridApi; data: FboStocks }) => {
            let { api, data } = params;
            return {
                detailGridOptions: {
                    suppressMovableColumns: true,
                    columnDefs: getColumns(detailColumns, {
                        onPhotoClicked: () => {},
                        isRowChanged: () => false
                    }),
                    onCellValueChanged: _ => {
                        changes.add(data.sku);
                        changes = changes;
                        api.redrawRows();
                    }
                },
                getDetailRowData: params => {
                    params.successCallback(params.data.storages);
                }
            } satisfies Partial<IDetailCellRendererParams<FboStocks, FboStorage>>;
        }
    };

    onMount(async () => {
        data = await fetchFboStocks();
    });
</script>

<Toolbar on:filterChanged={f => (filter = f.detail)} />
<Grid
    key="sku"
    grid_name="fbo_storage"
    {columns}
    bind:data
    bind:changes
    bind:filter
    otherGridOptions={options}
/>
<Footer bind:changes />
