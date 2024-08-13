<script lang="ts">
    export let placeholder = "Search...";
    export let value = "";
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
