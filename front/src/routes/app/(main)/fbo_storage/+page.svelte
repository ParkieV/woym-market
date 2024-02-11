<script lang="ts">
    import { ChangeList } from "$lib/components/datagrid/changes";
    import type { OfferBase } from "$lib/data/offers";
    import Footer from "../Footer.svelte";
    import Toolbar from "../Toolbar.svelte";

    let changes = new ChangeList<{ sku: number }, "sku">();
    let filter: (storage: OfferBase) => boolean = () => true;
</script>

<Toolbar on:filterChanged={f => (filter = f.detail)} />
<h1>Work in progress</h1>
<Footer bind:changes />
