(() => {
  "use strict";

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const header = document.querySelector("[data-site-header]");
  const toggle = document.querySelector("[data-nav-toggle]");
  const panel = document.querySelector("[data-nav-panel]");
  const overlay = document.querySelector("[data-nav-overlay]");
  const toggleLabel = document.querySelector("[data-nav-toggle-label]");
  const dashboardToggle = document.querySelector("[data-dashboard-menu]");
  const dashboardClose = document.querySelector("[data-dashboard-menu-close]");
  const dashboardSidebar = document.querySelector("[data-dashboard-sidebar]");
  const dashboardOverlay = document.querySelector("[data-dashboard-menu-overlay]");
  const compactNavigation = window.matchMedia("(max-width: 760px)");
  const compactDashboardNavigation = window.matchMedia("(max-width: 900px)");

  const isMenuOpen = () => Boolean(panel?.classList.contains("is-open"));
  const menuFocusables = () => [
    ...(toggle ? [toggle] : []),
    ...Array.from(panel?.querySelectorAll("a, button, [tabindex]:not([tabindex='-1'])") || []),
  ];

  const setMenuState = (shouldOpen, { restoreFocus = false } = {}) => {
    if (!toggle || !panel) return;

    const open = shouldOpen && compactNavigation.matches;
    toggle.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
    if (toggleLabel) toggleLabel.textContent = open ? "Close navigation" : "Open navigation";
    panel.classList.toggle("is-open", open);
    panel.setAttribute("aria-hidden", String(!open && compactNavigation.matches));
    panel.inert = !open && compactNavigation.matches;
    overlay?.classList.toggle("is-open", open);
    overlay?.setAttribute("aria-hidden", String(!open));
    header?.classList.toggle("is-menu-open", open);
    document.documentElement.classList.toggle("nav-open", open);
    document.body.classList.toggle("nav-open", open);

    if (open) {
      window.requestAnimationFrame(() => toggle.focus());
    } else if (restoreFocus) {
      toggle.focus();
    }
  };

  if (toggle && panel) {
    setMenuState(false);

    const closeMenu = ({ restoreFocus = false } = {}) => setMenuState(false, { restoreFocus });
    const openMenu = () => setMenuState(true);
    const handleMenuOutsideClick = (event) => {
      if (!isMenuOpen() || panel.contains(event.target) || toggle.contains(event.target)) return;
      if (overlay && event.target === overlay) return;
      closeMenu({ restoreFocus: true });
    };

    toggle.addEventListener("click", () => {
      if (isMenuOpen()) closeMenu({ restoreFocus: true });
      else openMenu();
    });
    panel.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => closeMenu()));
    overlay?.addEventListener("click", () => closeMenu({ restoreFocus: true }));
    document.addEventListener("click", handleMenuOutsideClick, true);
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && isMenuOpen()) {
        closeMenu({ restoreFocus: true });
        return;
      }
      if (event.key === "Tab" && isMenuOpen()) {
        const focusable = menuFocusables();
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (!first || !last) return;
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    });

    compactNavigation.addEventListener("change", () => setMenuState(false));
  }

  if (dashboardToggle && dashboardSidebar) {
    const dashboardToggleLabel = document.querySelector("[data-dashboard-menu-label]");
    const isDashboardMenuOpen = () => dashboardSidebar.classList.contains("is-open");
    const dashboardFocusables = () => Array.from(
      dashboardSidebar.querySelectorAll("a, button, [tabindex]:not([tabindex='-1'])")
    );

    const setDashboardMenuState = (shouldOpen, { restoreFocus = false } = {}) => {
      const open = shouldOpen && compactDashboardNavigation.matches;
      dashboardSidebar.classList.toggle("is-open", open);
      dashboardSidebar.setAttribute("aria-hidden", String(!open && compactDashboardNavigation.matches));
      dashboardSidebar.inert = !open && compactDashboardNavigation.matches;
      dashboardOverlay?.classList.toggle("is-open", open);
      dashboardOverlay?.setAttribute("aria-hidden", String(!open));
      dashboardToggle.classList.toggle("is-open", open);
      dashboardToggle.setAttribute("aria-expanded", String(open));
      dashboardToggle.setAttribute("aria-label", open ? "Close dashboard menu" : "Open dashboard menu");
      if (dashboardToggleLabel) dashboardToggleLabel.textContent = open ? "Close dashboard menu" : "Open dashboard menu";
      dashboardClose?.setAttribute("aria-hidden", String(!open));
      document.documentElement.classList.toggle("dashboard-menu-open", open);
      document.body.classList.toggle("dashboard-menu-open", open);

      if (open) {
        window.requestAnimationFrame(() => (dashboardClose || dashboardToggle).focus());
      } else if (restoreFocus) {
        dashboardToggle.focus();
      }
    };

    setDashboardMenuState(false);
    const closeDashboardMenu = ({ restoreFocus = false } = {}) =>
      setDashboardMenuState(false, { restoreFocus });
    const openDashboardMenu = () => setDashboardMenuState(true);
    const handleDashboardOutsideClick = (event) => {
      if (!isDashboardMenuOpen() || dashboardSidebar.contains(event.target) || dashboardToggle.contains(event.target)) return;
      if (dashboardOverlay && event.target === dashboardOverlay) return;
      closeDashboardMenu({ restoreFocus: true });
    };

    dashboardToggle.addEventListener("click", () => {
      if (isDashboardMenuOpen()) closeDashboardMenu({ restoreFocus: true });
      else openDashboardMenu();
    });
    dashboardClose?.addEventListener("click", () => closeDashboardMenu({ restoreFocus: true }));
    dashboardOverlay?.addEventListener("click", () => closeDashboardMenu({ restoreFocus: true }));
    dashboardSidebar.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => closeDashboardMenu()));
    document.addEventListener("click", handleDashboardOutsideClick, true);
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && isDashboardMenuOpen()) {
        closeDashboardMenu({ restoreFocus: true });
        return;
      }
      if (event.key === "Tab" && isDashboardMenuOpen()) {
        const focusable = dashboardFocusables();
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (!first || !last) return;
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    });
    compactDashboardNavigation.addEventListener("change", () => setDashboardMenuState(false));
  }

  if (header) {
    const updateHeader = () => header.classList.toggle("is-scrolled", window.scrollY > 24);
    updateHeader();
    window.addEventListener("scroll", updateHeader, { passive: true });
  }

  const sectionLinks = Array.from(document.querySelectorAll("[data-section-link]"));
  if (sectionLinks.length && "IntersectionObserver" in window) {
    const sections = sectionLinks
      .map((link) => document.getElementById(link.dataset.sectionLink))
      .filter(Boolean);
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        sectionLinks.forEach((link) => {
          const active = link.dataset.sectionLink === entry.target.id;
          link.classList.toggle("is-active", active);
          if (active) link.setAttribute("aria-current", "true");
          else link.removeAttribute("aria-current");
        });
      });
    }, { rootMargin: "-35% 0px -55% 0px", threshold: 0 });
    sections.forEach((section) => observer.observe(section));
  }

  const gsapAvailable = !reducedMotion && window.gsap && window.ScrollTrigger;
  if (gsapAvailable) {
    window.gsap.registerPlugin(window.ScrollTrigger);
    const motionMedia = window.gsap.matchMedia();
    motionMedia.add({ desktop: "(min-width: 761px)", mobile: "(max-width: 760px)" }, (context) => {
      const isMobile = context.conditions.mobile;
      const heroItems = document.querySelectorAll("[data-hero-item]");
      const heroHeading = document.querySelector("[data-hero-heading]");
      const heroVisual = document.querySelector("[data-hero-visual]");

      if (heroHeading || heroItems.length || heroVisual) {
        const timeline = window.gsap.timeline({ defaults: { ease: "power3.out" } });
        if (header) timeline.from(header, { y: isMobile ? -12 : -20, opacity: 0, duration: 0.55 });
        if (heroItems.length) timeline.from(heroItems, { y: isMobile ? 12 : 18, opacity: 0, stagger: 0.12, duration: 0.65 }, "-=.1");
        if (heroHeading) timeline.from(heroHeading, { y: isMobile ? 20 : 34, opacity: 0, duration: 0.8 }, "<.1");
        if (heroVisual) timeline.from(heroVisual, { y: isMobile ? 18 : 28, opacity: 0, scale: isMobile ? 0.995 : 0.985, duration: 0.9 }, "<.16");
      }

      window.gsap.utils.toArray("[data-reveal]").forEach((element) => {
        window.gsap.from(element, {
          y: isMobile ? 16 : 24,
          opacity: 0,
          duration: 0.7,
          ease: "power3.out",
          scrollTrigger: { trigger: element, start: "top 82%", once: true },
        });
      });

      window.gsap.utils.toArray("[data-project-row]").forEach((element) => {
        const media = element.querySelector(".project-row__media");
        window.gsap.from(element, {
          opacity: 0,
          y: isMobile ? 20 : 32,
          duration: 0.75,
          ease: "power3.out",
          scrollTrigger: { trigger: element, start: "top 86%", once: true },
        });
        if (media && !isMobile) {
          window.gsap.from(media, {
            scale: 0.96,
            scrollTrigger: { trigger: element, start: "top bottom", end: "bottom top", scrub: 0.5 },
          });
        }
      });
    });
  }

  const canHover = !reducedMotion && window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (canHover) {
    document.querySelectorAll(".button").forEach((button) => {
      button.addEventListener("pointermove", (event) => {
        const rect = button.getBoundingClientRect();
        const x = (event.clientX - rect.left - rect.width / 2) * 0.08;
        const y = (event.clientY - rect.top - rect.height / 2) * 0.08;
        button.style.transform = `translate(${x}px, ${y}px)`;
      });
      button.addEventListener("pointerleave", () => { button.style.transform = ""; });
    });
  }
  const loadingForms = Array.from(document.querySelectorAll("form[data-loading-form]"));
  const restoreSubmitButton = (form) => {
    const button = form.querySelector("[data-loading-original]");
    if (!button) return;
    button.innerHTML = button.dataset.loadingOriginal;
    delete button.dataset.loadingOriginal;
    button.disabled = false;
    button.removeAttribute("aria-disabled");
    button.classList.remove("is-loading");
    form.removeAttribute("aria-busy");
    delete form.dataset.submitting;
  };

  loadingForms.forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (form.dataset.submitting === "true") {
        event.preventDefault();
        return;
      }

      const submitter = event.submitter || form.querySelector("button[type='submit'], input[type='submit']");
      if (!submitter || submitter.disabled) return;

      const selectedFile = Array.from(form.querySelectorAll("input[type='file']")).some((input) => input.files?.length);
      const loadingText = selectedFile
        ? submitter.dataset.uploadingText || "Uploading…"
        : submitter.dataset.loadingText || "Working…";

      form.dataset.submitting = "true";
      form.setAttribute("aria-busy", "true");
      submitter.dataset.loadingOriginal = submitter.innerHTML;
      submitter.replaceChildren();
      const spinner = document.createElement("span");
      spinner.className = "button-spinner";
      spinner.setAttribute("aria-hidden", "true");
      const label = document.createElement("span");
      label.textContent = loadingText;
      submitter.append(spinner, label);
      submitter.classList.add("is-loading");
      submitter.disabled = true;
      submitter.setAttribute("aria-disabled", "true");
    });

    form.addEventListener("reset", () => restoreSubmitButton(form));
  });

  // A back/forward-cache restore should never leave controls appearing busy.
  window.addEventListener("pageshow", () => loadingForms.forEach(restoreSubmitButton));
})();
