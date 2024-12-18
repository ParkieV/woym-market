<script lang="ts">
    export let value: boolean | null = null;
    export let image: string;
    export let alt: string = "";

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
        @include square;
        padding: 4px;
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
