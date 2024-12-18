<script lang="ts">
    import Modal from "$lib/components/modal/Modal.svelte";

    export let open: boolean;
</script>

<Modal bind:open>
    <div>
        <header>
            <slot name="header" />
        </header>
        <slot />
        <footer>
            <slot name="footer" />
        </footer>
    </div>
</Modal>

<style lang="scss">
    div {
        display: flex;
        flex-direction: column;
        padding: 18px 32px 28px 32px;
        gap: 8px;
        width: 420px;
    }

    header {
        display: flex;
        flex-direction: column;
    }

    footer {
        display: flex;
        justify-content: end;
        gap: 8px;
        margin-top: 12px;
    }
</style>
