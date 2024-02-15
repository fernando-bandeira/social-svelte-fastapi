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
    Checkbox,
    Text,
  } from "@svelteuidev/core";
  import { EnvelopeClosed } from "radix-icons-svelte";

  const apiBase = import.meta.env.VITE_API_PATH;

  let email;
  let name;
  let password;
  let publicProfile;

  const login = () => {
    axios
      .post(apiBase + "register/", {
        name: name,
        email: email,
        password: password,
        public: publicProfile,
      })
      .then((res) => {
        goto("/login");
      });
  };
</script>

<LoginWrapper>
  <div id="box">
    <Paper>
      <form on:submit={login}>
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
        <PasswordInput
          bind:value={password}
          id="password"
          placeholder="******"
        />
        <br />
        <div id="public-section">
          <Checkbox bind:checked={publicProfile} id="public" />
          <Text>
            <label for="public">Perfil público</label>
          </Text>
        </div>
        <br />
        <div id="actions">
          <Button type="submit">Registrar</Button>
          <Text>
            <a href="/login">Já possuo uma conta</a>
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
  #public-section {
    display: flex;
    gap: 10px;
    align-items: center;
  }
</style>
