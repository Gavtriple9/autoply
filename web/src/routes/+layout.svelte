<script>
  import favicon from "$lib/assets/favicon.svg";

  let { children } = $props();
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
</svelte:head>

<div class="app">
  <div class="container">{@render children()}</div>
</div>

<style>
  :global(:root) {
    color-scheme: light dark;
  }

  :global(html, body) {
    height: 100%;
  }

  :global(body) {
    margin: 0;
    background: Canvas;
    color: CanvasText;
    line-height: 1.5;
    text-rendering: geometricPrecision;
  }

  :global(a) {
    color: LinkText;
  }

  :global(*),
  :global(*::before),
  :global(*::after) {
    box-sizing: border-box;
  }

  .app {
    min-height: 100%;
    padding: 24px 16px 56px;
    background: Canvas;
  }

  .container {
    max-width: 980px;
    margin: 0 auto;
  }
</style>
