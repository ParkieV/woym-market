<script lang="ts">
    export let image: string | undefined = undefined;
    export let options: { name: string; selected: boolean }[];

    const toggleAll = () => {
        let selected = true;
        if (options.some(x => x.selected)) {
            selected = false;
        }
        options = options.map(x => ({ ...x, selected }));
    };
</script>

<div>
    {#if image}
        <button class="parent" class:selected={options.some(x => x.selected)} on:click={toggleAll}>
            <img src={image} alt="" />
        </button>
    {/if}
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

        > button {
            @include selectable-button;
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
