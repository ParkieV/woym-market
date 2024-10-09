<script lang="ts">
    export let label: string;
    export let value: boolean;
    export let readonly: boolean = false;
</script>

<label>
    <span>{label}</span>
    <input type="checkbox" {readonly} bind:checked={value} />
</label>

<style lang="scss">
    label {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: nowrap;
        font-size: 18px;
        > input {
            flex: 0 0 120px;
            font-size: 18px;
            width: 120px;
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
