<script>
  import { TextInput, Modal, Paper, Text } from "@svelteuidev/core";
  import api from "../utils/api";
  import { MagnifyingGlass } from "radix-icons-svelte";
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  export let searchUsersModalOpened = false;
  let search = "";
  let users = [];

  let usersPage = 1;
  const searchUsers = async (query, accumulate = false) => {
    if (query !== "") {
      const res = await api.get(`/users?name=${query}&page=${usersPage}`);
      if (accumulate) {
        users = users.concat(res.data);
      } else {
        users = res.data;
      }
    }
  };

  const checkScroll = () => {
    const div = document.querySelector("#users-list");
    if (div.scrollTop + div.clientHeight === div.scrollHeight) {
      usersPage++;
      searchUsers(search, true);
    }
  };
</script>

<Modal
  opened={searchUsersModalOpened}
  on:close={() => {
    searchUsersModalOpened = false;
    dispatch("close");
  }}
  title="Buscar usuários"
  target="body"
  overflow="inside"
>
  <TextInput
    autofocus
    bind:value={search}
    on:input={(e) => {
      users = [];
      usersPage = 1;
      searchUsers(e.target.value);
    }}
    icon={MagnifyingGlass}
    placeholder="Buscar usuários"
  />
  <div id="users-list" on:scroll={checkScroll}>
    {#each users as user (user.id)}
      <div class="user-card">
        <Paper>
          <Text><a href={`/profile/${user.id}/`}>{user.name}</a></Text>
          <Text size="sm">{user.mutual} seguidor(es) em comum</Text>
        </Paper>
      </div>
    {/each}
  </div>
</Modal>

<style>
  #users-list {
    margin-top: 20px;
    max-height: 500px;
    overflow-y: auto;
  }
  .user-card {
    margin: 5px 0;
  }
  a {
    text-decoration: none;
  }
  a:hover {
    text-decoration: underline;
  }
</style>
