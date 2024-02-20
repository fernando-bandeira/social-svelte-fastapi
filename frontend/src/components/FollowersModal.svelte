<script>
  import { Modal, Tabs, Text, Paper } from "@svelteuidev/core";
  import { createEventDispatcher, onMount } from "svelte";
  import api from "../utils/api";

  const dispatch = createEventDispatcher();

  export let modalOpened;
  export let profileId;
  export let profileName;

  let data = [];
  let loading = true;
  let usersPage = 1;

  const fetchFollowers = async () => {
    const res = await api.get(
      `/follows/followers/${profileId}/?page=${usersPage}`,
    );
    data = data.concat(res.data);
    loading = false;
  };

  const fetchFollowing = async () => {
    const res = await api.get(
      `/follows/following/${profileId}/?page=${usersPage}`,
    );
    data = data.concat(res.data);
    loading = false;
  };

  onMount(async () => {
    await fetchFollowers();
    loading = false;
  });

  const onTabChange = (event) => {
    loading = true;
    const { key } = event.detail;
    switch (key) {
      case "followers":
        fetchFollowers();
        break;
      case "following":
        fetchFollowing();
        break;
    }
  };

  const checkScroll = () => {
    const div = document.querySelector("#users-list");
    if (div.scrollTop + div.clientHeight === div.scrollHeight) {
      usersPage++;
      fetchFollowers();
    }
  };
</script>

<Modal
  opened={modalOpened}
  on:close={() => dispatch("close")}
  title={profileName}
  target="body"
>
  <Tabs on:change={onTabChange}>
    <Tabs.Tab label="Seguidores" tabKey="followers"></Tabs.Tab>
    <Tabs.Tab label="Seguindo" tabKey="following"></Tabs.Tab>
  </Tabs>
  {#if !loading}
    <div id="users-list" on:scroll={checkScroll}>
      {#each data as follower (follower.id)}
        <div class="user-card">
          <Paper>
            <Text>
              <a href={`/profile/${follower.id}/`}>{follower.name}</a>
            </Text>
            <Text size="sm">{follower.mutual} seguidor(es) em comum</Text>
          </Paper>
        </div>
      {/each}
    </div>
  {/if}
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
