<script lang="ts">
    import type { Market } from "$lib/data/markets";
    import { createEventDispatcher, onMount } from "svelte";
    import NumberInput from "./NumberInput.svelte";
    import { userCanModify } from "$lib/data/user";

    export let market: Market;
    export let invalid: boolean;

    let dispatch = createEventDispatcher<{ change: void }>();
    let form: HTMLFormElement;
    onMount(() => (invalid = !form.checkValidity()));
</script>

<form
    on:input={() => (invalid = !form.checkValidity())}
    on:input={() => dispatch("change")}
    bind:this={form}
>
    <section>
        <h2>Основное</h2>
        <NumberInput
            label="Курс (долларов за рубль)"
            min={0}
            readonly={!$userCanModify}
            bind:value={market.rate}
        />
        <NumberInput
            label="Налог (%)"
            min={0}
            max={99}
            readonly={!$userCanModify}
            bind:value={market.tax}
        />
        <NumberInput
            label="Комиссия за продажу в FBO (%)"
            min={0}
            max={99}
            readonly={!$userCanModify}
            bind:value={market.fbo_sales_commission}
        />
    </section>
    <section>
        <h2>Логистика</h2>
        <NumberInput
            label="Цена длительного хранения (₽ / литр)"
            min={0}
            readonly={!$userCanModify}
            bind:value={market.long_term_storage_cost}
        />
        <NumberInput
            label="Порог для доп. логистики за 1 литр (л)"
            min={0}
            readonly={!$userCanModify}
            bind:value={market.volume_threshold_for_additional_logistics}
        />
        <NumberInput
            label="Цена доп. логистики за 1 литр (₽)"
            min={0}
            readonly={!$userCanModify}
            bind:value={market.cost_of_additional_logistics_per_liter}
        />
    </section>
    <section>
        <h2>Рекомендованная розничная цена (РРЦ)</h2>
        <p class="formula">X (₽) + «ОПТ» (₽) + «ОПТ» (₽) * Y%</p>
        <NumberInput
            label="X (₽)"
            min={0}
            readonly={!$userCanModify}
            bind:value={market.first_variable_for_recommended_retail_price}
        />
        <NumberInput
            label="Y (%)"
            min={0}
            readonly={!$userCanModify}
            bind:value={market.second_variable_for_recommended_retail_price}
        />
    </section>
    <section>
        <h2>Стоп-цена</h2>
        <p class="formula">X (₽) + «ОПТ» (₽) + «ОПТ» (₽) * Y%</p>
        <NumberInput
            label="X (₽)"
            min={0}
            readonly={!$userCanModify}
            bind:value={market.first_variable_for_stop_price}
        />
        <NumberInput
            label="Y (%)"
            min={0}
            readonly={!$userCanModify}
            bind:value={market.second_variable_for_stop_price}
        />
    </section>
    <section>
        <h2>Акции</h2>
        <NumberInput
            label="Скидка на товары (%)"
            min={0}
            max={99}
            readonly={!$userCanModify}
            bind:value={market.discount_purchase}
        />
        <NumberInput
            label="Цена до скидки (%)"
            min={0}
            max={99}
            readonly={!$userCanModify}
            bind:value={market.price_before_discount}
        />
        {#if market.type === "yandex"}
            <p class="formula">
                Ограничение на разницу между "целевая цена" и "цена до скидки": 5% &lt;= Разница
                &lt;= 99%
            </p>
        {:else if market.type === "ozon"}
            <p class="formula">
                Ограничение на разницу между "целевая цена" и "цена до скидки":<br />
                - Если цена &lt;= 400 рублей, то разница &gt;= 20 рублей<br />
                - Если цена от 400 до 10000 рублей, то разница &gt;= 5%<br />
                - Если цена &gt; 10000 рублей, то разница &gt;= 500<br />
            </p>
        {/if}
    </section>
    <section>
        <h2>Умная поставка</h2>
        <p class="formula">
            «заказы за 7 дней» * A + «заказы за 14 дней» * B + «заказы за 28 дней» * C + «заказы за
            60 дней» * D + «заказы за 120 дней» * E
        </p>
        <NumberInput
            label="A (Заказы за 7 дней)"
            readonly={!$userCanModify}
            bind:value={market.a_variable_for_smart_delivery}
        />
        <NumberInput
            label="B (Заказы за 14 дней)"
            readonly={!$userCanModify}
            bind:value={market.b_variable_for_smart_delivery}
        />
        <NumberInput
            label="C (Заказы за 28 дней)"
            readonly={!$userCanModify}
            bind:value={market.c_variable_for_smart_delivery}
        />
        <NumberInput
            label="D (Заказы за 60 дней)"
            readonly={!$userCanModify}
            bind:value={market.d_variable_for_smart_delivery}
        />
        <NumberInput
            label="E (Заказы за 120 дней)"
            readonly={!$userCanModify}
            bind:value={market.e_variable_for_smart_delivery}
        />
    </section>
</form>

<style lang="scss">
    form {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow-y: auto;
        padding: 40px;
        gap: 24px;
    }

    section {
        display: flex;
        flex-direction: column;
        max-width: 600px;
        gap: 8px;

        > h2 {
            font-size: 18px;
            padding: 12px 0 0 0;
        }

        > p {
            font-size: 18px;
            margin: 0 0 4px 0;
            &.formula {
                font-family: monospace;
                font-size: 16px;
                margin-top: -4px;
            }
        }
    }
</style>
