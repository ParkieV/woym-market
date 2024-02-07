<script lang="ts">
    import Loader from "$lib/components/Loader.svelte";

    import { createEventDispatcher, onMount } from "svelte";
    import Modal from "./Modal.svelte";

    export let open: boolean = true;
    export let header: string;
    export let errorHeader: string;
    export let promise: Promise<Response | Response[]>;

    let dispatch = createEventDispatcher<{ close: void }>();

    const close = () => {
        if (!open) return;
        open = false;
        dispatch("close");
    };

    onMount(() => {
        promise.then(async response => {
            let _response;
            if (!Array.isArray(response)) {
                _response = [response];
            } else {
                _response = response;
            }

            for (const response of _response) {
                if (!response.ok) {
                    let body = await response.json();
                    state = { kind: "reject", detail: body.detail };
                    return;
                }
            }
            close();
        });
        promise.catch(() => {
            state = { kind: "reject", detail: "Не удалось достичь сервера." };
        });
    });

    let state: State = { kind: "waiting" };
    type State = { kind: "waiting" } | { kind: "reject"; detail: string };
</script>

<Modal {open}>
    <div class="content" class:waiting={state.kind == "waiting"}>
        {#if state.kind == "reject"}
            <h1>{errorHeader}</h1>
            <span>{state.detail}</span>
            <footer>
                <button on:click={close}>Ок</button>
            </footer>
        {:else if state.kind == "waiting"}
            <h1>{header}</h1>
            <Loader size={"24px"} />
        {/if}
    </div>
</Modal>

<style lang="scss">
    @use "mixins.scss" as *;
    .content {
        display: flex;
        flex-direction: column;
        padding: 16px 28px 24px 28px;
        gap: 8px;
        > h1 {
            font-size: 21px;
        }
        &.waiting {
            flex-direction: row;
            justify-content: space-between;
            padding: 16px;
            gap: 16px;
        }
        > span {
            font-size: 18px;
        }
        > footer {
            display: flex;
            justify-content: end;
            gap: 8px;
            margin-top: 8px;
            > button {
                @include primary-button;
                width: 80px;
            }
        }
    }
</style>
