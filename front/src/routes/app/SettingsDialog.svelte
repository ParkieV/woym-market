<script lang="ts">
    import { fetchUserInfo, patchUserInfo } from "$lib/data/settings";
    import { createEventDispatcher, onMount } from "svelte";

    export let open: boolean;

    let dialog: HTMLDialogElement | null;
    let dispatch = createEventDispatcher<{ confirm: void }>();
    $: if (open && dialog) {
        dialog.showModal();
    } else if (dialog) {
        dialog.close();
    }

    let rate = 0;

    async function ok() {
        try {
            await patchUserInfo({ rate });
            dispatch("confirm");
            dialog?.close();
        } catch {
            alert("Произошла ошибка при обновлении настроек.");
        }
    }

    onMount(async () => {
        rate = (await fetchUserInfo()).rate;
    });
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
<dialog bind:this={dialog} on:close={() => (open = false)} on:click|self={() => dialog?.close()}>
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div on:click|stopPropagation>
        <h1>Настройки</h1>
        <label>
            <span>Текущий курс</span>
            <input type="number" min="0" bind:value={rate} />
        </label>
        <button on:click={ok}>Ок</button>
    </div>
</dialog>

<style lang="scss">
    dialog {
        margin: auto;
        max-width: 32em;
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
            width: 300px;
            padding: 20px;

            > h1 {
                margin-bottom: 8px;
            }
            > label {
                display: flex;
                justify-content: space-between;
                > input {
                    width: 100px;
                }
            }
            > button {
                align-self: flex-end;
                width: 80px;
                height: 32px;
                border-radius: 8px;
                border: 0;
                color: white;
                background-color: #455561;
                margin-top: 16px;
            }
        }
    }
</style>
