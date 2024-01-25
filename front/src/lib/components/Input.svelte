<script lang="ts">
    export let label: string;
    export let placeholder: string = "";
    export let type: "text" | "password" = "text";

    export let value: string;
</script>

<label>
    <span>{label}</span>
    {#if type == "text"}
        <input bind:value {placeholder} type="text" />
    {:else}
        <input bind:value {placeholder} type="password" />
    {/if}
</label>

<style lang="scss">
    label {
        display: flex;
        flex-direction: column;
        gap: 4px;
        span {
            color: black;
            font-size: 16px;
            margin-left: 12px;
        }
        input {
            height: 56px;
            font-size: 15px;
            border: 1px solid #222222;
            border-radius: 8px;
            padding: 20px 16px;
            background-color: white;
            outline: none;
            &:focus {
                border: 2px solid black;
            }
        }
    }
</style>
