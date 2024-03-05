<script>
  import {
    Button,
    Collapse,
    Textarea,
    Text,
    Center,
    Loader,
  } from "@svelteuidev/core";
  import { focus } from "@svelteuidev/composables";
  import api from "../utils/api";
  import Reply from "./Reply.svelte";
  import { createEventDispatcher } from "svelte";

  export let id;
  export let userId;
  export let showReplies;
  export let replyCount;

  const dispatch = createEventDispatcher();

  let replies = [];
  let loading = false;

  let reply;
  let replyPage = 1;

  const fetchReplies = async (accumulate = false) => {
    loading = true;
    if (!accumulate) {
      replies = [];
      replyPage = 1;
    }
    const res = await api.get(`/replies/${id}/?page=${replyPage}`);
    replies = res.data.concat(replies);
    loading = false;
  };

  const handleReplyFetch = () => {
    if (replies.length === 0 && showReplies) {
      fetchReplies();
    }
  };
  $: showReplies, handleReplyFetch();

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
  {#if replies.length < replyCount && !loading}
    <Center>
      <Button
        variant="subtle"
        on:click={() => {
          replyPage++;
          fetchReplies(true);
        }}
      >
        Exibir respostas mais antigas
      </Button>
    </Center>
  {/if}
  {#if replies.length > 0 && !loading}
    {#each replies as reply (reply.id)}
      <Reply
        {...reply}
        {userId}
        on:delete={() => {
          fetchReplies();
          dispatch("replyDeleted");
        }}
      />
    {/each}
  {:else if loading}
    <Center>
      <Loader />
    </Center>
  {:else}
    <Center>
      <Text>Não há respostas.</Text>
    </Center>
  {/if}
  <div id="reply-section">
    <Textarea bind:value={reply} use={[[focus]]} />
    <div id="reply-buttons">
      <Button
        color="red"
        on:click={() => {
          dispatch("close");
        }}
      >
        Cancelar
      </Button>
      <Button
        on:click={() => {
          postReply();
          dispatch("newReply");
        }}
      >
        Publicar
      </Button>
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
