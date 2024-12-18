<script lang="ts" generics="T">
    import Loader from "$lib/components/Loader.svelte";

    import { onMount } from "svelte";
    import Modal from "./Modal.svelte";

    export let isOpen: boolean = true;
    export let header: string;
    export let promise: Promise<T>;

    onMount(() => {
        promise.finally(() => (isOpen = false));
    });
</script>

{#if isOpen}
    <Modal open={isOpen}>
        <div class="content">
            <h1>{header}</h1>
            <Loader size={"24px"} />
        </div>
    </Modal>
{/if}

<style lang="scss">
    @use "mixins.scss" as *;
    .content {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        padding: 16px;
        gap: 16px;
        > h1 {
            font-size: 21px;
        }
    }
</style>
