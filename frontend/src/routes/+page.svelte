<script>
  import AuthWrapper from "../utils/AuthWrapper.svelte";
  import api from "../utils/api";
  import { userContext } from "../stores/userContext";
  import { Button, Textarea, Paper } from "@svelteuidev/core";
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

  let post;
  const createPost = async () => {
    await api.post("/create-post/", {
      content: post,
      author: user.id,
      date: new Date().toLocaleString("en-GB"),
    });
    post = "";
    fetchData();
  };
</script>

<AuthWrapper>
  <Header userId={user?.id} />
  <div id="box">
    <Paper>
      <form on:submit={createPost}>
        <Textarea bind:value={post} />
        <br />
        <Button type="submit">Postar</Button>
      </form>
      <hr />
      {#each posts as post}
        <Post
          id={post.id}
          userId={user?.id}
          author={post.author}
          content={post.content}
          date={post.date}
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
