<script lang="ts">
    export let label: string;
    export let max: number | undefined = undefined;
    export let min: number | undefined = undefined;
    export let value: number;
    export let readonly: boolean = false;
</script>

<label>
    <span>{label}</span>
    <input type="number" {min} {max} step="any" {readonly} bind:value />
</label>

<style lang="scss">
    label {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        font-size: 18px;
        > input {
            font-size: 18px;
            padding: 8px;
            max-width: 120px;
            border-radius: 8px;
            border: 1px solid grey;
            outline: 0;
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
