<script>
  export let processedPost;
  export let tags;
</script>

{#each processedPost.split("@tag@") as section, index (index)}
  {section}
  {#if index < tags.length}
    {#if tags[index]?.id}
      <a href={`/profile/${tags[index].id}`}>@{tags[index].name}</a>
    {:else}
      @{tags[index]}@
    {/if}
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
