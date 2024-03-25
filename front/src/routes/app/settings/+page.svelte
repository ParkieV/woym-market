<script lang="ts">
    import { patchSettings } from "$lib/data/settings";
    import NumberInput from "./NumberInput.svelte";
    import { userCanModify } from "$lib/data/user";
    import type { PageData } from "./$types";

    export let data: PageData;

    let form: HTMLFormElement;
    let disabled = false;

    async function ok() {
        await patchSettings(data.settings);
    }
</script>

<main>
    <form on:input={() => (disabled = !form.checkValidity())} bind:this={form}>
        <h1>НАСТРОЙКИ</h1>
        <section>
            <h2>Основное</h2>
            <NumberInput
                label="Текущий курс"
                min={0}
                readonly={!$userCanModify}
                bind:value={data.settings.rate}
            />
            <NumberInput
                label="Скидка на товары (%)"
                min={0}
                max={99}
                readonly={!$userCanModify}
                bind:value={data.settings.discount_purchase}
            />
            <NumberInput
                label="Комиссия за продажу в FBO (%)"
                min={0}
                max={99}
                readonly={!$userCanModify}
                bind:value={data.settings.fbo_sales_commission}
            />
        </section>
        <section>
            <h2>Налоги</h2>
            <h3>В процентах</h3>
            {#each data.settings.markets as market}
                <NumberInput
                    label={`${market.name} (${market.type})`}
                    min={0}
                    max={99}
                    readonly={!$userCanModify}
                    bind:value={market.tax}
                />
            {/each}
        </section>
        <section>
            <h2>Цена длительного хранения</h2>
            <h3>Рублей за литр в день</h3>
            {#each data.settings.markets as market}
                <NumberInput
                    label={`${market.name} (${market.type})`}
                    min={0}
                    readonly={!$userCanModify}
                    bind:value={market.long_term_storage_cost}
                />
            {/each}
        </section>
    </form>
    <footer>
        <div style:flex="1" />
        {#if $userCanModify}
            <button class="confirm" {disabled} on:click={ok}>Сохранить</button>
        {/if}
    </footer>
</main>

<style lang="scss">
    @use "mixins" as *;

    main {
        flex: 1;
        display: flex;
        flex-direction: column;

        > form {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            padding: 40px;
            gap: 24px;

            > h1 {
                font-size: 28px;
            }

            section {
                display: flex;
                flex-direction: column;
                max-width: 600px;
                gap: 12px;

                > h2 {
                    font-size: 20px;
                    padding: 12px 0 0 0;
                }
                > h3 {
                    font-size: 16px;
                    margin-top: -10px;
                    font-weight: 400;
                }
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
