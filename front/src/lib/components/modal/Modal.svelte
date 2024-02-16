<script lang="ts">
    export let open: boolean;

    let dialog: HTMLDialogElement | undefined;
    $: if (dialog) {
        if (open) dialog.showModal();
        else dialog.close();
    }
</script>

<dialog bind:this={dialog} on:close={() => (open = false)}>
    <slot />
</dialog>

<style lang="scss">
    dialog {
        margin: auto;
        border-radius: 4px;
        border: none;
        padding: 0;
        &::backdrop {
            background: rgba(0, 0, 0, 0.3);
        }
    }
</style>
