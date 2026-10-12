/**
 * SkillBridge - Internship Explorer & Application Tracker Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  initInternshipTabs();
  initApplicationActions();
  initBookmarkButtons();
});

// Tab Switcher between Explorer and Tracker
function initInternshipTabs() {
  const tabBtns = document.querySelectorAll("[data-internship-tab]");
  const tabPanes = document.querySelectorAll(".internship-tab-pane");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-internship-tab");

      tabBtns.forEach(b => {
        b.classList.remove("active", "btn-primary");
        b.classList.add("btn-secondary");
      });
      btn.classList.add("active", "btn-primary");
      btn.classList.remove("btn-secondary");

      tabPanes.forEach(pane => {
        if (pane.id === target) {
          pane.style.display = "block";
        } else {
          pane.style.display = "none";
        }
      });
    });
  });
}

// Application Tracker Actions & External Apply
function initApplicationActions() {
  // Apply & Track button
  document.querySelectorAll(".apply-track-btn").forEach(btn => {
    btn.addEventListener("click", async (e) => {
      const internshipId = btn.getAttribute("data-id");
      const externalUrl = btn.getAttribute("data-url");

      try {
        const res = await fetch("/api/applications/apply", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ internship_id: internshipId })
        });
        const data = await res.json();
        if (data.success) {
          showToast("Added to Application Tracker! Redirecting to demo vacancy…", "success");
          btn.innerText = "✓ Tracked (Applied)";
          btn.classList.add("btn-secondary");
          btn.classList.remove("btn-primary");
          setTimeout(() => {
            window.open(externalUrl, "_blank");
          }, 600);
        }
      } catch (err) {
        window.open(externalUrl, "_blank");
      }
    });
  });

  // Status Change in Tracker
  document.querySelectorAll(".tracker-status-select").forEach(select => {
    select.addEventListener("change", async () => {
      const appId = select.getAttribute("data-app-id");
      const newStatus = select.value;

      try {
        const res = await fetch("/api/applications/update-status", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ app_id: appId, status: newStatus })
        });
        const data = await res.json();
        if (data.success) {
          showToast(data.message, "success");
        } else {
          showToast(data.error || "Failed to update status.", "danger");
        }
      } catch (err) {
        showToast("Error updating application status.", "danger");
      }
    });
  });

  // Delete Application
  document.querySelectorAll(".delete-app-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const appId = btn.getAttribute("data-app-id");
      if (!confirm("Remove this opportunity from your application tracker?")) return;

      try {
        const res = await fetch("/api/applications/delete", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ app_id: appId })
        });
        const data = await res.json();
        if (data.success) {
          showToast(data.message, "info");
          btn.closest("tr")?.remove();
        } else {
          showToast(data.error || "Failed to remove.", "danger");
        }
      } catch (err) {
        showToast("Error removing application.", "danger");
      }
    });
  });
}

// Bookmark Button Clicks
function initBookmarkButtons() {
  document.querySelectorAll(".bookmark-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const internshipId = btn.getAttribute("data-id");
      toggleBookmark(internshipId, btn);
    });
  });
}
