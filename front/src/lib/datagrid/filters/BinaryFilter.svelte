<script lang="ts" generics="T">
    import type { Filter } from ".";
    import type { FilterGroup } from "./FilterGroup.svelte";
    import type { Writable } from "svelte/store";
    import { getContext } from "svelte";

    export let value: boolean = false;
    export let image: string;
    export let alt: string = "";
    export let filter: Filter<T>;

    /** What to do with filter when button is turned on. */
    export let mode: "enable" | "disable" | "invert" = "enable";

    let filterGroup = getContext<Writable<FilterGroup<T>>>("filter");
    $: filterGroup.update(group => {
        if (mode === "enable") {
            group.set(filter, { apply: value, invert: false });
        } else if (mode === "disable") {
            group.set(filter, { apply: !value, invert: false });
        } else if (mode === "invert") {
            group.set(filter, { apply: true, invert: value });
        }
        return group;
    });
</script>

<button on:click={() => (value = !value)} title={alt} class:enabled={value}>
    <img src={image} {alt} />
</button>

<style lang="scss">
    @use "./style.scss" as *;
    button {
        @include filter-btn;
        padding: 4px;
        aspect-ratio: 1;
        border: 0;
        border-radius: 4px;

        &.enabled {
            > img {
                filter: invert(1);
            }
        }
        > img {
            height: 24px;
            width: 24px;
        }
    }
</style>
