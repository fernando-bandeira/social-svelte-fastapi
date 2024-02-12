<script>
  import AuthWrapper from "../utils/AuthWrapper.svelte";
  import api from "../utils/api";
  import { userContext } from "../stores/userContext";
  import {
    Button,
    Textarea,
    Paper,
    Modal,
    TextInput,
    Text,
    Alert,
    Box,
  } from "@svelteuidev/core";
  import { Check, Cross2 } from "radix-icons-svelte";
  import Header from "../components/Header.svelte";
  import Post from "../components/Post.svelte";

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

  let posts = [];
  const fetchData = async () => {
    if (user?.id) {
      const res = await api.get(`/feed/${user.id}/`);
      posts = res.data;
    }
  };
  $: user, fetchData();

  let users = [];
  let tagUsersModalOpened = false;
  const searchUsers = async (search) => {
    const res = await api.get(`/users?name=${search}`);
    users = res.data;
  };

  let post;
  const createPost = async () => {
    try {
      await api.post("/create-post/", {
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
  <Modal
    opened={tagUsersModalOpened}
    on:close={() => (tagUsersModalOpened = false)}
    title="Buscar usuários"
    target="body"
  >
    <TextInput
      autofocus
      on:input={(e) => searchUsers(e.target.value)}
      placeholder="Buscar usuários"
    />
    <div id="users-list">
      {#each users as user (user.id)}
        <div class="user-card">
          <Box
            on:click={() => {
              post = post + `${user.id}@ `;
              tagUsersModalOpened = false;
            }}
          >
            <Paper>
              <Text>
                {user.name}
              </Text>
              <Text size="sm">{user.mutual} seguidor(es) em comum</Text>
            </Paper>
          </Box>
        </div>
      {/each}
    </div>
  </Modal>
  <div id="box">
    <Paper>
      <form on:submit={createPost}>
        <Textarea bind:value={post} />
        <br />
        <Button type="submit">Postar</Button>
      </form>
      <hr />
      {#each posts as post (post.id)}
        <Post
          id={post.id}
          userId={user?.id}
          author={post.author}
          content={post.content}
          date={post.date}
          edited={post.edited}
          repost={post.repost}
          originalAuthor={post.author.original}
          tags={post.tags}
          likeCount={post.likeCount}
          liked={post.liked}
          on:update={fetchData}
        />
      {/each}
    </Paper>
  </div>
</AuthWrapper>

<style>
  #box {
    width: 900px;
    margin: 0 auto;
  }
  .user-card {
    margin: 5px 0;
    cursor: pointer;
  }
</style>
