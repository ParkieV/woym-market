<script lang="ts" context="module">
    export type Option = { name: string; selected: boolean };
</script>

<script lang="ts" generics="T">
    import { getContext } from "svelte";
    import type { Writable } from "svelte/store";
    import type { FilterGroup } from "./FilterGroup.svelte";

    export let image: string | undefined = undefined;
    export let options: Option[];
    export let filter: (data: T, opts: Option[]) => boolean;
    const curriedFilter = (data: T) => filter(data, options);

    let filterGroup = getContext<Writable<FilterGroup<T>>>("filter");
    $: filterGroup.update(group => {
        group.set(curriedFilter, { apply: options.length !== 0, invert: false });
        return group;
    });

    function toggleAll() {
        let selected = true;
        if (options.some(x => x.selected)) {
            selected = false;
        }
        options = options.map(x => ({ ...x, selected }));
    }
</script>

<div>
    {#if image}
        <button class="parent" class:enabled={options.some(x => x.selected)} on:click={toggleAll}>
            <img src={image} alt="" />
        </button>
    {/if}
    {#each options as option}
        <button
            class:enabled={option.selected}
            on:click={() => {
                option.selected = !option.selected;
                options = options;
            }}
        >
            {option.name}
        </button>
    {/each}
</div>

<style lang="scss">
    @use "./style.scss" as *;
    div {
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
                    height: calc(100% - 8px);
                }
            }
        }
    }
</style>
