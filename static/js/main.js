/* ═══════════════════════════════════════════════════════════════
   EduPeak — Core JavaScript
   Navbar, theme toggle, mobile menu, toasts, scroll animations
   ═══════════════════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", function () {
  /* ── Navbar scroll shadow ─────────────────────────────────── */
  const nav = document.getElementById("mainNav");
  if (nav) {
    window.addEventListener("scroll", function () {
      if (window.scrollY > 10) nav.classList.add("scrolled");
      else nav.classList.remove("scrolled");
    });
  }

  /* ── Hamburger / mobile menu ──────────────────────────────── */
  const hamburger = document.getElementById("hamburger");
  const mobileMenu = document.getElementById("mobileMenu");
  if (hamburger && mobileMenu) {
    hamburger.addEventListener("click", function () {
      hamburger.classList.toggle("open");
      mobileMenu.classList.toggle("open");
    });
    mobileMenu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        hamburger.classList.remove("open");
        mobileMenu.classList.remove("open");
      });
    });
  }

  /* ── User dropdown ─────────────────────────────────────────── */
  const userMenuBtn = document.getElementById("userMenuBtn");
  const userDropdown = document.getElementById("userDropdown");
  if (userMenuBtn && userDropdown) {
    userMenuBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      userDropdown.classList.toggle("open");
    });
    document.addEventListener("click", function () {
      userDropdown.classList.remove("open");
    });
  }

  /* ── Dark mode toggle ─────────────────────────────────────── */
  const themeToggle = document.getElementById("themeToggle");
  const themeIcon = document.getElementById("themeIcon");
  const htmlEl = document.documentElement;

  function applyTheme(theme) {
    htmlEl.setAttribute("data-theme", theme);
    if (themeIcon) {
      themeIcon.className = theme === "dark" ? "bi bi-sun-fill" : "bi bi-moon-fill";
    }
    localStorage.setItem("ep-theme", theme);
  }

  const savedTheme = localStorage.getItem("ep-theme") || "light";
  applyTheme(savedTheme);

  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      const current = htmlEl.getAttribute("data-theme");
      applyTheme(current === "dark" ? "light" : "dark");
    });
  }

  /* ── Toast auto-dismiss ────────────────────────────────────── */
  document.querySelectorAll(".ep-toast").forEach((toast) => {
    const closeBtn = toast.querySelector(".ep-toast-close");
    const dismiss = () => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      setTimeout(() => toast.remove(), 300);
    };
    if (closeBtn) closeBtn.addEventListener("click", dismiss);
    setTimeout(dismiss, 5000);
  });

  /* ── Scroll-triggered fade-in animations ──────────────────── */
  const fadeEls = document.querySelectorAll(".ep-fade-in");
  if (fadeEls.length && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1 }
    );
    fadeEls.forEach((el) => observer.observe(el));
  } else {
    fadeEls.forEach((el) => el.classList.add("visible"));
  }

  /* ── Animated stat counters ───────────────────────────────── */
  const counters = document.querySelectorAll("[data-counter]");
  if (counters.length && "IntersectionObserver" in window) {
    const counterObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            counterObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );
    counters.forEach((el) => counterObserver.observe(el));
  }

  function animateCounter(el) {
    const target = parseInt(el.getAttribute("data-counter"), 10) || 0;
    const duration = 1500;
    const startTime = performance.now();
    function step(now) {
      const progress = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.floor(eased * target).toLocaleString();
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = target.toLocaleString();
    }
    requestAnimationFrame(step);
  }

  /* ── Category chip filter active state (visual only) ─────── */
  document.querySelectorAll(".ep-category-chip").forEach((chip) => {
    chip.addEventListener("click", function () {
      document.querySelectorAll(".ep-category-chip").forEach((c) => c.classList.remove("active"));
      this.classList.add("active");
    });
  });
});

/* ── Utility: get CSRF token from cookie ────────────────────── */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie("csrftoken");

/* ── Reusable toast trigger (for JS-driven flows) ───────────── */
function showToast(message, type = "info") {
  const container = document.querySelector(".ep-toast-container") || (() => {
    const c = document.createElement("div");
    c.className = "ep-toast-container";
    document.body.appendChild(c);
    return c;
  })();

  const icons = {
    success: "bi-check-circle-fill",
    error: "bi-x-circle-fill",
    info: "bi-info-circle-fill",
  };

  const toast = document.createElement("div");
  toast.className = `ep-toast ep-toast-${type}`;
  toast.innerHTML = `<i class="bi ${icons[type] || icons.info}"></i><span>${message}</span><button class="ep-toast-close"><i class="bi bi-x"></i></button>`;
  container.appendChild(toast);

  const dismiss = () => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    setTimeout(() => toast.remove(), 300);
  };
  toast.querySelector(".ep-toast-close").addEventListener("click", dismiss);
  setTimeout(dismiss, 5000);
}
