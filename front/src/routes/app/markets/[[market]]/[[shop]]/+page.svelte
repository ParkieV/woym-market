<script lang="ts">
    import { userCanModify } from "$lib/data/user";
    import type { PageServerData } from "./$types";
    import { patchStore } from "$lib/data/markets";
    import marketLogo from "$lib/components/market_logo";
    import MarketSettings from "./Market.svelte";
    import { page } from "$app/stores";
    import { afterNavigate, invalidateAll } from "$app/navigation";
    import { invalidateAllState } from "../../../(main)/state";

    export let data: PageServerData;

    let invalid = false;
    let changed = false;

    async function ok() {
        if (data.market) {
            await patchStore(data.market);
            await reset();
            await invalidateAllState();
        }
    }

    afterNavigate(async ({ type }) => {
        if (type === "enter") return;
        await reset();
    });

    async function reset() {
        await invalidateAll();
        changed = false;
        invalid = false;
    }
</script>

<div id="markets-page">
    <header>
        <h1>Магазины</h1>
        <ul>
            {#each data.markets as market}
                {#if !(market.name === $page.data.market?.name && market.type === data.market?.type)}
                    <a href={`/app/markets/${market.type}/${market.name}`}>
                        <li class:selected={market.name === $page.params.name}>
                            <h2>{market.name}</h2>
                            <img src={marketLogo(market)} alt={market.type} title={market.type} />
                        </li>
                    </a>
                {:else}
                    <li class="selected">
                        <h2>{market.name}</h2>
                        <img src={marketLogo(market)} alt={market.type} title={market.type} />
                    </li>
                {/if}
            {/each}
        </ul>
    </header>
    <main>
        {#if data.market === null}
            <div class="empty">Выберите магазин в списке</div>
        {:else}
            <MarketSettings
                market={data.market}
                bind:invalid
                on:change={() => {
                    if (data.market) {
                        changed = true;
                        changed = changed;
                    }
                }}
            />
        {/if}
    </main>
    <footer>
        {#if $userCanModify}
            <button class="confirm" disabled={invalid || !changed} on:click={ok}>
                Сохранить
            </button>
        {/if}
    </footer>
</div>

<style lang="scss">
    @use "mixins" as *;

    #markets-page {
        display: flex;
        flex-direction: column;
        min-width: 0;

        header {
            display: flex;
            flex-direction: column;
            gap: 12px;
            padding: 16px;
            padding-bottom: 0;

            h1 {
                font-size: 28px;
            }

            ul {
                display: flex;
                gap: 20px;
                overflow-x: auto;
                scrollbar-width: none;

                a {
                    display: contents;
                    color: inherit;
                    text-decoration: none;
                }

                li {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    padding: 8px 16px;
                    border-bottom: 2px solid rgb(200, 200, 200);
                    &:hover {
                        border-bottom: 2px solid rgb(165, 165, 165);
                    }
                    &.selected {
                        font-weight: bold;
                        border-bottom: 2px solid black;
                        cursor: default;
                    }
                    > h2 {
                        font-size: 20px;
                        font-weight: inherit;
                    }
                    > img {
                        height: 24px;
                    }
                }
            }
        }

        main {
            display: contents;
            flex: 1;
            .empty {
                font-size: 24px;
                margin: auto auto;
            }
        }

        footer {
            display: flex;
            justify-content: end;
            align-items: center;
            height: 70px;
            padding: 0 16px;
            gap: 16px;
            background-color: #ebebeb;
            button {
                @include primary-button;
                height: 40px;
            }
        }
    }
</style>
