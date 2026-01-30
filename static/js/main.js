// Main - Navbar toggle, theme toggle, global event listeners

document.addEventListener("DOMContentLoaded", () => {
  initNavbar();
  initSidebar();
  initTheme();
  initDropdowns();
  initUserMenu();
});

// Navbar initialization
function initNavbar() {
  const navbarToggle = document.getElementById("navbarToggle");
  const sidebar = document.getElementById("sidebar");
  const sidebarOverlay = document.getElementById("sidebarOverlay");
  const sidebarClose = document.getElementById("sidebarClose");

  if (navbarToggle && sidebar) {
    navbarToggle.addEventListener("click", () => {
      sidebar.classList.toggle("active");
      if (sidebarOverlay) {
        sidebarOverlay.classList.toggle("active");
      }
    });
  }

  if (sidebarClose && sidebar) {
    sidebarClose.addEventListener("click", () => {
      sidebar.classList.remove("active");
      if (sidebarOverlay) {
        sidebarOverlay.classList.remove("active");
      }
    });
  }

  if (sidebarOverlay) {
    sidebarOverlay.addEventListener("click", () => {
      sidebar?.classList.remove("active");
      sidebarOverlay.classList.remove("active");
    });
  }
}

// Sidebar initialization
function initSidebar() {
  const currentPath = window.location.pathname;
  const sidebarLinks = document.querySelectorAll(".sidebar-link");

  sidebarLinks.forEach((link) => {
    const href = link.getAttribute("href");
    if (href && currentPath.startsWith(href) && href !== "/") {
      link.classList.add("active");
    } else if (href === "/" && currentPath === "/") {
      link.classList.add("active");
    }
  });

  // Close sidebar on mobile when link is clicked
  sidebarLinks.forEach((link) => {
    link.addEventListener("click", () => {
      if (window.innerWidth <= 768) {
        const sidebar = document.getElementById("sidebar");
        const sidebarOverlay = document.getElementById("sidebarOverlay");

        sidebar?.classList.remove("active");
        sidebarOverlay?.classList.remove("active");
      }
    });
  });
}

// Theme toggle
function initTheme() {
  const themeToggle = document.getElementById("themeToggle");
  const currentTheme = storage.get("theme", "dark");

  // Apply saved theme
  document.documentElement.setAttribute("data-theme", currentTheme);

  if (themeToggle) {
    // Update icon
    updateThemeIcon(currentTheme);

    themeToggle.addEventListener("click", () => {
      const newTheme =
        document.documentElement.getAttribute("data-theme") === "dark"
          ? "light"
          : "dark";

      document.documentElement.setAttribute("data-theme", newTheme);
      storage.set("theme", newTheme);
      updateThemeIcon(newTheme);

      toast.info(`Switched to ${newTheme} theme`);
    });
  }
}

function updateThemeIcon(theme) {
  const themeToggle = document.getElementById("themeToggle");
  if (themeToggle) {
    const icon = themeToggle.querySelector("i");
    if (icon) {
      icon.className = theme === "dark" ? "fas fa-sun" : "fas fa-moon";
    }
  }
}

// Dropdown menus
function initDropdowns() {
  const dropdowns = document.querySelectorAll(".dropdown");

  dropdowns.forEach((dropdown) => {
    const toggle = dropdown.querySelector(".dropdown-toggle");
    const menu = dropdown.querySelector(".dropdown-menu");

    if (toggle) {
      toggle.addEventListener("click", (e) => {
        e.stopPropagation();

        // Close other dropdowns
        dropdowns.forEach((other) => {
          if (other !== dropdown) {
            other.classList.remove("active");
          }
        });

        dropdown.classList.toggle("active");
      });
    }
  });

  // Close dropdowns when clicking outside
  document.addEventListener("click", () => {
    dropdowns.forEach((dropdown) => {
      dropdown.classList.remove("active");
    });
  });
}

