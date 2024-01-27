<script lang="ts">
    import { fetchUserInfo, patchUserInfo, type Settings } from "$lib/data/settings";
    import { onMount } from "svelte";

    let settings: Settings | undefined = undefined;

    async function ok() {
        try {
            if (settings) await patchUserInfo(settings);
        } catch {
            alert("Произошла ошибка при обновлении настроек.");
        }
    }

    onMount(async () => {
        settings = await fetchUserInfo();
    });
</script>

<main>
    <h1>Настройки</h1>
    <div>
        {#if settings}
            <label>
                <span>Текущий курс</span>
                <input type="number" min="0" bind:value={settings.rate} />
            </label>
            <label>
                <span>Скидка на товары (%)</span>
                <input type="number" min="0" max="99" bind:value={settings.discount_purchase} />
            </label>
            <label>
                <span>Комиссия за продажу в FBY (%)</span>
                <input type="number" min="0" max="99" bind:value={settings.fby_sales_commission} />
            </label>
        {/if}
    </div>
    <menu class="bottombar">
        <div style:flex="1" />
        <button class="confirm" on:click={ok}>Сохранить</button>
    </menu>
</main>

<style lang="scss">
    @use "mixins" as *;

    main {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 8px;

        > h1 {
            font-size: 21px;
            margin-bottom: 8px;
            padding: 20px 20px 0 20px;
        }
        > div {
            flex: 1;
            display: flex;
            flex-direction: column;
            width: 600px;
            padding: 0 20px;
            gap: 12px;

            > label {
                display: flex;
                justify-content: space-between;
                font-size: 16px;
                > input {
                    font-size: 14px;
                    width: 100px;
                }
            }
        }
    }

    .bottombar {
        display: flex;
        align-items: center;
        padding: 16px;
        gap: 16px;
        background-color: #ebebeb;
        > button {
            @include primary-button;
            padding: 0 16px;
            height: 40px;
            border: 0;
            min-width: 100px;
        }
    }
</style>
