<script>
  import AuthWrapper from "../../../utils/AuthWrapper.svelte";
  import { userContext } from "../../../stores/userContext.js";
  import api from "../../../utils/api";
  import { Button, Title, Paper } from "@svelteuidev/core";
  import Header from "../../../components/Header.svelte";
  import Post from "../../../components/Post.svelte";

  export let data;
  const profileId = Number(data.slug);

  let user;
  userContext.subscribe((value) => {
    user = value;
  });

  let profileData;
  let relationData;
  let posts;
  let loading = true;

  const fetchData = async () => {
    if (user?.id) {
      console.log(typeof user.id)
      const resProfile = await api.get(`/user/${profileId}`);
      profileData = resProfile.data;
      const resRelation = await api.get(`/${user.id}/follows/${profileId}/`);
      relationData = resRelation.data;
      if (relationData?.approved || user.id === profileId || profileData.public) {
        const resPosts = await api.get(`/posts/${profileId}/`);
        posts = resPosts.data;
      }
      loading = false;
    }
  };

  $: user, fetchData();

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
          {#if user.id !== profileId}
            {#if relationData?.approved}
              <Button color="red" on:click={unfollow}>Parar de seguir</Button>
            {:else if relationData?.requested}
              <Button color="red" on:click={unfollow}
                >Cancelar solicitação</Button
              >
            {:else}
              <Button on:click={follow}>Seguir</Button>
            {/if}
          {/if}
        </div>
        <hr />
        {#if relationData?.approved || user.id === profileId || profileData.public}
          {#each posts as post}
            <Post
              id={post.id}
              userId={user?.id}
              author={post.author}
              content={post.content}
              date={post.date}
            />
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
</style>
