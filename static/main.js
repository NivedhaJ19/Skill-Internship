/**
 * SkillBridge - Main Client Utilities & Global Interactions
 */

// Mobile Navigation Toggle
document.addEventListener("DOMContentLoaded", () => {
  const mobileToggle = document.getElementById("mobileToggle");
  const navLinks = document.getElementById("navLinks");
  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener("click", () => {
      navLinks.classList.toggle("mobile-open");
    });
  }

  // Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = "opacity 0.4s ease";
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 400);
    }, 5000);
  });

  // Setup Modals
  initModals();

  // Setup AI Assistant
  initAIAssistant();

  // Setup Resume Extractor
  initResumeExtractor();
});

// Toast Notification System
function showToast(message, type = "success") {
  let toastContainer = document.getElementById("toastContainer");
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.id = "toastContainer";
    toastContainer.style.position = "fixed";
    toastContainer.style.bottom = "20px";
    toastContainer.style.right = "20px";
    toastContainer.style.zIndex = "9999";
    toastContainer.style.display = "flex";
    toastContainer.style.flexDirection = "column";
    toastContainer.style.gap = "10px";
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement("div");
  toast.className = `alert alert-${type}`;
  toast.style.margin = "0";
  toast.style.boxShadow = "var(--shadow-lg)";
  toast.style.minWidth = "280px";
  toast.innerHTML = `
    <span>${message}</span>
    <button style="background:none; border:none; cursor:pointer; font-size:1.1rem; margin-left:10px;" onclick="this.parentElement.remove()">×</button>
  `;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = "opacity 0.4s ease";
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

// Modal Handlers
function initModals() {
  document.querySelectorAll("[data-modal-open]").forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-modal-open");
      const modal = document.getElementById(targetId);
      if (modal) modal.classList.add("active");
    });
  });

  document.querySelectorAll(".modal-close, .modal-overlay").forEach(el => {
    el.addEventListener("click", (e) => {
      if (e.target === el) {
        el.closest(".modal-overlay")?.classList.remove("active");
      }
    });
  });
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove("active");
}

// Bookmark Toggle API Helper
async function toggleBookmark(internshipId, btn) {
  try {
    const res = await fetch("/api/internships/bookmark", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ internship_id: internshipId })
    });
    const data = await res.json();
    if (data.success) {
      if (data.bookmarked) {
        btn.innerHTML = "★ Bookmarked";
        btn.classList.add("btn-primary");
        btn.classList.remove("btn-secondary");
        showToast("Internship saved to bookmarks!", "success");
      } else {
        btn.innerHTML = "☆ Bookmark";
        btn.classList.remove("btn-primary");
        btn.classList.add("btn-secondary");
        showToast("Removed from bookmarks.", "info");
      }
    } else {
      showToast(data.error || "Failed to update bookmark.", "danger");
    }
  } catch (err) {
    showToast("Network error updating bookmark.", "danger");
  }
}

