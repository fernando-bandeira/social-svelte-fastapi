<script>
  import {
    Paper,
    Text,
    Checkbox,
    Button,
    Textarea,
    Menu,
    ActionIcon,
    Alert,
  } from "@svelteuidev/core";
  import api from "../utils/api";
  import { createEventDispatcher } from "svelte";
  import { focus } from "@svelteuidev/composables";
  import { Trash, Pencil1, Update, Check, Cross2 } from "radix-icons-svelte";
  import ProcessedPost from "./ProcessedPost.svelte";
  import ReplySection from "./ReplySection.svelte";

  const dispatch = createEventDispatcher();

  export let id;
  export let userId;
  export let author;
  export let date;
  export let content;
  export let edited;
  export let repost;
  export let tags;
  export let likeCount;
  export let liked;

  let showSuccessMessage = false;
  let showErrorMessage = false;
  let alertMessage;

  const handleAlert = (isError, msg) => {
    alertMessage = msg;
    showErrorMessage = isError;
    showSuccessMessage = !isError;
    setTimeout(() => {
      showErrorMessage = false;
      showSuccessMessage = false;
    }, 5000);
  };

  let editing = false;
  let editedContent = content;

  const fetchLike = async () => {
    const resLiked = await api.get(`/likes/${userId}/${id}/`);
    liked = resLiked.data.like;
    const resCount = await api.get(`/likes/post/${id}/`);
    likeCount = resCount.data.count;
    loadingLikeFetch = false;
  };

  const handleLike = async () => {
    if (liked) {
      await api.delete(`/likes/${userId}/${id}/`);
    } else {
      await api.post(`/likes/${userId}/${id}/`);
    }
    fetchLike();
  };

  const updatePost = async () => {
    try {
      await api.put(`/posts/${id}/`, {
        content: editedContent,
        author: userId,
        date: date,
        repost: false,
        reference: null,
      });
      dispatch("update");
      handleAlert(false, "Publicação editada com sucesso!");
    } catch (err) {
      handleAlert(true, "Não foi possível editar sua publicação.");
    }
  };

  const deletePost = async () => {
    if (window.confirm("Deseja realmente excluir este post?")) {
      try {
        await api.delete(`/posts/${id}/`);
        dispatch("update");
        handleAlert(false, "Publicação excluída com sucesso!");
      } catch (err) {
        handleAlert(true, "Não foi possível excluir sua publicação.");
      }
    }
  };

  const handleRepost = async () => {
    await api.post("/posts/", {
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
  <div style="position: fixed; bottom: 40px; right: 20px">
    {#if showSuccessMessage || showErrorMessage}
      <Alert
        color={showSuccessMessage ? "teal" : "red"}
        icon={showSuccessMessage ? Check : Cross2}
        withCloseButton
        on:close={() => {
          showSuccessMessage = false;
          showErrorMessage = false;
        }}
      >
        {alertMessage}
      </Alert>
    {/if}
  </div>
  <Paper>
    <div id="post-info">
      <div style="width: 100%">
        {#if repost}
          <div id="repost-title">
            <Update />
            <Text>
              <a href={`/profile/${author.id}/`}>{author.name}</a> repostou de
              <a href={`/profile/${author.original.id}/`}>
                {author.original.name}
              </a>
              em {date}
            </Text>
          </div>
        {:else}
          <Text>
            <a href={`/profile/${author.id}/`}>{author.name}</a> em {date}
            {#if edited}
              (Editado)
            {/if}
          </Text>
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
        {:else}
          {#key content}
            <Text><ProcessedPost {tags} {content} /></Text>
          {/key}
        {/if}
        <br />
      </div>
      {#if userId === author.id}
        <Menu>
          {#if !repost}
            <Menu.Item
              on:click={() => (editing = true)}
              disabled={editing}
              icon={Pencil1}
            >
              Editar
            </Menu.Item>
          {/if}
          <Menu.Item color="red" icon={Trash} on:click={deletePost}>
            Excluir
          </Menu.Item>
        </Menu>
      {:else if !repost}
        <ActionIcon on:click={handleRepost}>
          <Update />
        </ActionIcon>
      {/if}
    </div>
    <div id="like-section">
      <Checkbox checked={liked} on:input={handleLike} />
      <Text>{likeCount}</Text>
    </div>
    <hr />
    <ReplySection {id} {userId} />
  </Paper>
</div>

<style>
  #container {
    margin: 15px 0 15px 0;
  }
  #post-info {
    display: flex;
    justify-content: space-between;
    gap: 15px;
  }
  #repost-title {
    display: flex;
    align-items: center;
    gap: 5px;
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
