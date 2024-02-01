<script>
  import Logout from "../routes/Logout.svelte";
  import { TextInput, Modal, Button, Paper } from "@svelteuidev/core";
  import api from "../utils/api";
  import { MagnifyingGlass } from "radix-icons-svelte";
  import { goto } from "$app/navigation";

  export let userId;

  let searchUsersModalOpened = false;
  let followRequestsModalOpened = false;
  let users = [];
  let followRequests = [];

  const searchUsers = async (search) => {
    const res = await api.get(`/users?email=${search}`);
    users = res.data;
  };

  const getFollowRequests = async () => {
    if (userId) {
      const res = await api.get(`/requests/${userId}/`);
      followRequests = res.data;
    }
  };

  $: userId, getFollowRequests();

  const approve = async (otherUser) => {
    await api.put(`/${userId}/approves/${otherUser}/`);
    fetchData();
  };

  const unfollow = async (otherUser) => {
    await api.delete(`/${otherUser}/follows/${userId}/`);
    fetchData();
  };
</script>

<Modal
  opened={searchUsersModalOpened}
  on:close={() => (searchUsersModalOpened = false)}
  title="Buscar usuários"
  target="body"
>
  <TextInput
    on:input={(e) => searchUsers(e.target.value)}
    icon={MagnifyingGlass}
    placeholder="Buscar usuários"
  />
  <div id="users-list">
    {#each users as user}
      <Paper><a href={`/profile/${user.id}`}>{user.name}</a></Paper>
    {/each}
  </div>
</Modal>
<Modal
  opened={followRequestsModalOpened}
  on:close={() => (followRequestsModalOpened = false)}
  title="Follow Requests"
  target="body"
>
  {#if followRequests.length > 0}
    {#each followRequests as request}
      <Paper>
        <div class="request-card">
          {request.requester_name}
          <div class="request-actions">
            <Button on:click={() => approve(request.requester)}>Aprovar</Button>
            <Button color="red" on:click={() => unfollow(request.requester)}
              >Recusar</Button
            >
          </div>
        </div>
      </Paper>
    {/each}
  {:else}
    Sem solicitações
  {/if}
</Modal>
<nav id="navbar">
  <a href="/">
    <img src="/logo.png" alt="Logo" height="40" />
  </a>
  <div id="navbar-actions">
    <TextInput
      readonly
      on:click={() => (searchUsersModalOpened = true)}
      icon={MagnifyingGlass}
      placeholder="Buscar usuários"
    />
    <Button on:click={() => goto(`/profile/${userId}/`)}>Perfil</Button>
    <Button on:click={() => (followRequestsModalOpened = true)}>
      Solicitações
    </Button>
    <Logout />
  </div>
</nav>

<style>
  #navbar {
    display: flex;
    justify-content: space-between;
    border-bottom: 1px solid #ccc;
    padding: 10px;
    margin-bottom: 10px;
    background-color: #fff;
  }
  #navbar-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }
  #users-list {
    margin-top: 20px;
  }
  .request-card {
    display: flex;
    justify-content: space-between;
  }
  .request-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }
</style>
