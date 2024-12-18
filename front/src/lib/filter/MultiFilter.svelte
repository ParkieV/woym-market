<script lang="ts" context="module">
    export type MultiFilterEntry = {
        name: string;
        tooltip: string;
        enabled: boolean;
    };
</script>

<script lang="ts" generics="T extends {[K: string]: MultiFilterEntry}">
    export let value: T;
    export let image: string;
    export let alt: string = "";
</script>

<button title={alt}>
    <img src={image} {alt} />
    <section>
        {#each Object.values(value) as { name, tooltip, enabled }}
            <label title={tooltip}>
                <input bind:checked={enabled} type="checkbox" />
                <span>{name}</span>
                <span class="question">(?)</span>
            </label>
        {/each}
    </section>
</button>

<style lang="scss">
    @use "./style.scss" as *;
    button {
        @include square;
        padding: 4px;
        border: 0;
        border-radius: 4px;
        position: relative;

        &:hover {
            background-color: #e1e1e4;
        }
        &:not(:focus-within) {
            > section {
                display: none;
            }
        }
        &:focus-within {
            background-color: #2f4880;
            > img {
                filter: invert(1);
            }
        }
        > img {
            height: 24px;
            width: 24px;
        }
    }
    section {
        position: absolute;
        top: calc(100% + 8px);
        right: 0;
        width: max-content;
        z-index: 1;

        display: flex;
        flex-direction: column;
        gap: 8px;

        background-color: white;
        border: 1px solid gray;
        border-radius: 4px;
        padding: 12px 20px;

        > label {
            display: flex;
            gap: 8px;
            > span.question {
                border-bottom: 1px dotted black;
                margin-left: auto;
            }
        }
    }
</style>
