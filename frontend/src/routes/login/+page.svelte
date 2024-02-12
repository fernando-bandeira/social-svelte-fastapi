<script>
  import LoginWrapper from "../../utils/LoginWrapper.svelte";
  import axios from "axios";
  import { userContext } from "../../stores/userContext";
  import { goto } from "$app/navigation";
  import { TextInput, PasswordInput, Button, Paper, Text } from "@svelteuidev/core";
  import { EnvelopeClosed } from "radix-icons-svelte";

  const apiBase = import.meta.env.VITE_API_PATH;

  let email;
  let password;

  const login = () => {
    axios
      .post(apiBase + "login/", {
        email: email,
        password: password,
      })
      .then((res) => {
        localStorage.setItem("access", res.data.access);
        localStorage.setItem("refresh", res.data.refresh);
        userContext.set({
          id: res.data.user_id,
          email: res.data.user_email,
        });
        goto("/");
      });
  };
</script>

<LoginWrapper>
  <div id="box">
    <Paper>
      <form on:submit={login}>
        <Text><label for="email">E-mail:</label></Text>
        <TextInput bind:value={email} icon={EnvelopeClosed} id="email" />
        <br />
        <Text><label for="password">Senha:</label></Text>
        <PasswordInput bind:value={password} id="password" />
        <br />
        <Button type="submit">Entrar</Button>
      </form>
    </Paper>
  </div>
</LoginWrapper>

<style>
  #box {
    width: 900px;
    margin: 0 auto;
  }
</style>