// User menu
function initUserMenu() {
  const user = getCurrentUser();
  const userNameEl = document.getElementById("userName");
  const userRoleEl = document.getElementById("userRole");
  const userAvatarEl = document.getElementById("userAvatar");

  if (user) {
    if (userNameEl) {
      userNameEl.textContent = user.name || "User";
    }

    if (userRoleEl) {
      userRoleEl.textContent = user.role || "Student";
    }

    if (userAvatarEl) {
      const initials = (user.name || "U")
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);
      userAvatarEl.textContent = initials;
    }
  }

  // Logout button
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", (e) => {
      e.preventDefault();
      logout();
    });
  }
}

// Notification handlers
function initNotifications() {
  const notificationBtn = document.getElementById("notificationBtn");

  if (notificationBtn) {
    notificationBtn.addEventListener("click", () => {
      loadNotifications();
    });
  }
}

async function loadNotifications() {
  try {
    const response = await api.get("/notifications");

    if (response.success) {
      displayNotifications(response.notifications);
    }
  } catch (error) {
    console.error("Notifications error:", error);
  }
}

function displayNotifications(notifications) {
  // Implementation for notification display
  console.log("Notifications:", notifications);
}

// Search functionality
function initSearch() {
  const searchInput = document.getElementById("navbarSearch");

  if (searchInput) {
    searchInput.addEventListener(
      "input",
      debounce((e) => {
        performSearch(e.target.value);
      }, 300),
    );
  }
}

async function performSearch(query) {
  if (!query || query.length < 2) return;

  try {
    const response = await api.get(`/search?q=${encodeURIComponent(query)}`);

    if (response.success) {
      displaySearchResults(response.results);
    }
  } catch (error) {
    console.error("Search error:", error);
  }
}

function displaySearchResults(results) {
  // Implementation for search results display
  console.log("Search results:", results);
}

// Keyboard shortcuts
document.addEventListener("keydown", (e) => {
  // Ctrl/Cmd + K for search
  if ((e.ctrlKey || e.metaKey) && e.key === "k") {
    e.preventDefault();
    const searchInput = document.getElementById("navbarSearch");
    searchInput?.focus();
  }

  // Escape to close modals/dropdowns
  if (e.key === "Escape") {
    // Close all modals
    document.querySelectorAll(".modal-overlay.active").forEach((modal) => {
      modal.classList.remove("active");
    });

    // Close all dropdowns
    document.querySelectorAll(".dropdown.active").forEach((dropdown) => {
      dropdown.classList.remove("active");
    });

    // Close sidebar on mobile
    if (window.innerWidth <= 768) {
      const sidebar = document.getElementById("sidebar");
      const sidebarOverlay = document.getElementById("sidebarOverlay");

      sidebar?.classList.remove("active");
      sidebarOverlay?.classList.remove("active");
    }
  }
});

// Handle window resize
let resizeTimer;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    // Close sidebar on desktop if open
    if (window.innerWidth > 768) {
      const sidebar = document.getElementById("sidebar");
      const sidebarOverlay = document.getElementById("sidebarOverlay");

      sidebar?.classList.remove("active");
      sidebarOverlay?.classList.remove("active");
    }
  }, 250);
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    const href = this.getAttribute("href");
    if (href === "#") return;

    e.preventDefault();
    const target = document.querySelector(href);

    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  });
});

// Back to top button
function initBackToTop() {
  const backToTopBtn = document.getElementById("backToTop");

  if (backToTopBtn) {
    window.addEventListener("scroll", () => {
      if (window.pageYOffset > 300) {
        backToTopBtn.style.display = "block";
      } else {
        backToTopBtn.style.display = "none";
      }
    });

    backToTopBtn.addEventListener("click", () => {
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    });
  }
}

// Initialize all features
initNotifications();
initSearch();
initBackToTop();

// Handle online/offline status
window.addEventListener("online", () => {
  toast.success("Connection restored");
});

window.addEventListener("offline", () => {
  toast.warning("No internet connection");
});

// Service Worker registration disabled - uncomment when sw.js is created
// if ('serviceWorker' in navigator) {
//     window.addEventListener('load', () => {
//         navigator.serviceWorker.register('/sw.js')
//             .then(registration => {
//                 console.log('ServiceWorker registered:', registration);
//             })
//             .catch(error => {
//                 console.log('ServiceWorker registration failed:', error);
//             });
//     });
// }
