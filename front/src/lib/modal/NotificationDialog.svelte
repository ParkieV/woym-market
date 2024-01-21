<script lang="ts">
    import { createEventDispatcher } from "svelte";
    import Modal from "./Modal.svelte";

    export let open: boolean = true;
    export let header: string;
    export let text: string;

    let dispatch = createEventDispatcher<{ close: void }>();

    const onConfirm = () => {
        if (!open) return;
        open = false;
        dispatch("close");
    };
</script>

<Modal {open}>
    <div>
        <h1>{header}</h1>
        <span>{text}</span>
        <footer>
            <button class="confirm" on:click={onConfirm}>Ок</button>
        </footer>
    </div>
</Modal>

<style lang="scss">
    div {
        display: flex;
        flex-direction: column;
        gap: 8px;
        width: 400px;
        padding: 12px;
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
                width: 80px;
                height: 40px;
                border-radius: 8px;
                border: 0;
                color: white;
            }
        }
    }
</style>
