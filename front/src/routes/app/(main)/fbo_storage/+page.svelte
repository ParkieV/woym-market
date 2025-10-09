<script lang="ts">
    import { type FboStorage, patchFboStocks, patchFboStocksOffers } from "$lib/data/fbo_storage";
    import Footer from "../Footer.svelte";
    import Grid from "$lib/grid/Grid.svelte";
    import { get } from "svelte/store";
    import ImageWindow from "$lib/components/windows/ImageWindow.svelte";
    import fboOffersGrid, { detailApiMap } from "./fbo-offer";
    import { userCanModify } from "$lib/data/user";
    import Toolbar from "./Toolbar.svelte";
    import fboStocks, { calcToDeliver } from "./fbo-stocks";
    import { browser } from "$app/environment";
    import ChangesPlugin from "$lib/datagrid/plugins/changes";
    import ReadonlyPlugin from "$lib/datagrid/plugins/readonly";
    import ClassesPlugin from "$lib/datagrid/plugins/classes";
    import RowSelectionPlugin from "$lib/datagrid/plugins/row-selection";
    import DetailGridPlugin from "$lib/datagrid/plugins/detail";
    import FilterPlugin from "$lib/datagrid/plugins/filter";
    import { SummaryPlugin } from "$lib/datagrid/plugins/summary";
    import { fboState, fboStocksChanges } from "../state";
    import ZoomPlugin from "$lib/datagrid/plugins/zoom";
    import { onMount } from "svelte";
    import StatePlugin from "$lib/datagrid/plugins/state";
    import { fboStocksFilter, fboStorageFilter } from "./filter";
    import { fboStocksSelection, fboStorageSelection } from "../selection";

    let selected_image: string | undefined = undefined;

    onMount(() => fboState.load());

    async function save() {
        const changed_offers = $fboState.filter(x => get(fboState.changes).isChanged(x.id))
        const changed_stocks = changed_offers.map(x => x.stocks).flat();
        const offer_ok = await patchFboStocksOffers(changed_offers);
        let stock_ok = false
        if (offer_ok) {
            (changed_stocks.length > 0)
            ? stock_ok = await patchFboStocks(changed_stocks)
            : true;
        }
        if (offer_ok && stock_ok) {
            fboState.apply();
            fboStocksChanges.clear();
        }
    }
    const definition = (() => {
        const detail = fboStocks()
            .plugin(new FilterPlugin(fboStocksFilter))
            .plugin(
                new ChangesPlugin(
                    x => x.id,
                    fboStocksChanges,
                    ({ data: storage }) => {
                        let stock = get(fboState).find(x =>
                            x.stocks.some(s => s.id === storage.id)
                        );
                        if (stock) fboState.changes.add(stock.id);
                    }
                )
            )
            .plugin(new ReadonlyPlugin(!$userCanModify))
            .plugin(new ClassesPlugin())
            .plugin(
                new RowSelectionPlugin(fboStocksSelection, {
                    key: ({ warehouse }) => {
                        // Use wildcard key for clusters to represent selecting all warehouses of the market
                        if (warehouse.warehouse_type !== "warehouse") {
                            return `${warehouse.market}:*`;
                        }
                        return `${warehouse.market}:${warehouse.name}`;
                    },
                    sync: true,
                    match: (selected, data, key) => {
                        const k = key(data) as string;
                        if (selected.has(k as any)) return true;
                        // allow cluster shortcut: market:* selects all warehouses of the same market
                        const [market] = k.split(":");
                        const wildcard = `${market}:*` as any;
                        return selected.has(wildcard);
                    }
                })
            );

        const master = fboOffersGrid(fboState.changes, fboStocksChanges)
            .plugin(new FilterPlugin(fboStorageFilter))
            .plugin(new StatePlugin("fbo_storage"))
            .plugin(new ChangesPlugin(x => x.id, fboState.changes))
            .plugin(new ReadonlyPlugin(!$userCanModify))
            .plugin(new ZoomPlugin(href => (selected_image = href)))
            .plugin(new ClassesPlugin())
            .plugin(new RowSelectionPlugin(fboStorageSelection, { key: x => x.id }))
            .plugin(new DetailGridPlugin(detail, data => data.stocks, detailApiMap))
            .plugin(
                new SummaryPlugin<FboStorage>({
                    sku: () => "Всего:",
                    volume: ({ rows }) =>
                        rows.reduce((sum, row) => sum + row.volume * selectedToDeliver(row), 0),
                    self_weight: ({ rows }) =>
                        rows.reduce(
                            (sum, row) => sum + row.self_weight * selectedToDeliver(row),
                            0
                        ),
                    cost_price: ({ rows }) =>
                        rows.reduce(
                            (sum, row) => sum + row.cost_price * selectedToDeliver(row),
                            0
                        ),
                    profit: ({ rows }) =>
                        rows.reduce((sum, row) => sum + row.profit * selectedToDeliver(row), 0)
                })
            );
        function selectedToDeliver(row: FboStorage): number {
            const selected = get(fboStocksSelection.selected);
            if (!selected || selected.size === 0) return 0;
            return row.stocks
                .filter(x => x.warehouse.warehouse_type === "warehouse")
                .reduce((sum, storage) => {
                    const key = `${storage.warehouse.market}:${storage.warehouse.name}` as any;
                    const wildcard = `${storage.warehouse.market}:*` as any;
                    if (selected.has(key) || selected.has(wildcard)) {
                        return sum + calcToDeliver(storage);
                    }
                    return sum;
                }, 0);
        }
        return master;
    })();
</script>

{#if selected_image}
    <ImageWindow bind:src={selected_image} />
{/if}

<Toolbar />
{#if browser}
    <Grid {definition} bind:data={$fboState} />
{/if}
<Footer
    changes={fboState.changes}
    on:save={save}
    on:cancel={() => {
        fboState.cancel();
        fboStocksChanges.clear();
    }}
/>
