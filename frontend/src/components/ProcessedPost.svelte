<script>
  export let processedPost;
  export let tags;
</script>

{#each processedPost.split("@tag@") as section, index (index)}
  {section}
  {#if index < tags.length}
    <a href={`/profile/${tags[index].id}`}>@{tags[index].name}</a>
  {/if}
{/each}

<style>
  a {
    text-decoration: none;
  }
  a:hover {
    text-decoration: underline;
  }
</style>
