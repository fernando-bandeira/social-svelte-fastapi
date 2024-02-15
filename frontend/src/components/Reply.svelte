<script>
  import { Paper, Text, Menu } from "@svelteuidev/core";
  import { Trash } from "radix-icons-svelte";
  import api from "../utils/api";
  import { createEventDispatcher } from "svelte";

  export let id;
  export let author;
  export let content;
  export let date;
  export let userId;

  const dispatch = createEventDispatcher();

  const deleteReply = async () => {
    if (confirm("Deseja realmente excluir sua resposta?")) {
      await api.delete(`/replies/${id}/`);
      dispatch("delete");
    }
  };
</script>

<div id="container">
  <Paper>
    <div id="reply-section">
      <div>
        <Text>
          <a href={`/profile/${author.id}/`}>{author.name}</a> em {date}:
        </Text>
        <Text>{content}</Text>
      </div>
      {#if userId === author.id}
        <Menu>
          <Menu.Item color="red" icon={Trash} on:click={deleteReply}>
            Excluir
          </Menu.Item>
        </Menu>
      {/if}
    </div>
  </Paper>
</div>

<style>
  #container {
    padding: 10px 0px 10px 10px;
  }
  #reply-section {
    display: flex;
    justify-content: space-between;
  }
  a {
    text-decoration: none;
  }
  a:hover {
    text-decoration: underline;
  }
</style>
