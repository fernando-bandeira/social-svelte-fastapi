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
  import { Trash, Pencil1, Update } from "radix-icons-svelte";
  import ProcessedPost from "./ProcessedPost.svelte";

  const dispatch = createEventDispatcher();

  export let id;
  export let userId;
  export let author;
  export let date;
  export let content;
  export let edited;
  export let repost;
  export let reference;

  let liked = false;
  let likeCount;
  let loadingLikeFetch = true;

  let originalPostData;
  let loadingOriginalPostFetch = true;

  let editing = false;
  let editedContent = content;

  let processedPost = content;
  let tags = [];
  let loadingPostProcessing = true;

  const fetchLike = async () => {
    const resLiked = await api.get(`/${userId}/likes/${id}/`);
    liked = resLiked.data.like;
    const resCount = await api.get(`/likes/${id}/`);
    likeCount = resCount.data.count;
    loadingLikeFetch = false;
  };

  const fetchOriginalPost = async () => {
    if (repost) {
      const res = await api.get(`/post/${reference}/`);
      originalPostData = res.data;
    }
    loadingOriginalPostFetch = false;
  };

  const processPostTags = async () => {
    let target;
    const regex = /@(\w+)@/g;
    if (repost) {
      target = originalPostData.content;
    } else {
      target = content;
    }
    const matches = target.match(regex);
    if (matches) {
      tags = await Promise.all(
        matches.map(async (match) => {
          const word = match.substring(1, match.length - 1);
          const res = await api.get(`/user/${word}/`);
          return { id: res.data.id, name: res.data.name };
        }),
      );
      processedPost = target.replace(regex, () => {
        return "@tag@";
      });
    } else {
      processedPost = target;
    }
    loadingPostProcessing = false;
  };

  onMount(async () => {
    fetchLike();
    await fetchOriginalPost();
    processPostTags();
  });

  const handleLike = async () => {
    if (liked) {
      await api.delete(`/${userId}/likes/${id}/`);
    } else {
      await api.post(`/${userId}/likes/${id}/`);
    }
    fetchLike();
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

  const handleRepost = async () => {
    await api.post("/create-post/", {
      author: userId,
      content: "",
      date: new Date().toLocaleString("en-GB"),
      repost: true,
      reference: id,
    });
    dispatch("update");
  };
</script>

<div id="container">
  <Paper>
    <div id="post-info">
      <div>
        {#if repost && !loadingOriginalPostFetch}
          <div id="repost-title">
            <Update />
            <Text>
              <a href={`/profile/${author.id}/`}>{author.name}</a> repostou de
              <a href={`/profile/${originalPostData?.author?.id}/`}>
                {originalPostData?.author?.name}
              </a>
              em {date}
            </Text>
          </div>
          <hr />
        {:else if loadingOriginalPostFetch}
          <Skeleton height={20} radius="xl" />
        {:else}
          <Text>
            <a href={`/profile/${author.id}/`}>{author.name}</a> em {date}
          </Text>
        {/if}
        {#if edited}
          (Editado)
        {/if}
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
        {:else if !loadingPostProcessing}
          <Text><ProcessedPost {tags} {processedPost} /></Text>
        {:else}
          <Skeleton height={20} radius="xl" />
        {/if}
        <br />
      </div>
      {#if userId === author.id}
        <div id="actions">
          {#if !repost}
            <Button on:click={() => (editing = true)} disabled={editing}>
              <Pencil1 slot="leftIcon" />
              Editar
            </Button>
          {/if}
          <Button color="red" on:click={deletePost}>
            <Trash slot="leftIcon" />
            Excluir
          </Button>
        </div>
      {:else if !repost}
        <Button on:click={handleRepost}>Repostar</Button>
      {/if}
    </div>
    {#if loadingLikeFetch}
      <Skeleton circle height={25} />
    {:else}
      <div id="like-section">
        <Checkbox checked={liked} on:input={handleLike} />
        <Text>{likeCount}</Text>
      </div>
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
  #repost-title {
    display: flex;
    align-items: center;
    gap: 5px;
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
  #like-section {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    gap: 10px;
  }
  a {
    text-decoration: none;
  }
  a:hover {
    text-decoration: underline;
  }
</style>
