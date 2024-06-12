<script lang="ts" context="module">
    import type { Filter } from ".";

    export class FilterGroup<T> {
        constructor(
            public kind: "and" | "or",
            public invert: boolean,
            public extend: boolean
        ) {}

        private filters = new Map<Filter<T> | FilterGroup<T>, FilterMetadata>();

        public set(filter: Filter<T> | FilterGroup<T>, meta: FilterMetadata) {
            this.filters.set(filter, meta);
        }

        public check(data: T): boolean {
            let array = Array.from(this.filters).filter(([_, { apply }]) => apply);
            if (array.length === 0) return true;

            let method = array[this.kind === "and" ? "every" : "some"];
            return method.call(array, ([filter, { apply: _, invert }]) => {
                if (filter instanceof FilterGroup) {
                    if (filter.check(data) === invert) return false;
                } else {
                    if (filter(data) === invert) return false;
                }
                return true;
            });
        }
    }

    export type FilterMetadata = {
        apply: boolean;
        invert: boolean;
    };

    export const FILTER_KEY = "filter";
</script>

<script lang="ts" generics="T">
    import { writable, type Writable } from "svelte/store";
    import { getContext, setContext } from "svelte";

    export let kind: "and" | "or" = "and";
    export let invert: boolean = false;
    export let extend: boolean = true;

    let parent = getContext<Writable<FilterGroup<T>> | undefined>(FILTER_KEY);
    let current = writable(new FilterGroup<T>(kind, invert, extend));
    setContext(FILTER_KEY, current);

    $: if ($parent !== undefined && $current.extend) {
        $parent.set($current, { apply: true, invert });
        $parent = $parent;
    }

    export let filter = (_: T) => true;
    $: filter = $current.check.bind($current);
</script>

<slot />
