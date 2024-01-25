<script lang="ts">
    import type { ModalKind } from "./Modals.svelte";
    import Modals from "./Modals.svelte";
    import Sidebar from "./Sidebar.svelte";
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
