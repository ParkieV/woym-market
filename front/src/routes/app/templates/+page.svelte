<script lang="ts">
    import TemplateCard from "./TemplateCard.svelte";
    import { patchTemplates } from "$lib/data/templates";
    import { userCanModify } from "$lib/data/user";
    import type { PageData } from "./$types";

    export let data: PageData;
    let changed = new Set<string>();

    const save = async () => {
        let _templates = Array.from(changed).flatMap(name => {
            let template = data.templates.find(x => x.name === name);
            return template ?? [];
        });

        let ok = await patchTemplates(_templates);
        if (ok) {
            changed.clear();
            changed = changed;
        }
    };
</script>

<main>
    <div>
        <h1>ФОРМУЛЫ ЦЕНООБРАЗОВАНИЯ</h1>
        <ul>
            {#each data.templates as template}
                <TemplateCard
                    bind:template
                    on:changed={() => {
                        changed.add(template.name);
                        changed = changed;
                    }}
                />
            {/each}
        </ul>
    </div>
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

        > div {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 40px;
            overflow-y: auto;

            > h1 {
                font-size: 28px;
            }
            > ul {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 20px;
                padding: 15px;
            }
        }
        > footer {
            display: flex;
            justify-content: end;
            align-items: center;
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
