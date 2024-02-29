<script>
  import AuthWrapper from "../../../utils/AuthWrapper.svelte";
  import { userContext } from "../../../stores/userContext.js";
  import api from "../../../utils/api";
  import { Button, Title, Paper, Text, Box, Alert } from "@svelteuidev/core";
  import Header from "../../../components/Header.svelte";
  import Post from "../../../components/Post.svelte";
  import FollowersModal from "../../../components/FollowersModal.svelte";
  import { Check, Cross2 } from "radix-icons-svelte";

  export let data;
  $: profileId = Number(data.slug);

  let showSuccessMessage = false;
  let showErrorMessage = false;
  let alertMessage;

  const handleAlert = (isError, msg) => {
    alertMessage = msg;
    showErrorMessage = isError;
    showSuccessMessage = !isError;
    setTimeout(() => {
      showErrorMessage = false;
      showSuccessMessage = false;
    }, 5000);
  };

  let user;
  userContext.subscribe((value) => {
    user = value;
  });

  let profileData;
  let followData;
  let posts;
  let loading = true;

  let modalOpened = false;

  const fetchData = async () => {
    if (user?.id) {
      try {
        loading = true;
        const res = await api.get(`/users/${profileId}/`);
        profileData = res.data;
        followData = profileData.followInfo;
        if (
          followData?.approved ||
          user.id === profileId ||
          profileData.public
        ) {
          const resPosts = await api.get(`/posts/user/${profileId}/`);
          posts = resPosts.data;
        }
        loading = false;
      } catch (err) {
        handleAlert(true, "Erro ao carregar dados do usuário.");
      }
    }
  };

  $: user, profileId, fetchData();

  const follow = async () => {
    try {
      await api.post(`/follows/${user.id}/${profileId}/`);
    } catch (err) {
      handleAlert(true, "Erro ao seguir usuário.");
    }
    fetchData();
  };

  const unfollow = async () => {
    if (!profileData.public) {
      if (!confirm(`Este perfil é privado. Deseja mesmo parar de seguir?`)) {
        return;
      }
    }
    try {
      await api.delete(`/follows/${user.id}/${profileId}/`);
    } catch (err) {
      handleAlert(true, "Erro ao deixar de seguir usuário.");
    }
    fetchData();
  };

  const cancelRequest = async () => {
    try {
      await api.delete(`/follows/${user.id}/${profileId}/`);
    } catch (err) {
      handleAlert(true, "Erro ao cancelar solicitação.");
    }
    fetchData();
  };
</script>

<AuthWrapper>
  <Header userId={user?.id} />
  <div style="position: fixed; bottom: 40px; right: 20px">
    {#if showSuccessMessage || showErrorMessage}
      <Alert
        color={showSuccessMessage ? "teal" : "red"}
        icon={showSuccessMessage ? Check : Cross2}
        withCloseButton
        on:close={() => {
          showSuccessMessage = false;
          showErrorMessage = false;
        }}
      >
        {alertMessage}
      </Alert>
    {/if}
  </div>
  {#if !loading}
    <FollowersModal
      {modalOpened}
      {profileId}
      userId={user.id}
      profileName={profileData.name}
      on:modalClosed={() => (modalOpened = false)}
    />
    <div id="box">
      <Paper>
        <div id="title-action">
          <Title>{profileData.name}</Title>
          <div id="profile-info">
            {#if user.id !== profileId}
              {#if followData?.approved}
                <Button color="red" on:click={unfollow}>Parar de seguir</Button>
              {:else if followData?.requested}
                <Button color="red" on:click={cancelRequest}
                  >Cancelar solicitação</Button
                >
              {:else}
                <Button on:click={follow}>Seguir</Button>
              {/if}
            {/if}
            <div id="clickable-info">
              <Box on:click={() => (modalOpened = true)}>
                <Text>
                  Seguidores: {followData.followers} | Seguindo: {followData.following}
                  {#if profileId !== user.id}
                    | Seguidores em comum: {followData.mutual}
                  {/if}
                </Text>
              </Box>
            </div>
          </div>
        </div>
        <hr />
        {#if followData?.approved || user.id === profileId || profileData.public}
          {#each posts as post (post.id)}
            <Post userId={user?.id} {...post} on:update={fetchData} />
          {/each}
        {:else}
          <Text>Você não segue esse usuário.</Text>
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
  #clickable-info {
    cursor: pointer;
  }
</style>
