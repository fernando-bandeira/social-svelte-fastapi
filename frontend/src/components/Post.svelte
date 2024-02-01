<script>
  import { Paper, Text, Checkbox } from "@svelteuidev/core";
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

<Paper>
  <Text>{author} em {date}</Text>
  <Text>{content}</Text>
  <Checkbox checked={liked} on:input={handleLike} />
</Paper>
