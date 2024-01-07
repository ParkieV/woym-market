<script lang="ts">
    export let open: boolean;

    let dialog: HTMLDialogElement | undefined;
    $: if (dialog && open) {
        dialog.showModal();
    } else if (dialog) {
        dialog.close();
    }
</script>

{#if open}
    <dialog bind:this={dialog}>
        <div>
            <h1>Информация устарела</h1>
            <span>Данные в таблице были обновлены</span>
            <footer>
                <button class="confirm" on:click={() => (open = false)}>Ок</button>
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
