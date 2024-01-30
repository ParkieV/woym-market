<script lang="ts">
    import Loader from "$lib/components/Loader.svelte";

    import { createEventDispatcher, onMount } from "svelte";
    import Modal from "./Modal.svelte";

    export let open: boolean = true;
    export let header: string;
    export let errorHeader: string;
    export let errorText: string;
    export let promise: Promise<Response>;

    let dispatch = createEventDispatcher<{ close: void }>();

    const close = () => {
        if (!open) return;
        open = false;
        dispatch("close");
    };

    onMount(() => {
        promise.then(response => {
            if (response.ok) {
                close();
            } else {
                state = "reject";
            }
        });
        promise.catch(() => {
            state = "reject";
        });
    });

    let state: "waiting" | "reject" = "waiting";
</script>

<Modal {open}>
    <div class="content" class:waiting={state == "waiting"}>
        {#if state == "reject"}
            <h1>{errorHeader}</h1>
            <span>{errorText}</span>
            <footer>
                <button on:click={close}>Ок</button>
            </footer>
        {:else if state == "waiting"}
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
                height: 40px;
                border-radius: 8px;
                border: 0;
                color: white;
            }
        }
    }
</style>
