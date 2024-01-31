<script>
  import LoginWrapper from "../../utils/LoginWrapper.svelte";
  import axios from "axios";
  import { userContext } from "../../stores/userContext";
  import { goto } from "$app/navigation";
  import { TextInput, PasswordInput, Button } from "@svelteuidev/core";
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
  <form on:submit={login}>
    <TextInput bind:value={email} icon={EnvelopeClosed} />
    <br />
    <PasswordInput bind:value={password} />
    <br />
    <Button type="submit">Entrar</Button>
  </form>
</LoginWrapper>
