<script>
  import api from "../utils/api";
  import { Paper, Modal, TextInput, Text, Box } from "@svelteuidev/core";
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  export let tagUsersModalOpened = false;
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
  opened={tagUsersModalOpened}
  on:close={() => dispatch("close")}
  title="Marcar usuários"
  target="body"
>
  <TextInput
    autofocus
    bind:value={search}
    on:input={(e) => {
      users = [];
      usersPage = 1;
      searchUsers(e.target.value);
    }}
    placeholder="Buscar usuários"
  />
  <div id="users-list" on:scroll={checkScroll}>
    {#each users as user (user.id)}
      <div class="user-card">
        <Box
          on:click={() => {
            dispatch("userClicked", { id: user.id, name: user.name });
          }}
        >
          <Paper>
            <Text>
              {user.name}
            </Text>
            <Text size="sm">{user.mutual} seguidor(es) em comum</Text>
          </Paper>
        </Box>
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
    cursor: pointer;
  }
</style>
