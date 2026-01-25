<script>
  let { data } = $props();
</script>

<main class="page">
  <header class="hero">
    <h1 class="title">Dinners</h1>
    <p class="subtitle">
      Meals and shopping list from <code>dinners.json</code>.
    </p>
  </header>

  {#if data?.dinners?.meals?.length}
    <section class="section">
      <div class="sectionHeader">
        <h2>Meals</h2>
        <p class="meta">{data.dinners.meals.length} total</p>
      </div>

      <div class="grid">
        {#each data.dinners.meals as meal}
          <article class="card">
            <div class="cardHeader">
              <h3 class="cardTitle">{meal.dish_name}</h3>
              <span class="chip">{meal.total_time} min</span>
            </div>
            <p class="cardDesc">{meal.description}</p>

            <div class="twoCol">
              <section class="subsection">
                <h4>Ingredients</h4>
                <ul class="list">
                  {#each meal.ingredients as ingredient}
                    <li>{ingredient}</li>
                  {/each}
                </ul>
              </section>

              <section class="subsection">
                <h4>Recipe</h4>
                <ol class="steps">
                  {#each meal.recipe as step}
                    <li>{step}</li>
                  {/each}
                </ol>
              </section>
            </div>
          </article>
        {/each}
      </div>
    </section>
  {/if}

  {#if data?.dinners?.ingredient_list?.length}
    <section class="section">
      <div class="sectionHeader">
        <h2>Ingredient list</h2>
        <p class="meta">{data.dinners.ingredient_list.length} items</p>
      </div>
      <div class="tableWrap" role="region" aria-label="Ingredient list">
        <table class="table">
          <thead>
            <tr>
              <th>Ingredient</th>
              <th>Quantity</th>
              <th>In deals</th>
            </tr>
          </thead>
          <tbody>
            {#each data.dinners.ingredient_list as item}
              <tr>
                <td>{item.ingredient}</td>
                <td class="nowrap">{item.quantity}</td>
                <td>
                  <span
                    class="pill"
                    data-state={item.in_deals === "yes" ? "yes" : "no"}
                  >
                    {item.in_deals}
                  </span>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </section>
  {/if}
</main>

<style>
  .page {
    display: grid;
    gap: 20px;
  }

  .hero {
    padding: 18px 16px;
    border: 1px solid color-mix(in oklab, CanvasText 14%, Canvas);
    border-radius: 14px;
    background: color-mix(in oklab, Canvas 92%, CanvasText);
  }

  .title {
    margin: 0;
    font-size: clamp(1.6rem, 2.2vw + 1rem, 2.4rem);
    letter-spacing: -0.02em;
  }

  .subtitle {
    margin: 6px 0 0;
    color: color-mix(in oklab, CanvasText 70%, Canvas);
  }

  .subtitle code {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
      "Liberation Mono", "Courier New", monospace;
    font-size: 0.95em;
    padding: 0.1em 0.35em;
    border: 1px solid color-mix(in oklab, CanvasText 14%, Canvas);
    border-radius: 8px;
    background: color-mix(in oklab, Canvas 88%, CanvasText);
  }

  .section {
    display: grid;
    gap: 12px;
  }

  .sectionHeader {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 12px;
  }

  .sectionHeader h2 {
    margin: 0;
    font-size: 1.25rem;
  }

  .meta {
    margin: 0;
    color: color-mix(in oklab, CanvasText 70%, Canvas);
    font-size: 0.95rem;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 14px;
  }

  @media (min-width: 720px) {
    .grid {
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
    }
  }

  .card {
    container-type: inline-size;
    border: 1px solid color-mix(in oklab, CanvasText 14%, Canvas);
    border-radius: 14px;
    padding: 16px;
    background: color-mix(in oklab, Canvas 94%, CanvasText);
  }

  .cardHeader {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
  }

  .cardTitle {
    margin: 0;
    font-size: 1.05rem;
    letter-spacing: -0.01em;
  }

  .chip {
    flex: none;
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid color-mix(in oklab, CanvasText 14%, Canvas);
    background: Canvas;
    font-size: 0.9rem;
    white-space: nowrap;
  }

  .cardDesc {
    margin: 10px 0 0;
    color: color-mix(in oklab, CanvasText 80%, Canvas);
  }

  .twoCol {
    margin-top: 14px;
    display: grid;
    grid-template-columns: 1fr;
    gap: 18px;
  }

  @container (min-width: 720px) {
    .twoCol {
      grid-template-columns: 1fr 1fr;
    }
  }

  .subsection h4 {
    margin: 0 0 8px;
    font-size: 0.95rem;
    color: color-mix(in oklab, CanvasText 80%, Canvas);
  }

  .list,
  .steps {
    margin: 0;
    padding-left: 1.2rem;
    display: grid;
    gap: 6px;
  }

  .tableWrap {
    border: 1px solid color-mix(in oklab, CanvasText 14%, Canvas);
    border-radius: 14px;
    overflow: auto;
    background: color-mix(in oklab, Canvas 94%, CanvasText);
  }

  .table {
    width: 100%;
    border-collapse: collapse;
    min-width: 0;
  }

  .table th,
  .table td {
    padding: 12px 14px;
    border-bottom: 1px solid color-mix(in oklab, CanvasText 10%, Canvas);
    text-align: left;
    vertical-align: top;
  }

  .table thead th {
    font-size: 0.9rem;
    color: color-mix(in oklab, CanvasText 75%, Canvas);
    background: color-mix(in oklab, Canvas 88%, CanvasText);
    position: sticky;
    top: 0;
  }

  .table tbody tr:last-child td {
    border-bottom: none;
  }

  .nowrap {
    white-space: nowrap;
  }

  @media (max-width: 520px) {
    .hero {
      padding: 16px 14px;
    }

    .sectionHeader {
      flex-direction: column;
      align-items: flex-start;
      gap: 4px;
    }

    .table th,
    .table td {
      padding: 10px 12px;
    }

    .table td:first-child {
      word-break: break-word;
    }
  }

  .pill {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid color-mix(in oklab, CanvasText 14%, Canvas);
    background: Canvas;
    font-size: 0.9rem;
    white-space: nowrap;
  }

  .pill[data-state="yes"] {
    font-weight: 600;
  }
</style>
