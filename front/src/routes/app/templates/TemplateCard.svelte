<script lang="ts">
    import { createEventDispatcher } from "svelte";
    import type { Template } from "$lib/data/templates";
    import { userCanModify } from "$lib/user";

    export let template: Template;

    let dispatch = createEventDispatcher<{ changed: void }>();
</script>

<li class={template.market}>
    <header>
        <span>{template.name}</span>
    </header>
    <ul class="toggles">
        {#each template.fields as field}
            <label>
                <input
                    type="checkbox"
                    bind:checked={field.value}
                    on:input={() => dispatch("changed")}
                    on:click={e => {
                        if (!$userCanModify) e.preventDefault();
                    }}
                />
                <span>{field.name}</span>
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
                readonly={!$userCanModify}
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
                readonly={!$userCanModify}
            />
        </label>
    </ul>
</li>

<style lang="scss">
    li {
        flex: 0 0 content;
        display: flex;
        flex-direction: column;
        gap: 24px;
        max-width: 800px;

        border-radius: 16px;
        overflow: hidden;
        border: 2px black solid;

        &.yandex {
            border-color: #ec2300;
            > header {
                background-color: #ec2300;
            }
        }
        &.ozon {
            border-color: #0000c5;
            > header {
                background-color: #0000c5;
            }
        }

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
            margin: 0 40px;

            &.toggles {
                flex-direction: column;
                align-items: stretch;
                gap: 8px;

                > label {
                    display: flex;
                    gap: 12px;
                    height: min-content;

                    > span {
                        font-size: 16px;
                        white-space: nowrap;
                    }
                }
            }
            &.numbers {
                display: flex;
                flex-wrap: wrap;
                row-gap: 16px;
                column-gap: 64px;
                margin-bottom: 32px;
                > label {
                    flex: 1;
                    display: flex;
                    gap: 32px;
                    justify-content: space-between;
                    > span {
                        white-space: nowrap;
                        font-size: 16px;
                    }
                    > input {
                        width: 100px;
                    }
                }
            }
        }
    }
</style>
