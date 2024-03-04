<script>
  import {
    Paper,
    Text,
    Button,
    Textarea,
    Menu,
    ActionIcon,
    Alert,
  } from "@svelteuidev/core";
  import api from "../utils/api";
  import { createEventDispatcher } from "svelte";
  import { focus } from "@svelteuidev/composables";
  import {
    Trash,
    Pencil1,
    Update,
    Check,
    Cross2,
    ChatBubble,
  } from "radix-icons-svelte";
  import ProcessedPost from "./ProcessedPost.svelte";
  import ReplySection from "./ReplySection.svelte";
  import { Heart, HeartFilled } from "radix-icons-svelte";

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
  export let repostCount;
  export let replyCount;

  let showReplies = false;

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
  };

  const fetchReplies = async () => {
    const red = await api.get(`/replies/count/${id}/`);
    replyCount = red.data.count;
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
      editedContent = editedContent.replace(/@([^@]+)@/g, (_, tagName) => {
        const id = tags.find((tag) => tag.name == tagName).id;
        return "@" + id + "@";
      });
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
              on:click={() => {
                editedContent = editedContent.replace(
                  /@([^@]+)@/g,
                  (_, tagId) => {
                    const name = tags.find((tag) => tag.id == tagId)?.name;
                    return "@" + name + "@";
                  },
                );
                editing = true;
              }}
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
      {/if}
    </div>
    <hr />
    <div id="action-group">
      <div class="action">
        <ActionIcon variant="hover" color="#228BE625" on:click={handleLike}>
          {#if liked}
            <HeartFilled color="#228BE6" size={25} />
          {:else}
            <Heart color="#228BE6" size={25} />
          {/if}
        </ActionIcon>
        <Text>{likeCount}</Text>
      </div>
      {#if !repost}
        <div class="action">
          <ActionIcon variant="hover" color="#228BE625" on:click={handleRepost}>
            <Update color="#228BE6" size={20} />
          </ActionIcon>
          <Text>{repostCount}</Text>
        </div>
      {/if}
      <div class="action">
        <ActionIcon
          variant="hover"
          color="#228BE625"
          on:click={() => (showReplies = !showReplies)}
        >
          <ChatBubble color="#228BE6" size={20} />
        </ActionIcon>
        <Text>{replyCount}</Text>
      </div>
    </div>
    <ReplySection
      {id}
      {userId}
      {showReplies}
      {replyCount}
      on:close={() => (showReplies = false)}
      on:newReply={fetchReplies}
      on:replyDeleted={fetchReplies}
    />
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
  #action-group {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    gap: 25px;
  }
  .action {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 3px;
  }
  a {
    text-decoration: none;
  }
  a:hover {
    text-decoration: underline;
  }
</style>
