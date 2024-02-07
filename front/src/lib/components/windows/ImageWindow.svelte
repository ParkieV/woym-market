<script lang="ts">
    export let src: string;

    let dialog: HTMLDialogElement;
    $: if (src && dialog) {
        dialog.showModal();
    } else if (dialog) {
        dialog.close();
    }
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
<dialog bind:this={dialog} on:click|stopPropagation={() => (src = "")} on:close={() => (src = "")}>
    <div>
        <img {src} alt="" />
    </div>
</dialog>

<style lang="scss">
    dialog {
        width: 100%;
        height: 100%;
        z-index: 1;
        background-color: transparent;
        &::backdrop {
            background: rgba(0, 0, 0, 0.3);
        }
        border: 0;
    }
    div {
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    img {
        max-height: 70vh;
        max-width: 70vw;
    }
</style>
