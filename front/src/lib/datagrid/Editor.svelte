<script lang="ts">
    import type { ICellEditorParams } from "ag-grid-enterprise";
    import { onMount } from "svelte";

    export let params: ICellEditorParams;

    let input: HTMLInputElement;
    let textValue: string;
    $: invalid = input && params.parseValue(textValue ?? "") instanceof Error;

    let select: boolean = false;

    onMount(() => {
        const { eventKey, value, formatValue } = params;
        if (eventKey === "Backspace" || eventKey === "Del") {
            textValue = "";
            return;
        }
        if (eventKey && /^[0-9\p{Letter}]$/u.test(eventKey)) {
            textValue = eventKey;
            return;
        }
        if (value !== undefined && value !== null) {
            if (eventKey === null || eventKey === "Enter") {
                select = true;
            }
            textValue = formatValue(value);
            return;
        }
    });

    export function afterGuiAttached() {
        input.focus();
        if (select) input.select();
    }

    export function getValue() {
        return params.parseValue(textValue);
    }

    export function isCancelAfterEnd() {
        try {
            params.parseValue(textValue);
            return false;
        } catch {
            return true;
        }
    }
</script>

<input bind:this={input} bind:value={textValue} class:invalid />

<style lang="scss">
    input {
        width: 100%;
        height: 100%;
        padding-left: var(--ag-grid-size);
        &.invalid {
            border-color: red;
        }
    }
</style>
