<script lang="ts" generics="T extends { id: number }">
    export let selectedId: number | null = null;
    export let data: T[] | Promise<T[]>;
    let container: HTMLDivElement;
    let entries: HTMLLabelElement[] = [];

    export let pageSize = 5;

    async function onKey(key: string) {
        // if (!container.contains(document.activeElement)) return;
        if (selectedId === null) return;

        let values = await data;

        let index = values.findIndex(x => x.id === selectedId);
        if (key === "ArrowUp") {
            index = Math.max(0, index - 1);
        } else if (key === "ArrowDown") {
            index = Math.min(values.length - 1, index + 1);
        } else if (key === "PageUp") {
            index = Math.max(0, index - pageSize);
        } else if (key === "PageDown") {
            index = Math.min(values.length - 1, index + pageSize);
        } else if (key === "Home") {
            index = 0;
        } else if (key === "End") {
            index = values.length - 1;
        }

        selectedId = values[index].id;
        entries[index].scrollIntoView({ behavior: "smooth", block: "center" });
    }
</script>

<svelte:window on:keydown={e => onKey(e.code)} />

<div bind:this={container}>
    {#await data}
        <span class="loading">Загрузка...</span>
    {:then values}
        {#each values as value, i}
            <label class:checked={value.id === selectedId} bind:this={entries[i]}>
                <input type="radio" value={value.id} bind:group={selectedId} />
                <slot {value} />
            </label>
        {/each}
    {/await}
</div>

<style lang="scss">
    div {
        display: flex;
        flex-direction: column;
        height: 200px;
        overflow-y: auto;
        border: 1px solid #b9b9b9;

        label {
            flex: 0 0 40px;
            display: flex;
            align-items: center;
            padding: 0 12px;
            height: 40px;
            border-bottom: 0;
            &:hover,
            &:focus {
                background-color: #e2e2e2;
            }
            &.checked {
                color: white;
                background-color: #3b5897;
            }
        }

        input {
            display: none;
        }
        .loading {
            font-size: 16px;
            margin: auto auto;
        }
    }
</style>
