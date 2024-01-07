<script lang="ts" context="module">
    export type DialogData = {
        header: string;
        text: string;
        onConfirm?: () => void;
        onCancel?: () => void;
    };
</script>

<script lang="ts">
    export let data: DialogData | undefined = undefined;

    let dialog: HTMLDialogElement | undefined;
    $: if (dialog) {
        data;
        dialog.showModal();
    }

    const onConfirm = () => {
        if (!data) return;
        let action = data.onConfirm;
        data = undefined;
        if (action) action();
    };
    const onCancel = () => {
        if (!data) return;
        let action = data.onCancel;
        data = undefined;
        if (action) action();
    };
</script>

{#if data}
    <dialog bind:this={dialog}>
        <div>
            <h1>{data.header}</h1>
            {#if data.text}
                <span>{data.text}</span>
            {/if}
            <footer>
                <button class="cancel" on:click={onCancel}>Отмена</button>
                <button class="confirm" on:click={onConfirm}>Ок</button>
            </footer>
        </div>
    </dialog>
{/if}

<style lang="scss">
    dialog {
        margin: auto;
        border-radius: 4px;
        border: none;
        padding: 0;
        &::backdrop {
            background: rgba(0, 0, 0, 0.3);
        }

        > div {
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
    }
</style>
