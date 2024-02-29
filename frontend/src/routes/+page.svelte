<script>
  import AuthWrapper from "../utils/AuthWrapper.svelte";
  import api from "../utils/api";
  import { userContext } from "../stores/userContext";
  import { Button, Textarea, Paper, Alert } from "@svelteuidev/core";
  import { Check, Cross2 } from "radix-icons-svelte";
  import Header from "../components/Header.svelte";
  import Post from "../components/Post.svelte";
  import UserTagModal from "./UserTagModal.svelte";

  let showSuccessMessage = false;
  let showErrorMessage = false;
  let alertMessage;
  let tagUsersModalOpened = false;
  let tags = {};

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

  let posts = [];
  const fetchData = async () => {
    if (user?.id) {
      try {
        const res = await api.get(`/posts/feed/${user.id}/`);
        posts = res.data;
      } catch (err) {
        handleAlert(true, "Erro ao carregar posts.");
      }
    }
  };
  $: user, fetchData();

  let post;
  const createPost = async () => {
    try {
      const regex = /@([^@]+)@/g;
      const matches = post.match(regex);
      if (matches) {
        for (const match of matches) {
          let name = match.slice(1, -1);
          if (tags[name]) {
            post = post.replace(match, `@${tags[name]}@`);
          } else {
            handleAlert(true, `Sintaxe inválida: ${match}`);
            return;
          }
        }
      }

      await api.post("/posts/", {
        content: post,
        author: user.id,
        date: new Date().toLocaleString("en-GB"),
        repost: false,
        reference: null,
      });
      post = "";
      handleAlert(false, "Publicação realizada com sucesso!");
    } catch (err) {
      handleAlert(true, "Erro ao publicar.");
    }
    fetchData();
  };

  const handleTagUser = () => {
    if (
      post === "@" ||
      (post?.endsWith("@") && !/^[a-zA-Z0-9@]$/.test(post[post.length - 2]))
    ) {
      tagUsersModalOpened = true;
    }
  };

  $: post, handleTagUser();
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
  <UserTagModal
    {tagUsersModalOpened}
    on:close={() => (tagUsersModalOpened = false)}
    on:userClicked={(e) => {
      post = post + `${e.detail.name}@ `;
      tags[e.detail.name] = e.detail.id;
      tagUsersModalOpened = false;
    }}
  />
  <div id="box">
    <Paper>
      <form on:submit={createPost}>
        <Textarea bind:value={post} />
        <br />
        <Button type="submit">Postar</Button>
      </form>
      <hr />
      {#each posts as post (post.id)}
        <Post userId={user?.id} {...post} on:update={fetchData} />
      {/each}
    </Paper>
  </div>
</AuthWrapper>

<style>
  #box {
    width: 900px;
    margin: 0 auto;
  }
</style>
