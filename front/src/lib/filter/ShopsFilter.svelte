<script lang="ts" context="module">
    export type ShopOption = { id: number; name: string; market: string; selected: boolean };
</script>

<script lang="ts">
    import marketLogo from "$lib/components/market_logo";

    export let options: ShopOption[];
    $: markets = new Set(options.map(x => x.market));

    function toggleMarket(market: string) {
        let selected = true;
        if (options.filter(x => x.market === market).some(x => x.selected)) {
            selected = false;
        }
        options = options.map(x => (x.market === market ? { ...x, selected } : x));
        markets = markets;
    }
</script>

<div class="shopsFilter">
    {#each markets as market}
        <div>
            <button
                class="parent"
                class:enabled={options.some(x => x.selected && x.market === market)}
                on:click={() => toggleMarket(market)}
            >
                <img src={marketLogo(market)} alt="" />
            </button>
            {#each options.filter(x => x.market === market) as option}
                <button
                    class:enabled={option.selected}
                    on:click={() => (option.selected = !option.selected)}
                >
                    {option.name}
                </button>
            {/each}
        </div>
    {/each}
</div>

<style lang="scss">
    @use "./style.scss" as *;
    .shopsFilter {
        flex: 1 1 400px;
        display: flex;
        gap: 16px;
        overflow-x: auto;
        scrollbar-width: none;
        margin-right: auto;

        > div {
            display: flex;

            > button {
                @include filter-btn;
                padding: 0 12px;

                overflow: hidden;
                &:first-of-type {
                    border-top-left-radius: 4px;
                    border-bottom-left-radius: 4px;
                }
                &:last-of-type {
                    border-top-right-radius: 4px;
                    border-bottom-right-radius: 4px;
                }
                &:not(:last-child) {
                    border-right: 1px solid #8ca1b4;
                }

                &.parent {
                    padding: 0 10px;
                    > img {
                        aspect-ratio: 1;
                        height: 28px;
                        border-radius: 8px;
                    }
                }
            }
        }
    }
</style>
