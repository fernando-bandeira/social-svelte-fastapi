<script>
  import AuthWrapper from "../../../utils/AuthWrapper.svelte";
  import { userContext } from "../../../stores/userContext.js";
  import api from "../../../utils/api";
  import { Button } from "@svelteuidev/core";
  import Header from "../../../components/Header.svelte";
  import Post from "../../../components/Post.svelte";

  export let data;
  const profileId = data.slug;

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
      const resProfile = await api.get(`/user/${profileId}`);
      profileData = resProfile.data;
      const resRelation = await api.get(`/${user.id}/follows/${profileId}/`);
      relationData = resRelation.data;
      if (relationData?.approved) {
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
    <div>
      <h1>Perfil de {profileData.name}</h1>
      {#if relationData?.approved}
        <Button color="red" on:click={unfollow}>Parar de seguir</Button>
      {:else if relationData?.requested}
        <Button color="red" on:click={unfollow}>Cancelar solicitação</Button>
      {:else}
        <Button on:click={follow}>Seguir</Button>
      {/if}
      <hr />
      {#if relationData?.approved}
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
    </div>
  {/if}
</AuthWrapper>
