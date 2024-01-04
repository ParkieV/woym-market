<script lang="ts">
    import { fetchUserInfo, patchUserInfo } from "$lib";
    import { createEventDispatcher, onMount } from "svelte";

    export let open: boolean;
    export let text: string;

    let dialog: HTMLDialogElement | null;
    $: if (open && dialog) {
        dialog.showModal();
    } else if (dialog) {
        dialog.close();
    }

    let dispatch = createEventDispatcher<{ ok: void; cancel: void }>();
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
<dialog bind:this={dialog} on:cancel={() => dispatch("cancel")} on:close={() => (open = false)}>
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div on:click|stopPropagation>
        <h1>Вы уверены?</h1>
        {#if text}
            <span>{text}</span>
        {/if}
        <footer>
            <button class="cancel" on:click={() => dispatch("cancel")}>Отмена</button>
            <button class="confirm" on:click={() => dispatch("ok")}>Ок</button>
        </footer>
    </div>
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

        > div {
            display: flex;
            flex-direction: column;
            gap: 8px;
            width: 400px;
            padding: 12px;

            > h1 {
                margin-bottom: 8px;
            }
            > span {
                font-size: 16px;
            }
            > footer {
                display: flex;
                justify-content: end;
                gap: 8px;
                > button {
                    width: 80px;
                    height: 40px;
                    border-radius: 8px;
                    border: 0;
                    color: white;
                    margin-top: 16px;
                }
            }
        }
    }
</style>
