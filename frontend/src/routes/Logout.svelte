<script>
  import api from "../utils/api";
  import { goto } from "$app/navigation";
  import { Button } from "@svelteuidev/core";

  const logout = async () => {
    await api.post("/logout/", {
      access: localStorage.getItem("access"),
      refresh: localStorage.getItem("refresh"),
    });
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    goto("/login");
  };
</script>

<Button color="red" on:click={logout}>Sair</Button>
