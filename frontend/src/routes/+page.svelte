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
  } from "@svelteuidev/core";
  import Header from "../components/Header.svelte";
  import Post from "../components/Post.svelte";

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
  let processedPost;
  const createPost = async () => {
    await api.post("/create-post/", {
      content: post,
      author: user.id,
      date: new Date().toLocaleString("en-GB"),
      repost: false,
      reference: null,
    });
    post = "";
    fetchData();
  };

  const handleTagUser = () => {
    if (
      (post?.endsWith("@") &&
        !"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@".includes(
          post[post.length - 2]?.toUpperCase(),
        )) ||
      post === "@"
    ) {
      tagUsersModalOpened = true;
    }
  };

  $: post, handleTagUser();
</script>

<AuthWrapper>
  <Header userId={user?.id} />
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
        <Paper>
          <Text
            on:click={() => {
              post = post + `${user.id}@`;
              tagUsersModalOpened = false;
            }}
          >
            {user.name}
          </Text>
        </Paper>
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
          reference={post.reference}
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
</style>
