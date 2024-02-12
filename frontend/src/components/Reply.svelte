<script>
  import { Paper, Text } from "@svelteuidev/core";
  export let author;
  export let content;
  export let date;
</script>

<div>
  <Paper>
    <Text><a href={`/profile/${author.id}/`}>{author.name}</a> em {date}:</Text>
    <Text>{content}</Text>
  </Paper>
</div>

<style>
  div {
    padding: 10px 0px 10px 10px;
  }
  a {
    text-decoration: none;
  }
  a:hover {
    text-decoration: underline;
  }
</style>
