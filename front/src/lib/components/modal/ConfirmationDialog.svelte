<script lang="ts">
    import { createEventDispatcher } from "svelte";
    import Modal from "./Modal.svelte";

    export let open: boolean = true;
    export let header: string;
    export let text: string;

    let dispatch = createEventDispatcher<{ close: void; cancel: void; confirm: void }>();

    const onConfirm = () => {
        if (!open) return;
        open = false;
        dispatch("confirm");
        dispatch("close");
    };
    const onCancel = () => {
        if (!open) return;
        open = false;
        dispatch("cancel");
        dispatch("close");
    };
</script>

<Modal {open}>
    <div>
        <h1>{header}</h1>
        <span>{text}</span>
        <footer>
            <button class="cancel" on:click={onCancel}>Отмена</button>
            <button class="confirm" on:click={onConfirm}>Ок</button>
        </footer>
    </div>
</Modal>

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
