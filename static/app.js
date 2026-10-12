const roleSkills = {
  "Full-Stack Developer": [
    ["HTML & CSS", 4], ["JavaScript", 5], ["React", 4], ["SQL", 3], ["Backend APIs", 4], ["Git & GitHub", 3]
  ],
  "Data Analyst": [
    ["Excel", 4], ["SQL", 4], ["Python", 4], ["Statistics", 3], ["Data Visualization", 4], ["Pandas", 3]
  ],
  "AI/ML Engineer": [
    ["Python", 5], ["Statistics", 4], ["Machine Learning", 4], ["SQL", 3], ["Data Structures", 3], ["Pandas", 3]
  ],
  "Cybersecurity Analyst": [
    ["Networking", 4], ["Linux", 3], ["Python", 3], ["Security Fundamentals", 5], ["Log Analysis", 3]
  ],
  "UI/UX Designer": [
    ["Figma", 4], ["Wireframing", 4], ["Prototyping", 4], ["User Research", 3], ["Visual Design", 4]
  ]
};

const form = document.getElementById("skill-form");
const roleSelect = document.getElementById("role");
const skillInputs = document.getElementById("skill-inputs");
const skillCount = document.getElementById("skill-count");
const resultsPanel = document.getElementById("results-panel");
const internshipResults = document.getElementById("internship-results");

function renderSkillInputs() {
  const skills = roleSkills[roleSelect.value] || [];
  skillInputs.innerHTML = skills.map(([name, required]) => `
    <div class="skill-row">
      <label for="skill-${safeId(name)}">${escapeHTML(name)}<small>Role target: ${required}/5</small></label>
      <select id="skill-${safeId(name)}" data-skill="${escapeHTML(name)}" aria-label="${escapeHTML(name)} proficiency">
        <option value="0">Not learned (0)</option>
        <option value="1">Beginner (1)</option>
        <option value="2">Basic (2)</option>
        <option value="3">Intermediate (3)</option>
        <option value="4">Advanced (4)</option>
        <option value="5">Confident (5)</option>
      </select>
    </div>`).join("");
  updateSkillCount();
}
function safeId(value) { return value.toLowerCase().replace(/[^a-z0-9]+/g, "-"); }
function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
}
function updateSkillCount() {
  const selects = [...skillInputs.querySelectorAll("select[data-skill]")];
  const count = selects.filter(select => Number(select.value) > 0).length;
  skillCount.textContent = `${count} added`;
}
roleSelect.addEventListener("change", renderSkillInputs);
skillInputs.addEventListener("change", updateSkillCount);

function renderTags(items, className) {
  if (!items.length) return `<span class="tag ${className}">None identified</span>`;
  return items.map(item => `<span class="tag ${className}">${escapeHTML(item.name)}</span>`).join("");
}
function renderResults(data) {
  resultsPanel.innerHTML = `
    <div class="result-top">
      <div><h3>Your skill map</h3><p>Target role: ${escapeHTML(data.role)}</p></div>
      <div class="score-pill"><b>${data.readiness}%</b><small>role readiness*</small></div>
    </div>
    <div class="result-section"><h4>✓ Skills at target level</h4><div class="tag-list">${renderTags(data.matched, "")}</div></div>
    <div class="result-section"><h4>↗ Skills to strengthen</h4><div class="tag-list">${renderTags(data.improve, "warn")}</div></div>
    <div class="result-section"><h4>＋ Skills to start learning</h4><div class="tag-list">${renderTags(data.missing, "missing")}</div></div>
    <div class="result-section"><h4>Your suggested next steps</h4>
      ${data.roadmap.length ? data.roadmap.slice(0, 5).map(item => `
        <div class="roadmap-item"><b>${escapeHTML(item.skill)} · ${item.current}/${item.required}</b><p>${escapeHTML(item.suggestion)}</p></div>`).join("") : "<p>Great! All listed skills meet the current target. Try a project to validate your skills.</p>"}
    </div>
    <p class="form-note">*A learning indicator based on this demo's role weights, not a prediction of hiring success.</p>`;
  if (!data.internships.length) {
    internshipResults.innerHTML = `<div class="internship-placeholder"><span>↗</span><b>No sample listings for this role yet</b><p>Add verified opportunities for this role in the backend data.</p></div>`;
    return;
  }
  internshipResults.innerHTML = data.internships.map((job, index) => `
    <article class="internship-card">
      <div class="company-mark">${escapeHTML(job.company.slice(0,1))}</div>
      <h3>${escapeHTML(job.title)}</h3>
      <div class="company">${escapeHTML(job.company)} · Sample listing</div>
      <div class="internship-meta"><span class="meta-chip">${escapeHTML(job.mode)}</span><span class="meta-chip">${escapeHTML(job.level)}</span></div>
      <div class="company">Relevant skills: ${job.skills.map(escapeHTML).join(", ")}</div>
      <div class="match-line"><span>Skill overlap</span><b>${job.match}%</b></div>
      <a href="${escapeHTML(job.url)}" target="_blank" rel="noopener noreferrer">Example link (not a live vacancy) ↗</a>
    </article>`).join("");
  document.getElementById("opportunities").scrollIntoView({behavior: "smooth", block: "start"});
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  const skills = [...skillInputs.querySelectorAll("select[data-skill]")].map(select => ({
    name: select.dataset.skill, level: Number(select.value)
  }));
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;
  button.innerHTML = "Analyzing…";
  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({role: roleSelect.value, skills})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not analyze your skills.");
    renderResults(data);
  } catch (error) {
    resultsPanel.innerHTML = `<div class="empty-state"><h3>Could not analyze skills</h3><p>${escapeHTML(error.message)} Make sure the Flask server is running.</p></div>`;
  } finally {
    button.disabled = false;
    button.innerHTML = 'Analyze my skill gaps <span>→</span>';
  }
});

renderSkillInputs();
