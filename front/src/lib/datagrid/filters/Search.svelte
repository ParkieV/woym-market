<script lang="ts" generics="T">
    import { getContext } from "svelte";
    import type { Writable } from "svelte/store";
    import type { FilterGroup } from "./FilterGroup.svelte";

    export let placeholder = "Search...";
    export let value = "";
    $: search = normalizeString(value);

    /** Fields to check when doing search. */
    export let fields: (keyof T)[] | ((data: T) => string[]);

    function filter(data: T) {
        let strings: string[];
        if (Array.isArray(fields)) {
            strings = fields.map(field => data[field] + "");
        } else {
            strings = fields(data);
        }
        return strings
            .filter(data => data !== undefined && data !== null)
            .map(data => normalizeString((data as {}).toString()))
            .some(s => s.includes(search));
    }

    function normalizeString(s: string): string {
        return s.trim().toLowerCase().replaceAll("ё", "е");
    }

    let filterGroup = getContext<Writable<FilterGroup<T>>>("filter");
    $: filterGroup.update(group => {
        group.set(filter, { apply: value.length !== 0, invert: false });
        return group;
    });
</script>

<input bind:value type="text" {placeholder} />

<style lang="scss">
    input {
        flex: 1;
        max-width: 300px;
        min-width: 150px;

        padding: 8px;
        border: 1px solid #ccc;
        border-radius: 4px;
        padding-left: 40px;
        background: url("/magnifying-glass.svg") no-repeat 10px center;
        background-size: 20px 20px;
        outline: none;
        &:focus {
            border: 1px solid #3b5897;
        }
    }
</style>
