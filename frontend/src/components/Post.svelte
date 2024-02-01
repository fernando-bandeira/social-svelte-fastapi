<script>
  import { Paper, Text, Checkbox, Button } from "@svelteuidev/core";
  import api from "../utils/api";
  import { onMount } from "svelte";

  export let id;
  export let userId;
  export let author;
  export let date;
  export let content;

  let liked = false;

  onMount(async () => {
    const res = await api.get(`/${userId}/likes/${id}/`);
    liked = res.data.like;
  });

  const handleLike = async () => {
    if (liked) {
      await api.delete(`/${userId}/likes/${id}/`);
      liked = false;
    } else {
      await api.post(`/${userId}/likes/${id}/`);
      liked = true;
    }
  };
</script>

<div id="container">
  <Paper>
    <div id="post-info">
      <div>
        <Text>{author.name} em {date}</Text>
        <Text>{content}</Text>
      </div>
      {#if userId === author.id}
        <div id="actions">
          <Button>Editar</Button>
          <Button color="red">Excluir</Button>
        </div>
      {/if}
    </div>
    <Checkbox checked={liked} on:input={handleLike} />
  </Paper>
</div>

<style>
  #container {
    margin: 15px 0 15px 0;
  }
  #post-info {
    display: flex;
    justify-content: space-between;
  }
  #actions {
    display: flex;
    justify-content: space-between;
    gap: 10px;
  }
</style>
