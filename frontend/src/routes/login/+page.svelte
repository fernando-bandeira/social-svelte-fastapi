<script>
  import LoginWrapper from "../../utils/LoginWrapper.svelte";
  import axios from "axios";
  import { userContext } from "../../stores/userContext";
  import { goto } from "$app/navigation";
  import {
    TextInput,
    PasswordInput,
    Button,
    Paper,
    Text,
    Alert,
  } from "@svelteuidev/core";
  import { Check, Cross2, EnvelopeClosed } from "radix-icons-svelte";

  const apiBase = import.meta.env.VITE_API_PATH;

  let email;
  let password;

  let showSuccessMessage = false;
  let showErrorMessage = false;
  let alertMessage;

  const handleAlert = (isError, msg) => {
    alertMessage = msg;
    showErrorMessage = isError;
    showSuccessMessage = !isError;
    setTimeout(() => {
      showErrorMessage = false;
      showSuccessMessage = false;
    }, 5000);
  };

  const login = async () => {
    try {
      const res = await axios.post(apiBase + "login/", {
        email: email,
        password: password,
      });
      localStorage.setItem("access", res.data.access);
      localStorage.setItem("refresh", res.data.refresh);
      userContext.set({
        id: res.data.user_id,
        email: res.data.user_email,
      });
      goto("/");
    } catch (err) {
      handleAlert(true, "Erro ao autenticar.");
    }
  };
</script>

<LoginWrapper>
  <div style="position: fixed; bottom: 40px; right: 20px">
    {#if showSuccessMessage || showErrorMessage}
      <Alert
        color={showSuccessMessage ? "teal" : "red"}
        icon={showSuccessMessage ? Check : Cross2}
        withCloseButton
        on:close={() => {
          showSuccessMessage = false;
          showErrorMessage = false;
        }}
      >
        {alertMessage}
      </Alert>
    {/if}
  </div>
  <div id="box">
    <Paper>
      <form on:submit={login}>
        <Text><label for="email">E-mail:</label></Text>
        <TextInput bind:value={email} icon={EnvelopeClosed} id="email" />
        <br />
        <Text><label for="password">Senha:</label></Text>
        <PasswordInput bind:value={password} id="password" />
        <br />
        <div id="actions">
          <Button type="submit">Entrar</Button>
          <Text>
            <a href="/register">Criar conta</a>
          </Text>
        </div>
      </form>
    </Paper>
  </div>
</LoginWrapper>

<style>
  #box {
    width: 900px;
    margin: 0 auto;
  }
  #actions {
    display: flex;
    gap: 10px;
    align-items: center;
  }
  a {
    text-decoration: none;
  }
  a:hover {
    text-decoration: underline;
  }
</style>
