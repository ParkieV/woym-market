<script lang="ts">
    import { fetchSettings, patchSettings, type Settings } from "$lib/data/settings";
    import { onMount } from "svelte";
    import NumberInput from "./NumberInput.svelte";
    import { userCanModify } from "$lib/user";

    let settings: Settings | undefined = undefined;

    async function ok() {
        if (!settings) return;
        await patchSettings(settings);
    }

    onMount(async () => {
        settings = await fetchSettings();
    });

    let form: HTMLFormElement;
    let disabled = false;
</script>

<main>
    <form on:input={() => (disabled = !form.checkValidity())} bind:this={form}>
        <h1>НАСТРОЙКИ</h1>
        {#if settings}
            <section>
                <h2>Основное</h2>
                <NumberInput
                    label="Текущий курс"
                    min={0}
                    readonly={!$userCanModify}
                    bind:value={settings.rate}
                />
                <NumberInput
                    label="Скидка на товары (%)"
                    min={0}
                    max={99}
                    readonly={!$userCanModify}
                    bind:value={settings.discount_purchase}
                />
                <NumberInput
                    label="Комиссия за продажу в FBY (%)"
                    min={0}
                    max={99}
                    readonly={!$userCanModify}
                    bind:value={settings.fby_sales_commission}
                />
            </section>
            <section>
                <h2>Налоги</h2>
                {#each settings.taxes as market}
                    <NumberInput
                        label={`${market.name} (${market.type})`}
                        min={0}
                        max={99}
                        readonly={!$userCanModify}
                        bind:value={market.tax}
                    />
                {/each}
            </section>
        {/if}
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
            margin: 40px;
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
                    font-size: 24px;
                    padding: 20px 20px 0 0;
                }
            }
        }

        > footer {
            display: flex;
            align-items: center;
            height: 70px;
            padding: 0 16px;
            gap: 16px;
            background-color: #ebebeb;
            > button {
                @include primary-button;
                height: 40px;
            }
        }
    }
</style>
