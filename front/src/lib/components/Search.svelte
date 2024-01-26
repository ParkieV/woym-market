<script lang="ts">
    export let placeholder = "Search...";
    export let value = "";
</script>

<input bind:value type="text" class="search-input" {placeholder} />

<style>
    .search-input {
        padding: 8px;
        border: 1px solid #ccc;
        min-width: 300px;
        padding-left: 40px;
        background: url("/magnifying-glass.svg") no-repeat 10px center;
        background-size: 20px 20px;
        outline: none;
    }
</style>
