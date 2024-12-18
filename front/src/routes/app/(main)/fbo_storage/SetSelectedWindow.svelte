<script lang="ts">
    import { selectedDisplayInfo } from "./selected";
    import type { ChangeList } from "$lib/datagrid/plugins/changes";
    import type { Readable } from "svelte/store";
    import type { FboStorage, FboStocks } from "$lib/data/fbo_storage";
    import type { GridApi, IRowNode } from "ag-grid-enterprise";
    import Window from "$lib/components/windows/Window.svelte";

    export let isOpen: boolean;
    let target: number;
    let input: HTMLInputElement;
    let valid = false;

    export let grid: GridApi<FboStorage>;

    export let changes: ChangeList<FboStorage, number>;
    export let innerChanges: ChangeList<FboStocks, number>;

    export let selectedStocks: Readable<Map<number, FboStorage>>;
    export let selectedStorage: Readable<Map<number, FboStocks>>;

    function ok() {
        let changedStocks = new Set<IRowNode<FboStorage>>();

        grid.forEachNode(node => {
            if (node.data === undefined || !$selectedStocks.has(node.data.id)) return;
            changes.add(node.data.id);
            for (const stock of node.data.stocks) {
                if ($selectedStorage.has(stock.warehouse.id)) {
                    changedStocks.add(node);
                    innerChanges.add(stock.id);
                    stock.min_stock = target;
                }
            }
            refreshDetail(node);
        });
        grid.refreshCells({ rowNodes: Array.from(changedStocks) });
        isOpen = false;
    }

    function refreshDetail(node: IRowNode) {
        let detailGrid = grid.getDetailGridInfo(`detail_${node.id}`)?.api;
        detailGrid?.refreshCells({
            force: true,
            columns: ["warehouse.name", "min_stock"]
        });
    }
</script>

<Window bind:open={isOpen}>
    <header slot="header">
        <h1>Установить значения</h1>
        <p>{$selectedDisplayInfo}</p>
    </header>
    <div>
        <label class="content">
            <span>Минимальный остаток</span>
            <input
                bind:value={target}
                type="number"
                step="1"
                min="0"
                bind:this={input}
                on:input={() => (valid = input.checkValidity())}
            />
        </label>
    </div>
    <svelte:fragment slot="footer">
        <button class="cancel" on:click={() => (isOpen = false)}>Отмена</button>
        <button class="confirm" on:click={ok} disabled={!valid}>Ок</button>
    </svelte:fragment>
</Window>

<style lang="scss">
    @use "mixins.scss" as *;

    @use "mixins" as *;
    header {
        h1 {
            margin-bottom: 4px;
        }
        p {
            font-size: 14px;
        }
    }
    div {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin: 20px 0 10px 0;
        label {
            display: flex;
            justify-content: space-between;
            span,
            input {
                font-size: 16px;
            }
            input {
                width: 120px;
            }
        }
    }

    button.confirm {
        @include primary-button;
        width: 80px;
    }
    button.cancel {
        @include secondary-button;
        width: 80px;
    }
</style>
