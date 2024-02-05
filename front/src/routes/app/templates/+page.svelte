<script lang="ts" context="module">
    export type Template = {
        id: number;
        name: string;

        use_total_price: boolean;
        use_attractive_price_threshold: boolean;
        use_moderately_attractive_price_threshold: boolean;
        use_your_price_for_buyers: boolean;
        use_best_price_wm: boolean;
        use_best_price_im: boolean;
        use_minimum_group_price: boolean;

        /** Number that the resulting price will be divided by. */
        n: number;
        /** Amount that will be added to the price (in percent). */
        m: number;
    };
</script>

<script lang="ts">
    import { fetchAuthenticated } from "$lib/auth";
    import { getContext, onMount } from "svelte";
    import type { ModalKind } from "../Modals.svelte";
    import TemplateCard from "./TemplateCard.svelte";

    let templates: Template[] = [];

    const addModal = getContext<(modal: ModalKind) => void>("addModal");
    onMount(async () => {
        let _templates: Template[] = await (await fetchAuthenticated("data/pricing-schemes")).json();
        _templates.sort((a, b) => a.id - b.id);
        templates = _templates;
    });

    const update = async () => {
        let promises = [];
        for (const id of changed) {
            let template = templates.find(x => x.id === id);
            let promise = fetchAuthenticated("data/pricing-schemes", {
                method: "PATCH",
                body: JSON.stringify(template),
                headers: {
                    "Content-Type": "application/json"
                }
            });
            promises.push(promise);
        }
        addModal({
            kind: "await",
            errorHeader: "Ошибка при сохранении изменений в формуле",
            header: "Обновляем данные на сервере...",
            promise: Promise.all(promises)
        });
    };

    const changed = new Set<number>();
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
        <button class="confirm" on:click={update}>Сохранить изменения</button>
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
            background-color: white;
            button {
                padding-left: 16px;
                padding-right: 16px;
                height: 40px;
                &.confirm {
                    @include primary-button;
                }
            }
        }
    }
</style>
