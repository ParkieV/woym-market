<script lang="ts" generics="T">
    import type { Filter } from ".";
    import type { FilterGroup } from "./FilterGroup.svelte";
    import type { Writable } from "svelte/store";
    import { getContext } from "svelte";

    export let value: boolean | null = null;
    export let image: string;
    export let alt: string = "";
    export let filter: Filter<T>;

    let filterGroup = getContext<Writable<FilterGroup<T>>>("filter");
    $: filterGroup.update(group => {
        group.set(filter, { apply: value !== null, invert: value === false });
        return group;
    });

    function next() {
        if (value === null) value = true;
        else if (value === true) value = false;
        else if (value === false) value = null;
    }
</script>

<button
    on:click={next}
    title={alt}
    class:enabled={value !== null}
    class:true={value === true}
    class:false={value === false}
>
    <img src={image} {alt} />
</button>

<style lang="scss">
    @use "./style.scss" as *;
    button {
        @include ternary-btn;
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
