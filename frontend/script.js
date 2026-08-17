const API_BASE = "http://localhost:8000"; // TODO: replace with your deployed Render URL

const form = document.getElementById("search-form");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const query = document.getElementById("query").value.trim();
  const asSong = document.querySelector('input[name="mode"]:checked').value === "song";
  const energy = document.getElementById("energy").value || null;

  if (!query) return;

  statusEl.textContent = asSong ? "Building this song's vibe profile..." : "Searching...";
  resultsEl.innerHTML = "";

  try {
    const response = await fetch(`${API_BASE}/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, as_song: asSong, energy, top_k: 10 }),
    });

    if (!response.ok) throw new Error(`Request failed: ${response.status}`);

    const matches = await response.json();
    statusEl.textContent = "";
    renderResults(matches);
  } catch (err) {
    statusEl.textContent = `Something went wrong: ${err.message}`;
  }
});

function renderResults(matches) {
  if (matches.length === 0) {
    resultsEl.innerHTML = "<p>No matches found.</p>";
    return;
  }

  resultsEl.innerHTML = matches
    .map(
      (m) => `
    <div class="card">
      <h3>${m.name ?? "Unknown"} — ${m.artist ?? "Unknown"} (${m.release_year ?? "?"})</h3>
      <p class="score">match score: ${m.score.toFixed(2)}</p>
      <p>${m.description ?? ""}</p>
      <p class="meta"><strong>Mood:</strong> ${m.mood ?? "-"} &nbsp; <strong>Energy:</strong> ${m.energy ?? "-"} &nbsp; <strong>Era feel:</strong> ${m.era_feel ?? "-"}</p>
      <p class="meta"><strong>Best for:</strong> ${m.best_for ?? "-"}</p>
    </div>
  `
    )
    .join("");
}
