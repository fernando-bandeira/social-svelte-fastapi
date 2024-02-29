<script>
  import {
    Button,
    Collapse,
    Textarea,
    Text,
    Center,
    Loader,
  } from "@svelteuidev/core";
  import api from "../utils/api";
  import Reply from "./Reply.svelte";
  import { createEventDispatcher } from "svelte";

  export let id;
  export let userId;
  export let showReplies;

  const dispatch = createEventDispatcher();

  let replies = [];
  let loading = false;

  let reply;

  const fetchReplies = async () => {
    if (replies.length === 0 && showReplies) {
      loading = true;
      const res = await api.get(`/replies/${id}/`);
      replies = res.data;
      loading = false;
    }
  };
  $: showReplies, fetchReplies();

  const postReply = async () => {
    await api.post(`/replies/`, {
      author: userId,
      content: reply,
      date: new Date().toLocaleString("en-GB"),
      post: id,
    });
    reply = "";
    fetchReplies();
  };
</script>

<Collapse open={showReplies}>
  {#if replies.length > 0 && !loading}
    {#each replies as reply (reply.id)}
      <Reply {...reply} {userId} on:delete={fetchReplies} />
    {/each}
  {:else if loading}
    <Loader />
  {:else}
    <Center>
      <Text>Não há respostas.</Text>
    </Center>
  {/if}
  <div id="reply-section">
    <Textarea autofocus bind:value={reply} />
    <div id="reply-buttons">
      <Button
        color="red"
        on:click={() => {
          dispatch("close");
        }}
      >
        Cancelar
      </Button>
      <Button on:click={postReply}>Publicar</Button>
    </div>
  </div>
</Collapse>

<style>
  div {
    display: flex;
    gap: 10px;
  }
  #reply-section {
    padding-top: 10px;
    flex-direction: column;
  }
  #reply-buttons {
    justify-content: flex-end;
  }
</style>
