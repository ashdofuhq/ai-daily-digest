/**
 * AI Daily Digest — Frontend App
 * Vanilla JS, zero dependencies.
 */

// ---- State ----
const state = {
  allItems: [],
  filteredItems: [],
  activeSources: new Set(),
  activeTags: new Set(),
  searchQuery: "",
  displayCount: 30,
  loadIncrement: 30,
  date: "",
  theme: "dark",
};

// ---- DOM refs ----
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const dom = {
  cardGrid: $("#cardGrid"),
  searchInput: $("#searchInput"),
  searchClear: $("#searchClear"),
  sourceFilters: $("#sourceFilters"),
  tagFilters: $("#tagFilters"),
  statDate: $("#statDate"),
  statCount: $("#statCount"),
  loadMore: $("#loadMore"),
  loadMoreBtn: $("#loadMoreBtn"),
  loading: $("#loading"),
  emptyState: $("#emptyState"),
  themeToggle: $("#themeToggle"),
};

// ---- Data Fetching ----
async function loadData() {
  dom.loading.classList.remove("hidden");
  dom.cardGrid.innerHTML = "";
  dom.emptyState.classList.add("hidden");

  try {
    const resp = await fetch("data/latest.json");
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const json = await resp.json();
    state.allItems = json.items || [];
    state.date = json.date || "";
  } catch {
    // If latest.json not available, try archive
    try {
      const resp = await fetch("data/archive.json");
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const archive = await resp.json();
      const dates = Object.keys(archive).sort().reverse();
      if (dates.length > 0) {
        const latest = archive[dates[0]];
        state.allItems = latest.items || [];
        state.date = latest.date || dates[0];
      }
    } catch {
      state.allItems = [];
      state.date = "";
    }
  }

  // Reset filters
  state.displayCount = 30;
  state.searchQuery = "";
  state.activeSources.clear();
  state.activeTags.clear();
  dom.searchInput.value = "";
  dom.searchClear.classList.add("hidden");

  dom.loading.classList.add("hidden");
  render();
}

// ---- Rendering ----
function createCard(item) {
  const card = document.createElement("article");
  card.className = "card";
  card.addEventListener("click", () => window.open(item.url, "_blank", "noopener"));

  // Hot score level
  let hotClass = "";
  if (item.hot_score >= 80) hotClass = "";
  else if (item.hot_score >= 50) hotClass = "medium";
  else hotClass = "low";

  // Source badge
  const sourceClass = `source-${item.source}`;

  // Tags
  const tagsHtml = (item.tags || []).slice(0, 4).map((t) =>
    `<span class="card-tag">${escapeHtml(t)}</span>`
  ).join("");

  // Stars
  const starsHtml = item.stars > 0
    ? `<span class="card-stars">
         <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 22 12 18.56 5.82 22 7 14.14l-5-4.87 6.91-1.01L12 2z"/></svg>
         ${formatNumber(item.stars)}
       </span>`
    : "";

  // Author
  const authorHtml = item.authors
    ? `<span class="card-author">${escapeHtml(item.authors)}</span>`
    : "";

  card.innerHTML = `
    <div class="card-meta">
      <span class="card-source ${sourceClass}">${escapeHtml(item.source_label)}</span>
      ${item.hot_score > 0 ? `<span class="card-hot ${hotClass}">${item.hot_score}°</span>` : ""}
    </div>
    <h3 class="card-title">${escapeHtml(item.title)}</h3>
    ${item.summary ? `<p class="card-summary">${escapeHtml(item.summary)}</p>` : ""}
    <div class="card-footer">
      <div class="card-tags">${tagsHtml}</div>
      <div style="display:flex;align-items:center;gap:8px;">
        ${authorHtml}
        ${starsHtml}
      </div>
    </div>
  `;

  return card;
}

function render() {
  dom.cardGrid.innerHTML = "";
  dom.emptyState.classList.add("hidden");

  // Compute filtered items
  let items = [...state.allItems];

  // Source filter
  if (state.activeSources.size > 0) {
    items = items.filter((i) => state.activeSources.has(i.source));
  }

  // Tag filter
  if (state.activeTags.size > 0) {
    items = items.filter((i) =>
      (i.tags || []).some((t) => state.activeTags.has(t))
    );
  }

  // Search filter
  if (state.searchQuery.trim()) {
    const q = state.searchQuery.trim().toLowerCase();
    items = items.filter(
      (i) =>
        i.title.toLowerCase().includes(q) ||
        (i.summary || "").toLowerCase().includes(q) ||
        (i.authors || "").toLowerCase().includes(q) ||
        (i.tags || []).some((t) => t.toLowerCase().includes(q))
    );
  }

  state.filteredItems = items;

  // Stats
  const d = state.date ? new Date(state.date + "T00:00:00") : new Date();
  const dateStr = d.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric",
    weekday: "long",
  });
  dom.statDate.textContent = dateStr;
  dom.statCount.textContent = `共 ${items.length} 篇`;

  // Empty state
  if (items.length === 0) {
    dom.emptyState.classList.remove("hidden");
    dom.loadMore.classList.add("hidden");
    updateFilters();
    return;
  }

  // Render visible cards
  const visible = items.slice(0, state.displayCount);
  const fragment = document.createDocumentFragment();
  visible.forEach((item) => fragment.appendChild(createCard(item)));
  dom.cardGrid.appendChild(fragment);

  // Load more
  if (state.displayCount >= items.length) {
    dom.loadMore.classList.add("hidden");
  } else {
    dom.loadMore.classList.remove("hidden");
  }

  updateFilters();
}

