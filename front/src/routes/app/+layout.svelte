<script lang="ts">
    import type { ModalKind } from "$lib/components/modal/Modals.svelte";
    import Modals from "$lib/components/modal/Modals.svelte";
    import Sidebar from "$lib/components/sidebar/Sidebar.svelte";
    import { setContext } from "svelte";

    let modals: ModalKind[] = [];
    setContext("addModal", (modal: ModalKind) => {
        modals = [...modals, modal];
    });
</script>

<Modals bind:modals />
<div id="wrapper">
    <Sidebar />
    <slot />
</div>

<style lang="scss">
    #wrapper {
        display: flex;
        align-items: stretch;
        height: 100%;
    }
</style>
