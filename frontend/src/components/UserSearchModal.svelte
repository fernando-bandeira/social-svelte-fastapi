<script>
  import { TextInput, Modal, Paper, Text, Button } from "@svelteuidev/core";
  import api from "../utils/api";
  import { MagnifyingGlass } from "radix-icons-svelte";
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  export let searchUsersModalOpened = false;
  export let userId;
  let search = "";
  let users = [];
  let usersPage = 1;

  const searchUsers = async (query, accumulate = false) => {
    if (query !== "") {
      const res = await api.get(`/users/?name=${query}&page=${usersPage}`);
      if (accumulate) {
        users = users.concat(res.data);
      } else {
        users = res.data;
      }
    }
  };

  const fetchUser = async (id, index) => {
    const res = await api.get(`/users/${id}/`);
    users[index] = res.data;
  };

  const checkScroll = () => {
    const div = document.querySelector("#users-list");
    if (div.scrollTop + div.clientHeight === div.scrollHeight) {
      usersPage++;
      searchUsers(search, true);
    }
  };

  const follow = async (profileId, index) => {
    await api.post(`/follows/${userId}/${profileId}/`);
    fetchUser(profileId, index)
  };

  const unfollow = async (publicProfile, profileId, index) => {
    if (!publicProfile) {
      if (!confirm(`Este perfil é privado. Deseja mesmo parar de seguir?`)) {
        return;
      }
    }
    await api.delete(`/follows/${userId}/${profileId}/`);
    fetchUser(profileId, index)
  };

  const cancelRequest = async (profileId, index) => {
    await api.delete(`/follows/${userId}/${profileId}/`);
    fetchUser(profileId, index)
  };
</script>

<Modal
  opened={searchUsersModalOpened}
  on:close={() => dispatch("close")}
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
    {#each users as user, index (user.id)}
      <div class="user-card">
        <Paper>
          <div id="card-content">
            <div>
              <Text><a href={`/profile/${user.id}/`}>{user.name}</a></Text>
              <Text size="sm">{user.followInfo.mutual} seguidor(es) em comum</Text>
            </div>
            {#if !user.followInfo.requested}
              <Button on:click={() => follow(user.id, index)}>Seguir</Button>
            {:else if !user.followInfo.approved}
              <Button
                color="red"
                on:click={() => cancelRequest(user.id, index)}
              >
                Cancelar pedido
              </Button>
            {:else}
              <Button
                color="red"
                on:click={() => unfollow(user.public, user.id, index)}
              >
                Parar de seguir
              </Button>
            {/if}
          </div>
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
  #card-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  a {
    text-decoration: none;
  }
  a:hover {
    text-decoration: underline;
  }
</style>
