<script>
  import LoginWrapper from "../../utils/LoginWrapper.svelte";
  import axios from "axios";
  import { goto } from "$app/navigation";
  import {
    TextInput,
    PasswordInput,
    Button,
    Paper,
    Checkbox,
    Text,
    Alert,
  } from "@svelteuidev/core";
  import { Check, Cross2, EnvelopeClosed } from "radix-icons-svelte";

  const apiBase = import.meta.env.VITE_API_PATH;

  let email;
  let name;
  let password;
  let publicProfile;

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

  const register = async () => {
    try {
      const res = await axios.post(apiBase + "register/", {
        name: name,
        email: email,
        password: password,
        public: publicProfile,
      });
      goto("/login");
    } catch (err) {
      handleAlert(true, "Erro ao registrar usuário.");
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
      <Text><label for="name">Nome:</label></Text>
      <TextInput bind:value={name} id="name" placeholder="Fulano de Tal" />
      <br />
      <Text><label for="email">E-mail:</label></Text>
      <TextInput
        bind:value={email}
        icon={EnvelopeClosed}
        id="email"
        placeholder="fulano@email.com"
      />
      <br />
      <Text><label for="password">Senha:</label></Text>
      <PasswordInput bind:value={password} id="password" placeholder="******" />
      <br />
      <div id="public-section">
        <Checkbox bind:checked={publicProfile} id="public" />
        <Text>
          <label for="public">Perfil público</label>
        </Text>
      </div>
      <br />
      <div id="actions">
        <Button on:click={register}>Registrar</Button>
        <Text>
          <a href="/login">Já possuo uma conta</a>
        </Text>
      </div>
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
  #public-section {
    display: flex;
    gap: 10px;
    align-items: center;
  }
</style>
