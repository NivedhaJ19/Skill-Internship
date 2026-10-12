/**
 * SkillBridge - Student Dashboard Controller
 * Handles Radar Chart, Skill Management, Milestone Tracking, & Project Showcase
 */

document.addEventListener("DOMContentLoaded", () => {
  initRadarChart();
  initSkillManager();
  initProfileForm();
  initMilestoneChecklist();
  initProjectManager();
});

// Chart.js Radar Visualization
let radarChartInstance = null;

function initRadarChart() {
  const ctx = document.getElementById("skillRadarCanvas");
  if (!ctx || typeof Chart === "undefined") return;

  const rawLabels = ctx.getAttribute("data-labels");
  const rawUserData = ctx.getAttribute("data-user");
  const rawTargetData = ctx.getAttribute("data-target");

  if (!rawLabels) return;

  try {
    const labels = JSON.parse(rawLabels);
    const userData = JSON.parse(rawUserData);
    const targetData = JSON.parse(rawTargetData);

    radarChartInstance = new Chart(ctx, {
      type: "radar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Your Skill Level",
            data: userData,
            backgroundColor: "rgba(16, 185, 129, 0.25)",
            borderColor: "rgba(16, 185, 129, 0.9)",
            pointBackgroundColor: "rgba(16, 185, 129, 1)",
            pointBorderColor: "#fff",
            pointHoverBackgroundColor: "#fff",
            pointHoverBorderColor: "rgba(16, 185, 129, 1)",
            borderWidth: 2
          },
          {
            label: "Role Benchmark Target",
            data: targetData,
            backgroundColor: "rgba(100, 116, 139, 0.08)",
            borderColor: "rgba(100, 116, 139, 0.7)",
            borderDash: [4, 4],
            pointBackgroundColor: "rgba(100, 116, 139, 1)",
            pointBorderColor: "#fff",
            borderWidth: 1.5
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        scales: {
          r: {
            angleLines: { color: "rgba(226, 232, 240, 0.8)" },
            grid: { color: "rgba(226, 232, 240, 0.8)" },
            pointLabels: {
              font: { family: "Plus Jakarta Sans", size: 11, weight: "600" },
              color: "#334155"
            },
            ticks: {
              stepSize: 1,
              display: false
            },
            suggestedMin: 0,
            suggestedMax: 5
          }
        },
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              boxWidth: 14,
              font: { family: "Plus Jakarta Sans", size: 12, weight: "600" },
              color: "#475569"
            }
          }
        }
      }
    });
  } catch (e) {
    console.error("Error creating radar chart:", e);
  }
}

// Skills Management Form & Operations
function initSkillManager() {
  const addSkillForm = document.getElementById("addSkillForm");
  if (addSkillForm) {
    addSkillForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const nameInput = document.getElementById("skillNameInput");
      const levelSelect = document.getElementById("skillLevelSelect");
      const submitBtn = addSkillForm.querySelector("button[type='submit']");

      const skill_name = nameInput ? nameInput.value.trim() : "";
      const proficiency_level = levelSelect ? levelSelect.value : 1;

      if (!skill_name) {
        showToast("Please enter a skill name.", "warning");
        return;
      }

      submitBtn.disabled = true;
      try {
        const res = await fetch("/api/skills/update", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ skill_name, proficiency_level })
        });
        const data = await res.json();
        if (data.success) {
          showToast(data.message, "success");
          setTimeout(() => window.location.reload(), 700);
        } else {
          showToast(data.error || "Failed to add skill.", "danger");
        }
      } catch (err) {
        showToast("Error updating skill.", "danger");
      } finally {
        submitBtn.disabled = false;
      }
    });
  }

  // Delete skill buttons
  document.querySelectorAll(".delete-skill-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const skill_name = btn.getAttribute("data-skill");
      if (!confirm(`Remove "${skill_name}" from your profile?`)) return;

      try {
        const res = await fetch("/api/skills/delete", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ skill_name })
        });
        const data = await res.json();
        if (data.success) {
          showToast(data.message, "success");
          btn.closest(".skill-chip")?.remove();
          setTimeout(() => window.location.reload(), 700);
        } else {
          showToast(data.error || "Failed to remove skill.", "danger");
        }
      } catch (err) {
        showToast("Error removing skill.", "danger");
      }
    });
  });
}

// Profile Modal & Updates
function initProfileForm() {
  const profileForm = document.getElementById("editProfileForm");
  if (profileForm) {
    profileForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(profileForm);
      const payload = Object.fromEntries(formData.entries());

      const submitBtn = profileForm.querySelector("button[type='submit']");
      submitBtn.disabled = true;
      submitBtn.innerText = "Saving…";

      try {
        const res = await fetch("/api/profile/update", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
          showToast("Profile updated successfully!", "success");
          closeModal("editProfileModal");
          setTimeout(() => window.location.reload(), 700);
        } else {
          showToast(data.error || "Update failed.", "danger");
        }
      } catch (err) {
        showToast("Error updating profile.", "danger");
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = "Save Changes";
      }
    });
  }

  // Target role switcher directly from header
  const targetRoleSelector = document.getElementById("headerTargetRoleSelector");
  if (targetRoleSelector) {
    targetRoleSelector.addEventListener("change", async () => {
      const newRole = targetRoleSelector.value;
      try {
        const res = await fetch("/api/profile/update", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ target_role: newRole, name: targetRoleSelector.getAttribute("data-user-name") })
        });
        const data = await res.json();
        if (data.success) {
          showToast(`Target role switched to ${newRole}!`, "success");
          setTimeout(() => window.location.reload(), 600);
        }
      } catch (err) {
        showToast("Failed to change target role.", "danger");
      }
    });
  }
}

// Milestone Checklist
function initMilestoneChecklist() {
  document.querySelectorAll(".milestone-checkbox").forEach(chk => {
    chk.addEventListener("change", async () => {
      const milestone_id = chk.getAttribute("data-id");
      try {
        const res = await fetch("/api/milestones/toggle", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ milestone_id })
        });
        const data = await res.json();
        if (data.success) {
          const item = chk.closest(".milestone-item");
          if (data.completed) {
            item.classList.add("completed");
            showToast("Milestone completed! Keep moving forward.", "success");
          } else {
            item.classList.remove("completed");
          }
        }
      } catch (err) {
        showToast("Error updating milestone.", "danger");
      }
    });
  });
}

// Project Showcase CRUD
function initProjectManager() {
  const addProjectForm = document.getElementById("addProjectForm");
  if (addProjectForm) {
    addProjectForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(addProjectForm);
      const payload = Object.fromEntries(formData.entries());

      const submitBtn = addProjectForm.querySelector("button[type='submit']");
      submitBtn.disabled = true;

      try {
        const res = await fetch("/api/projects/add", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
          showToast(data.message, "success");
          closeModal("addProjectModal");
          setTimeout(() => window.location.reload(), 700);
        } else {
          showToast(data.error || "Failed to add project.", "danger");
        }
      } catch (err) {
        showToast("Error adding project.", "danger");
      } finally {
        submitBtn.disabled = false;
      }
    });
  }

  // Delete project
  document.querySelectorAll(".delete-project-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const project_id = btn.getAttribute("data-id");
      if (!confirm("Are you sure you want to remove this project?")) return;

      try {
        const res = await fetch("/api/projects/delete", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ project_id })
        });
        const data = await res.json();
        if (data.success) {
          showToast(data.message, "info");
          btn.closest(".project-card")?.remove();
        } else {
          showToast(data.error || "Failed to delete project.", "danger");
        }
      } catch (err) {
        showToast("Error deleting project.", "danger");
      }
    });
  });
}
