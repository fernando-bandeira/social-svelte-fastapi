<script>
  import {
    Paper,
    Text,
    Checkbox,
    Button,
    Textarea,
    Skeleton,
  } from "@svelteuidev/core";
  import api from "../utils/api";
  import { onMount } from "svelte";
  import { createEventDispatcher } from "svelte";
  import { focus } from "@svelteuidev/composables";
  import { Trash, Pencil1 } from "radix-icons-svelte";

  const dispatch = createEventDispatcher();

  export let id;
  export let userId;
  export let author;
  export let date;
  export let content;
  export let edited;

  let liked = false;
  let loadingLikeFetch = true;
  let editing = false;
  let editedContent = content;

  onMount(async () => {
    const res = await api.get(`/${userId}/likes/${id}/`);
    liked = res.data.like;
    loadingLikeFetch = false;
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
    dispatch("update");
  };

  const deletePost = async () => {
    if (window.confirm("Deseja realmente excluir este post?")) {
      await api.delete(`/delete-post/${id}/`);
      dispatch("update");
    }
  };
</script>

<div id="container">
  <Paper>
    <div id="post-info">
      <div>
        <Text>
          <a href={`/profile/${author.id}/`}>{author.name}</a> em {date}
          {#if edited}
            (Editado)
          {/if}
        </Text>
        <br />
        {#if editing}
          <div id="edit-section">
            <Textarea bind:value={editedContent} use={[[focus]]} />
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
            <Pencil1 slot="leftIcon" />
            Editar
          </Button>
          <Button color="red" on:click={deletePost}>
            <Trash slot="leftIcon" />
            Excluir
          </Button>
        </div>
      {/if}
    </div>
    {#if loadingLikeFetch}
      <Skeleton circle height={25} />
    {:else}
      <Checkbox checked={liked} on:input={handleLike} />
    {/if}
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
