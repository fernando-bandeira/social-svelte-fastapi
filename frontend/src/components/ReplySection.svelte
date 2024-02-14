<script>
  import { Button, Collapse, Textarea, Text, Center } from "@svelteuidev/core";
  import { ChatBubble } from "radix-icons-svelte";
  import api from "../utils/api";
  import Reply from "./Reply.svelte";

  export let id;
  export let userId;

  let replies = [];
  let showReplies = false;
  let loading = false;

  let showReplyInput;

  let reply;

  const fetchReplies = async () => {
    loading = true;
    const res = await api.get(`/replies/${id}/`);
    replies = res.data;
    loading = false;
  };

  const handleCollapse = async () => {
    if (!showReplies) {
      if (replies.length === 0) {
        await fetchReplies();
      }
      showReplies = true;
    } else {
      showReplies = false;
    }
  };

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
  {#if replies.length > 0}
    {#each replies as reply (reply.id)}
      <Reply {...reply} />
    {/each}
  {:else}
    <Center>
      <Text>Não há respostas.</Text>
    </Center>
  {/if}
</Collapse>
<div>
  <Button on:click={handleCollapse} {loading}>
    {showReplies ? "Ocultar" : "Exibir"} respostas
  </Button>
  {#if !showReplyInput}
    <Button
      on:click={() => (showReplyInput = true)}
      variant="outline"
    >
      <ChatBubble slot="leftIcon" />
      Responder
    </Button>
  {/if}
</div>
<Collapse open={showReplyInput}>
  <div id="reply-section">
    <Textarea autofocus bind:value={reply} />
    <div id="reply-buttons">
      <Button color="red" on:click={() => (showReplyInput = false)}>
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
