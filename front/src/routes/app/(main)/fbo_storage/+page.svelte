<script lang="ts">
    import { ChangeList } from "$lib/components/datagrid/changes";
    import Footer from "../Footer.svelte";

    let changes = new ChangeList<{ sku: number }, "sku">();
</script>

<h1>Work in progress</h1>
<Footer bind:changes />
