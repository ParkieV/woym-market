<script lang="ts">
    import { getContext, onMount } from "svelte";
    import type { ModalKind } from "$lib/components/modal/Modals.svelte";
    import TemplateCard from "./TemplateCard.svelte";
    import { fetchTemplates, patchTemplate, type Template } from "$lib/data/templates";

    const addModal = getContext<(modal: ModalKind) => void>("addModal");

    let templates: Template[] = [];
    const changed = new Set<number>();

    const update = async () => {
        let promises = [];
        for (const id of changed) {
            let template = templates.find(x => x.id === id);
            if (template) {
                let promise = patchTemplate(template);
                promises.push(promise);
            }
        }
        addModal({
            kind: "await",
            errorHeader: "Ошибка при сохранении изменений в формуле",
            header: "Обновляем данные на сервере...",
            promise: Promise.all(promises)
        });
    };

    onMount(async () => {
        templates = await fetchTemplates();
    });
</script>

<main>
    <div>
        <header>
            <h1>ФОРМУЛЫ ЦЕНООБРАЗОВАНИЯ</h1>
        </header>
        <ul>
            {#each templates as template}
                <TemplateCard bind:template on:changed={() => changed.add(template.id)} />
            {/each}
        </ul>
    </div>
    <footer>
        <button on:click={update}>Сохранить</button>
    </footer>
</main>

<style lang="scss">
    @use "mixins" as *;

    main {
        display: flex;
        flex-direction: column;
        padding: 20px;
        flex: 1;
        > div {
            overflow-y: scroll;
            display: flex;
            flex-direction: column;
            padding: 20px;
            flex: 1;
            > header {
                padding-left: 12px;
                padding-bottom: 20px;
                > h1 {
                    font-size: 28px;
                }
            }
            > ul {
                flex: 1;
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                align-content: start;
                align-items: start;
                gap: 20px;
                padding: 30px 0;
            }
        }
        > footer {
            display: flex;
            justify-content: end;
            align-items: center;
            margin: 0 -20px -20px -20px;
            padding: 16px;
            gap: 16px;
            background-color: #ebebeb;
            button {
                @include primary-button;
                height: 40px;
            }
        }
    }
</style>
