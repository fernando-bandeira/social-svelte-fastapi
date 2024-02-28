<script>
  import Logout from "../routes/Logout.svelte";
  import {
    TextInput,
    Modal,
    Button,
    Paper,
    Text,
    Tooltip,
  } from "@svelteuidev/core";
  import api from "../utils/api";
  import { MagnifyingGlass } from "radix-icons-svelte";
  import { goto } from "$app/navigation";
  import UserSearchModal from "./UserSearchModal.svelte";

  export let userId;

  let followRequestsModalOpened = false;
  let searchUsersModalOpened = false;
  let followRequests = [];

  const getFollowRequests = async () => {
    if (userId) {
      const res = await api.get(`/follows/requests/${userId}/`);
      followRequests = res.data;
    }
  };

  $: userId, getFollowRequests();

  const approve = async (otherUser) => {
    await api.put(`/follows/${otherUser}/${userId}/`);
    getFollowRequests();
  };

  const unfollow = async (otherUser) => {
    await api.delete(`/follows/${otherUser}/${userId}/`);
    getFollowRequests();
  };
</script>

<UserSearchModal
  {searchUsersModalOpened}
  {userId}
  on:close={() => (searchUsersModalOpened = false)}
/>
<Modal
  opened={followRequestsModalOpened}
  on:close={() => (followRequestsModalOpened = false)}
  title="Solicitações para seguir"
  target="body"
>
  {#if followRequests.length > 0}
    {#each followRequests as request (request.id)}
      <div style="margin-bottom: 10px;">
        <Paper>
          <div class="request-card">
            <Text>
              <a href={`/profile/${request.requester}/`}>
                {request.requester_name}
              </a>
            </Text>
            <div class="request-actions">
              <Button
                on:click={() => {
                  approve(request.requester);
                }}
              >
                Aprovar
              </Button>
              <Button
                color="red"
                on:click={() => {
                  unfollow(request.requester);
                }}
              >
                Recusar
              </Button>
            </div>
          </div>
        </Paper>
      </div>
    {/each}
  {:else}
    <Text>Não há solicitações.</Text>
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
    <Tooltip
      opened={followRequests.length > 0 && !followRequestsModalOpened}
      color="red"
      label={followRequests.length}
      position="bottom"
      placement="center"
      withArrow
    >
      <Button on:click={() => (followRequestsModalOpened = true)}>
        Solicitações
      </Button>
    </Tooltip>
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
  .request-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .request-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }
  a {
    text-decoration: none;
  }
  a:hover {
    text-decoration: underline;
  }
</style>
