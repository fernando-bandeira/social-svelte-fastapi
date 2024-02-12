<script>
  import AuthWrapper from "../../../utils/AuthWrapper.svelte";
  import { userContext } from "../../../stores/userContext.js";
  import api from "../../../utils/api";
  import { Button, Title, Paper, Text } from "@svelteuidev/core";
  import Header from "../../../components/Header.svelte";
  import Post from "../../../components/Post.svelte";

  export let data;
  $: profileId = Number(data.slug);

  let user;
  userContext.subscribe((value) => {
    user = value;
  });

  let profileData;
  let followData;
  let posts;
  let loading = true;

  const fetchData = async () => {
    if (user?.id) {
      loading = true;
      const res = await api.get(`/user/${profileId}/`);
      profileData = res.data;
      followData = profileData.followInfo;
      if (followData?.approved || user.id === profileId || profileData.public) {
        const resPosts = await api.get(`/posts/${profileId}/`);
        posts = resPosts.data;
      }
      loading = false;
    }
  };

  $: user, profileId, fetchData();

  const follow = async () => {
    await api.post(`/${user.id}/follows/${profileId}/`);
    fetchData();
  };

  const unfollow = async () => {
    await api.delete(`/${user.id}/follows/${profileId}/`);
    fetchData();
  };
</script>

<AuthWrapper>
  <Header userId={user?.id} />
  {#if !loading}
    <div id="box">
      <Paper>
        <div id="title-action">
          <Title>{profileData.name}</Title>
          <div id="profile-info">
            {#if user.id !== profileId}
              {#if followData?.approved}
                <Button color="red" on:click={unfollow}>Parar de seguir</Button>
              {:else if followData?.requested}
                <Button color="red" on:click={unfollow}
                  >Cancelar solicitação</Button
                >
              {:else}
                <Button on:click={follow}>Seguir</Button>
              {/if}
            {/if}
            <Text>
              Seguidores: {followData.followers} | Seguindo: {followData.following}
              {#if profileId !== user.id}
                | Seguidores em comum: {followData.mutual}
              {/if}
            </Text>
          </div>
        </div>
        <hr />
        {#if followData?.approved || user.id === profileId || profileData.public}
          {#each posts as post (post.id)}
            <Post userId={user?.id} {...post} on:update={fetchData} />
          {/each}
        {:else}
          Você não segue esse usuário.
        {/if}
      </Paper>
    </div>
  {/if}
</AuthWrapper>

<style>
  #box {
    width: 900px;
    margin: 0 auto;
  }
  #title-action {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    gap: 10px;
  }
  #profile-info {
    display: flex;
    align-items: center;
    gap: 10px;
  }
</style>
