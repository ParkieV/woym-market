<script lang="ts">
    import { goto } from "$app/navigation";
    import Input from "$lib/components/Input.svelte";
    import { login as login_request } from "$lib/auth";

    let login: string;
    let password: string;

    async function onclick() {
        let login_result = login_request(login, password);
        login_result.then(success => {
            if (success) goto("/app");
            else alert("Не удалось войти в аккаунт.");
        });
        login_result.catch(() => {
            alert("Не удалось достичь сервера.");
        });
    }
</script>

<main>
    <h1>Вход в систему</h1>
    <div class="inputs">
        <Input bind:value={login} label="Логин" />
        <Input bind:value={password} label="Пароль" type="password" />
    </div>
    <button on:click={onclick}>Войти</button>
</main>

<style lang="scss">
    main {
        height: 100dvh;
        max-width: 600px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: stretch;
        padding: 20px;
        h1 {
            text-align: center;
            font-size: 24px;
            font-weight: normal;
        }
        .inputs {
            display: flex;
            flex-direction: column;

            margin-top: 16px;
            margin-bottom: 20px;
            gap: 12px;
        }
        button {
            font-size: 15px;
            color: white;
            background-color: #126ed6;
            border: 0;
            height: 56px;
            border-radius: 8px;
            font-size: 16px;
            margin-top: 20px;
        }
    }
</style>
