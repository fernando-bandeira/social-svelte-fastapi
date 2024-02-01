<script>
  import { Paper, Text, Checkbox, Button, Textarea } from "@svelteuidev/core";
  import api from "../utils/api";
  import { onMount } from "svelte";

  export let id;
  export let userId;
  export let author;
  export let date;
  export let content;

  let liked = false;
  let editing = false;
  let editedContent = content;

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

  const updatePost = async () => {
    await api.put(`/edit-post/${id}/`, {
      content: editedContent,
      author: userId,
      date: date,
    });
    const res = await api.get(`/post/${id}/`);
    content = res.data.content;
  };
</script>

<div id="container">
  <Paper>
    <div id="post-info">
      <div>
        <Text>
          <a href={`/profile/${author.id}/`}>{author.name}</a> em {date}
        </Text>
        <br />
        {#if editing}
          <div id="edit-section">
            <Textarea bind:value={editedContent} autofocus />
            <div id="edit-actions">
              <Button
                color="red"
                on:click={() => {
                  editing = false;
                  editedContent = content;
                }}
              >
                Cancelar
              </Button>
              <Button
                disabled={editedContent === content}
                on:click={() => {
                  editing = false;
                  updatePost();
                }}
              >
                Salvar
              </Button>
            </div>
          </div>
        {:else}
          <Text>{content}</Text>
        {/if}
        <br />
      </div>
      {#if userId === author.id}
        <div id="actions">
          <Button on:click={() => (editing = true)} disabled={editing}>
            Editar
          </Button>
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
  #edit-section {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  #edit-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }
  a {
    text-decoration: none;
  }
  a:hover {
    text-decoration: underline;
  }
</style>
