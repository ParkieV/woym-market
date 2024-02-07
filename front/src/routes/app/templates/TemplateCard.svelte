<script lang="ts">
    import { createEventDispatcher } from "svelte";
    import type { Template } from "./+page.svelte";

    export let template: Template;

    const ToggleFieldNames = {
        use_total_price: "Расчётная цена",
        use_attractive_price_threshold: "Порог для привлекательной цены",
        use_moderately_attractive_price_threshold: "Порог для умеренно привлекательной цены",
        use_your_price_for_buyers: "Ваша цена для покупателей",
        use_min_price_in_market: "Лучшая цена на Я.Маркете в группе",
        use_min_price_without_market: "Лучшая цена без учета Я.Маркета",
        use_min_general_markets_price: "Лучшая цена среди всех площадок"
    } as const;
    const ToggleFields = Object.keys(ToggleFieldNames) as (keyof typeof ToggleFieldNames)[];

    let dispatch = createEventDispatcher<{ changed: void }>();
</script>

<li>
    <header>
        <span>{template.name}</span>
    </header>
    <ul class="toggles">
        {#each ToggleFields as toggle_field}
            <label>
                <input
                    type="checkbox"
                    bind:checked={template[toggle_field]}
                    on:input={() => dispatch("changed")}
                />
                <span>{ToggleFieldNames[toggle_field]}</span>
            </label>
        {/each}
    </ul>
    <ul class="numbers">
        <label>
            <span>Делитель</span>
            <input
                type="number"
                min="0.01"
                step="0.01"
                bind:value={template.n}
                on:input={() => dispatch("changed")}
                on:focusout={() => {
                    if (template.n <= 0) {
                        template.n = 1;
                    }
                }}
            />
        </label>
        <label>
            <span>Прибавить/отнять (%)</span>
            <input
                type="number"
                step="0.01"
                bind:value={template.m}
                on:input={() => dispatch("changed")}
                on:focusout={() => {
                    if (template.m === null) {
                        template.m = 0;
                    }
                }}
            />
        </label>
    </ul>
</li>

<style lang="scss">
    li {
        display: flex;
        flex-direction: column;
        border-radius: 16px;
        width: min-content;
        overflow: hidden;
        border: 2px black solid;
        > header {
            display: flex;
            justify-content: center;
            align-items: center;
            flex: 0 0 50px;
            overflow: hidden;
            margin: 18px 20px 0 20px;
            border-radius: 16px;

            color: white;
            background-color: #424242;
            > span {
                font-weight: bold;
                font-size: 21px;
            }
        }
        > ul {
            display: flex;
            &.toggles {
                display: flex;
                flex-direction: column;
                align-items: stretch;

                padding: 24px 0;
                > label {
                    display: flex;
                    gap: 12px;
                    height: min-content;
                    padding: 8px 40px;

                    > span {
                        font-size: 16px;
                        white-space: nowrap;
                    }
                }
            }
            &.numbers {
                flex-direction: column;
                gap: 12px;
                padding: 0 40px 36px 40px;
                > label {
                    display: flex;
                    gap: 16px;
                    justify-content: space-between;
                    > span {
                        font-size: 16px;
                    }
                    > input {
                        min-width: 0;
                    }
                }
            }
        }
    }
</style>
