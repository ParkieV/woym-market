<script lang="ts">
    import Modal from "./Modal.svelte";

    export let isOpen: boolean;
    export let header: string;
    export let text: string;
    export let showCancelButton: boolean = false;

    export let onConfirm: () => void = () => {};
    export let onCancel: () => void = () => {};

    const cancel = () => {
        isOpen = false;
        onCancel();
    };

    const confirm = () => {
        isOpen = false;
        onConfirm();
    };
</script>

{#if isOpen}
    <Modal open={isOpen}>
        <div>
            <h1>{header}</h1>
            <span>{text}</span>
            <footer>
                {#if showCancelButton}
                    <button class="cancel" on:click={cancel}>Отмена</button>
                {/if}
                <button class="confirm" on:click={confirm}>Ок</button>
            </footer>
        </div>
    </Modal>
{/if}

<style lang="scss">
    @use "mixins.scss" as *;
    div {
        display: flex;
        flex-direction: column;
        gap: 8px;
        width: 460px;
        padding: 20px 30px;
        gap: 8px;

        > span {
            font-size: 16px;
        }
        > footer {
            display: flex;
            justify-content: end;
            gap: 8px;
            margin-top: 8px;
            > button {
                &.cancel {
                    @include secondary-button;
                    width: 80px;
                }
                &.confirm {
                    @include primary-button;
                    width: 80px;
                }
            }
        }
    }
</style>
