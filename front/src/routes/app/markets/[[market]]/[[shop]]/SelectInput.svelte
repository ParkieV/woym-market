<script lang="ts">
    export let label: string;
    export let value: string | null;
    export let options: string[];
    export let readonly: boolean = false;
</script>

<label>
    <span>{label}</span>
    <select disabled={readonly} bind:value>
        {#each options as option}
            <option value={option}>{option}</option>
        {/each}
    </select>
</label>

<style lang="scss">
    label {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: nowrap;
        font-size: 18px;
        > select {
            flex: 0 0 120px;
            font-size: 18px;
            width: 120px;
            height: 42px;
            border-radius: 8px;
            padding: 8px;
            border: 1px solid grey;
            outline: 0;
            background-color: white;
            &:invalid {
                color: #cf2222;
                background-color: #ffeeee;
                border: 1px solid #cf2222;
            }
            &:focus {
                padding: 7px;
                border-width: 2px;
            }
        }
    }
</style>
