const API_BASE = "https://vibemax.onrender.com";
// const API_BASE = "http://localhost:8000";

const SONG_MESSAGES = [
  "Waking up the server...",
  "Resolving the track...",
  "Reading the room...",
  "Building this song's vibe profile...",
  "Almost there...",
];

const PHRASE_MESSAGES = [
  "Waking up the server...",
  "Reading the vibe...",
  "Searching...",
  "Almost there...",
];

const form = document.getElementById("search-form");
const statusEl = document.getElementById("status");
const statusTextEl = document.getElementById("status-text");
const spinnerEl = document.getElementById("spinner");
const resultsEl = document.getElementById("results");

let messageInterval = null;

function startLoading(messages) {
  spinnerEl.classList.add("active");
  let i = 0;
  statusTextEl.textContent = messages[0];
  messageInterval = setInterval(() => {
    i = (i + 1) % messages.length;
    statusTextEl.textContent = messages[i];
  }, 2500);
}

function stopLoading(finalText = "") {
  clearInterval(messageInterval);
  spinnerEl.classList.remove("active");
  statusTextEl.textContent = finalText;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const query = document.getElementById("query").value.trim();
  const asSong = document.querySelector('input[name="mode"]:checked').value === "song";
  const energy = document.getElementById("energy").value || null;

  if (!query) return;

  resultsEl.innerHTML = "";
  startLoading(asSong ? SONG_MESSAGES : PHRASE_MESSAGES);

  try {
    const response = await fetch(`${API_BASE}/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, as_song: asSong, energy, top_k: 10 }),
    });

    if (!response.ok) throw new Error(`Request failed: ${response.status}`);

    const matches = await response.json();
    stopLoading();
    renderResults(matches);
  } catch (err) {
    stopLoading(`Something went wrong: ${err.message}`);
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
