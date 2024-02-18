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

  const fetchFollowers = async () => {
    const res = await api.get(`/follows/followers/${profileId}/`);
    data = res.data;
    loading = false;
  };

  const fetchFollowing = async () => {
    const res = await api.get(`/follows/following/${profileId}/`);
    data = res.data;
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
</script>

<Modal
  opened={modalOpened}
  on:close={() => {
    modalOpened = false;
    dispatch("close");
  }}
  title={profileName}
  target="body"
>
  <Tabs on:change={onTabChange}>
    <Tabs.Tab label="Seguidores" tabKey="followers"></Tabs.Tab>
    <Tabs.Tab label="Seguindo" tabKey="following"></Tabs.Tab>
  </Tabs>
  {#if !loading}
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
  {/if}
</Modal>

<style>
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
