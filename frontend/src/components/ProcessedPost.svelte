<script>
  export let content;
  export let tags;

  const processedContent = content.replace(/@(\w+)@/g, "@tag@");
</script>

{#each processedContent.split("@tag@") as section, index (index)}
  {section}
  {#if index < tags.length}
    {#if tags[index]?.id}
      <a href={`/profile/${tags[index].id}`}>@{tags[index].name}</a>
    {:else if tags[index]}
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
