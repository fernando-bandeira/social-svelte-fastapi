<script>
  import AuthWrapper from "../utils/AuthWrapper.svelte";
  import api from "../utils/api";
  import { userContext } from "../stores/userContext";
  import { Button, Textarea } from "@svelteuidev/core";
  import Header from "../components/Header.svelte";

  let user;
  userContext.subscribe((value) => {
    user = value;
  });

  let posts = [];
  const fetchData = async () => {
    if (user?.id) {
      const res = await api.get(`/posts/${user.id}/`);
      posts = res.data;
    }
  };
  $: user, fetchData();

  let post;
  const createPost = async () => {
    await api.post("/create-post/", {
      content: post,
      author: user.id,
    });
    post = "";
    const res = await api.get(`/posts/${user.id}/`);
    posts = res.data;
  };
</script>

<AuthWrapper>
  <Header userId={user?.id} />
  <form on:submit={createPost}>
    <Textarea bind:value={post} />
    <br />
    <Button type="submit">Postar</Button>
  </form>
  <hr />
  <ul>
    {#each posts as post}
      <li>{post.content}</li>
    {/each}
  </ul>
</AuthWrapper>
