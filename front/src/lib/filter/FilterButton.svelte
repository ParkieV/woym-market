<script lang="ts">
    export let image: string;
    export let alt: string = "";
    export let disabled: boolean = false;
</script>

<button on:click title={alt} {disabled}>
    <img src={image} {alt} />
</button>

<style lang="scss">
    @use "$lib/scss/mixins.scss" as *;
    @use "./style.scss" as *;
    button {
        @include button;
        @include square;
        padding: 4px;
        border: 0;
        border-radius: 4px;

        &:hover {
            background-color: #e1e1e4;
        }
        &:active {
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
</style>
