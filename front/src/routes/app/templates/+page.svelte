<script lang="ts">
    import { onMount } from "svelte";
    import TemplateCard from "./TemplateCard.svelte";
    import { fetchTemplates, patchTemplates, type Template } from "$lib/data/templates";
    import { userCanModify } from "$lib/user";

    let templates: Template[] = [];
    let changed = new Set<string>();

    const save = async () => {
        let _templates = Array.from(changed).flatMap(name => {
            let template = templates.find(x => x.name === name);
            return template ?? [];
        });

        let ok = await patchTemplates(_templates);
        if (ok) {
            changed.clear();
            changed = changed;
        }
    };

    onMount(async () => {
        templates = await fetchTemplates();
    });
</script>

<main>
    <header>
        <h1>ФОРМУЛЫ ЦЕНООБРАЗОВАНИЯ</h1>
    </header>
    <ul>
        {#each templates as template}
            <TemplateCard
                bind:template
                on:changed={() => {
                    changed.add(template.name);
                    changed = changed;
                }}
            />
        {/each}
    </ul>
    <footer>
        {#if $userCanModify}
            <button on:click={save} disabled={changed.size === 0}>Сохранить</button>
        {/if}
    </footer>
</main>

<style lang="scss">
    @use "mixins" as *;

    main {
        flex: 1;
        display: flex;
        flex-direction: column;
        padding: 20px;
        > header {
            padding-left: 12px;
            padding-bottom: 20px;
            > h1 {
                font-size: 28px;
            }
        }
        > ul {
            display: flex;
            flex-direction: column;
            align-items: center;
            overflow-y: auto;
            gap: 20px;
            padding: 15px 15px;
        }
        > footer {
            display: flex;
            justify-content: end;
            align-items: center;
            margin: 0 -20px -20px -20px;
            height: 70px;
            padding: 0 16px;
            gap: 16px;
            background-color: #ebebeb;
            button {
                @include primary-button;
                height: 40px;
            }
        }
    }
</style>