// AI Career Assistant Logic
function initAIAssistant() {
  const aiChatModal = document.getElementById("aiChatModal");
  const aiChatBtn = document.getElementById("aiChatFloatingBtn");
  const aiInput = document.getElementById("aiChatInput");
  const aiSendBtn = document.getElementById("aiChatSendBtn");
  const messagesBox = document.getElementById("aiChatMessages");

  if (aiChatBtn && aiChatModal) {
    aiChatBtn.addEventListener("click", () => {
      aiChatModal.classList.add("active");
      if (aiInput) aiInput.focus();
    });
  }

  // Suggestion chips
  document.querySelectorAll(".suggestion-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      if (aiInput) {
        aiInput.value = chip.textContent;
        sendMessage();
      }
    });
  });

  if (aiSendBtn) {
    aiSendBtn.addEventListener("click", sendMessage);
  }
  if (aiInput) {
    aiInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  async function sendMessage() {
    if (!aiInput) return;
    const text = aiInput.value.trim();
    if (!text) return;

    aiInput.value = "";
    appendMessage(text, "user");

    const loadingId = appendMessage("Thinking & analyzing career pathways…", "bot", true);

    try {
      const res = await fetch("/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();

      const loadingElem = document.getElementById(loadingId);
      if (loadingElem) loadingElem.remove();

      if (data.reply) {
        appendMessage(data.reply, "bot");
      } else {
        appendMessage(data.error || "Sorry, I could not generate advice at this moment.", "bot");
      }
    } catch (err) {
      const loadingElem = document.getElementById(loadingId);
      if (loadingElem) loadingElem.remove();
      appendMessage("Network error connecting to AI assistant.", "bot");
    }
  }

  function appendMessage(content, sender, isLoading = false) {
    if (!messagesBox) return "";
    const msg = document.createElement("div");
    msg.className = `chat-bubble ${sender}`;
    const id = "msg-" + Date.now();
    msg.id = id;

    if (isLoading) {
      msg.innerHTML = `<i>${content}</i>`;
    } else {
      // Basic markdown parser for headings and bullets
      let formatted = escapeHTML(content)
        .replace(/### (.*?)\n/g, '<h4>$1</h4>')
        .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
        .replace(/\*(.*?)\*/g, '<i>$1</i>')
        .replace(/\n- (.*?)/g, '<br>• $1')
        .replace(/\n1\. (.*?)/g, '<br>1. $1')
        .replace(/\n2\. (.*?)/g, '<br>2. $1')
        .replace(/\n3\. (.*?)/g, '<br>3. $1')
        .replace(/\n\n/g, '<br><br>');
      msg.innerHTML = formatted;
    }

    messagesBox.appendChild(msg);
    messagesBox.scrollTop = messagesBox.scrollHeight;
    return id;
  }
}

// Resume Skill Extractor Logic
function initResumeExtractor() {
  const scanBtn = document.getElementById("scanResumeBtn");
  const resumeModal = document.getElementById("resumeModal");
  const resumeText = document.getElementById("resumeText");
  const resumeFile = document.getElementById("resumeFile");
  const parseBtn = document.getElementById("parseResumeBtn");
  const extractedArea = document.getElementById("extractedSkillsArea");
  const importBtn = document.getElementById("importSkillsBtn");

  if (scanBtn && resumeModal) {
    scanBtn.addEventListener("click", () => {
      resumeModal.classList.add("active");
    });
  }

  let extractedList = [];

  if (parseBtn) {
    parseBtn.addEventListener("click", async () => {
      const text = resumeText ? resumeText.value.trim() : "";
      const file = resumeFile && resumeFile.files[0] ? resumeFile.files[0] : null;

      if (!text && !file) {
        showToast("Please enter resume text or choose a text file.", "warning");
        return;
      }

      parseBtn.disabled = true;
      parseBtn.innerText = "Extracting skills…";

      try {
        let res;
        if (file) {
          const formData = new FormData();
          formData.append("resume_file", file);
          res = await fetch("/api/resume/extract", { method: "POST", body: formData });
        } else {
          res = await fetch("/api/resume/extract", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
          });
        }

        const data = await res.json();
        if (data.success && data.skills) {
          extractedList = data.skills;
          renderExtractedSkills(data.skills);
        } else {
          showToast(data.error || "No skills identified.", "warning");
        }
      } catch (err) {
        showToast("Error extracting resume skills.", "danger");
      } finally {
        parseBtn.disabled = false;
        parseBtn.innerText = "Extract Skills";
      }
    });
  }

  function renderExtractedSkills(skills) {
    if (!extractedArea) return;
    if (!skills.length) {
      extractedArea.innerHTML = "<p class='text-muted'>No recognizable technical skills detected. Try pasting raw text.</p>";
      if (importBtn) importBtn.style.display = "none";
      return;
    }

    extractedArea.innerHTML = `
      <h4 style="margin: 1rem 0 0.5rem; font-size: 0.95rem;">Identified ${skills.length} Technical Skills:</h4>
      <div style="display:flex; flex-wrap:wrap; gap:0.5rem; max-height:160px; overflow-y:auto; padding:0.5rem; border:1px solid var(--slate-200); border-radius:var(--radius-md);">
        ${skills.map(s => `
          <span class="badge badge-green" style="font-size:0.8rem; padding:0.35rem 0.65rem;">
            ${escapeHTML(s.name)} (Lvl ${s.level}/5)
          </span>
        `).join("")}
      </div>
    `;

    if (importBtn) {
      importBtn.style.display = "inline-flex";
    }
  }

  if (importBtn) {
    importBtn.addEventListener("click", async () => {
      if (!extractedList.length) return;
      importBtn.disabled = true;
      importBtn.innerText = "Importing…";

      try {
        const res = await fetch("/api/skills/batch", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ skills: extractedList })
        });
        const data = await res.json();
        if (data.success) {
          showToast(data.message, "success");
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showToast(data.error || "Import failed.", "danger");
        }
      } catch (err) {
        showToast("Error importing skills.", "danger");
      } finally {
        importBtn.disabled = false;
      }
    });
  }
}

function escapeHTML(str) {
  return String(str || "").replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
}
