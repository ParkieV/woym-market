<script lang="ts">
    import ExportWindow from "$lib/export/ExportWindow.svelte";
    import ImportWindow from "$lib/import/ImportWindow.svelte";
    import { userCanModify } from "$lib/data/user";
    import { page } from "$app/stores";
    import type { GridState } from "$lib/state";

    let import_open = false;
    let export_open = false;

    const reload = () => {
        ($page.data["state"] as GridState<any, any>)?.forceReload();
    };
</script>

<ExportWindow bind:open={export_open} />
{#if $userCanModify}
    <ImportWindow bind:open={import_open} on:import={reload} />
{/if}
<menu>
    <button on:click={() => (export_open = true)}>Экспорт</button>
    {#if $userCanModify}
        <button on:click={() => (import_open = true)}>Импорт</button>
    {/if}
</menu>

<style lang="scss">
    menu {
        display: flex;
        background-color: #f1f0f0;
        > button {
            background-color: transparent;
            border: 0;
            padding: 4px 12px;
            border-radius: 0;
            font-size: 15px;
            &:hover {
                background-color: #e2e2e2;
            }
        }
    }
</style>
