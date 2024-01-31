<script>
  import { verifyAuth } from "./verifyAuth";
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";

  let loading = true;
  let authenticated = false;

  onMount(async () => {
    try {
      if (await verifyAuth()) {
        authenticated = true;
      }
    } finally {
      loading = false;
      if (authenticated) {
        goto("/");
      }
    }
  });
</script>

{#if !loading && !authenticated}
  <slot />
{/if}
