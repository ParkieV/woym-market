<script lang="ts">
    export let options: Set<{ name: string; selected: boolean }>;
</script>

<div>
    {#each options as option}
        <button
            class:selected={option.selected}
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
    @use "mixins.scss" as *;
    div {
        display: flex;
        border-radius: 4px;
        overflow: hidden;
        > button {
            @include selectable-button;
            &:not(:last-child) {
                border-right: 1px solid #8ca1b4;
            }
        }
    }
</style>