// ---- Filters ----
function sourceLabel(source) {
  const map = {
    arxiv: "Arxiv",
    github: "GitHub",
    huggingface: "HuggingFace",
    paperswithcode: "PapersWithCode",
    hackernews: "Hacker News",
  };
  return map[source] || source;
}

function updateFilters() {
  // Source filters
  const sourceCounts = {};
  state.allItems.forEach((i) => {
    sourceCounts[i.source] = (sourceCounts[i.source] || 0) + 1;
  });

  dom.sourceFilters.innerHTML = Object.entries(sourceCounts)
    .map(
      ([s, c]) =>
        `<span class="filter-chip${state.activeSources.has(s) ? " active" : ""}" data-source="${s}">
          <span class="dot dot-${s}"></span>${sourceLabel(s)} (${c})
        </span>`
    )
    .join("");

  // Tag filters — collect top tags from currently source-filtered items
  const baseItems =
    state.activeSources.size > 0
      ? state.allItems.filter((i) => state.activeSources.has(i.source))
      : state.allItems;

  const tagCounts = {};
  baseItems.forEach((i) => {
    (i.tags || []).forEach((t) => {
      tagCounts[t] = (tagCounts[t] || 0) + 1;
    });
  });

  const topTags = Object.entries(tagCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 15);

  dom.tagFilters.innerHTML = topTags
    .map(
      ([t, c]) =>
        `<span class="filter-chip${state.activeTags.has(t) ? " active" : ""}" data-tag="${t}">
          ${t} (${c})
        </span>`
    )
    .join("");
}

// ---- Event Handlers ----
function toggleSource(source) {
  if (state.activeSources.has(source)) {
    state.activeSources.delete(source);
  } else {
    state.activeSources.add(source);
  }
  state.displayCount = 30;
  render();
}

function toggleTag(tag) {
  if (state.activeTags.has(tag)) {
    state.activeTags.delete(tag);
  } else {
    state.activeTags.add(tag);
  }
  state.displayCount = 30;
  render();
}

function onSearchInput(value) {
  state.searchQuery = value;
  state.displayCount = 30;
  if (value) {
    dom.searchClear.classList.remove("hidden");
  } else {
    dom.searchClear.classList.add("hidden");
  }
  render();
}

function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  html.setAttribute("data-theme", next);
  state.theme = next;
  try {
    localStorage.setItem("ai-digest-theme", next);
  } catch {}
}

function loadTheme() {
  let theme = "dark";
  try {
    theme = localStorage.getItem("ai-digest-theme") || "dark";
  } catch {}
  document.documentElement.setAttribute("data-theme", theme);
  state.theme = theme;
}

// ---- Event Delegation ----
dom.sourceFilters.addEventListener("click", (e) => {
  const chip = e.target.closest("[data-source]");
  if (chip) toggleSource(chip.dataset.source);
});

dom.tagFilters.addEventListener("click", (e) => {
  const chip = e.target.closest("[data-tag]");
  if (chip) toggleTag(chip.dataset.tag);
});

dom.searchInput.addEventListener("input", (e) => onSearchInput(e.target.value));
dom.searchClear.addEventListener("click", () => onSearchInput(""));

dom.loadMoreBtn.addEventListener("click", () => {
  state.displayCount += state.loadIncrement;
  render();
  // Scroll to new items smoothly
  const cards = $$(".card");
  if (cards.length > state.loadIncrement) {
    cards[cards.length - state.loadIncrement - 1]?.scrollIntoView({
      behavior: "smooth",
      block: "nearest",
    });
  }
});

dom.themeToggle.addEventListener("click", toggleTheme);

// Keyboard shortcut: Ctrl+K to focus search
document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "k") {
    e.preventDefault();
    dom.searchInput.focus();
  }
  if (e.key === "Escape") {
    dom.searchInput.blur();
  }
});

// ---- Utilities ----
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function formatNumber(n) {
  if (n >= 1000) return (n / 1000).toFixed(1) + "k";
  return String(n);
}

// ---- Init ----
function init() {
  loadTheme();
  loadData();
}

document.addEventListener("DOMContentLoaded", init);
