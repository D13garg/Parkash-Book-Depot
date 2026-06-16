/**
 * Autofill script — injected on /admin/books/add
 *
 * Reads URL params set by background.js and fills every form field.
 * Uses a MutationObserver + retry loop because React renders the form
 * asynchronously — the inputs may not exist immediately on page load.
 *
 * Also dispatches React-compatible input events so React Hook Form
 * registers the values correctly (plain value assignment isn't enough).
 */

(function () {
  "use strict";

  const params = new URLSearchParams(window.location.search);

  // Only run if the URL contains at least a title param from our extension
  if (!params.get("title") && !params.get("source")) return;

  // ── Field map: URL param → input label text or placeholder ────────────────
  const FIELD_MAP = {
    title:               { label: "Title" },
    authors:             { label: "Authors", placeholder: "Author 1, Author 2" },
    categories:          { label: "Categories", placeholder: "textbook, science" },
    price:               { label: "Price" },
    publisher:           { label: "Publisher" },
    isbn:                { label: "ISBN" },
    description:         { label: "Description", isTextarea: true },
    language:            { label: "Language" },
    edition:             { label: "Edition" },
    low_stock_threshold: { label: "Low Stock Alert" },
  };

  // ── React-compatible value setter ─────────────────────────────────────────
  function setNativeValue(el, value) {
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
      el.tagName === "TEXTAREA"
        ? window.HTMLTextAreaElement.prototype
        : window.HTMLInputElement.prototype,
      "value"
    ).set;
    nativeInputValueSetter.call(el, value);
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
  }

  // ── Find input by label text ───────────────────────────────────────────────
  function findInput(fieldKey, isTextarea) {
    const field = FIELD_MAP[fieldKey];
    if (!field) return null;

    // Try finding by associated label text
    const labels = document.querySelectorAll("label");
    for (const label of labels) {
      if (label.textContent.trim().startsWith(field.label)) {
        // label[for] → input[id]
        if (label.htmlFor) {
          const el = document.getElementById(label.htmlFor);
          if (el) return el;
        }
        // label wraps the input
        const el = label.querySelector(isTextarea ? "textarea" : "input");
        if (el) return el;
        // sibling input
        const sibling = label.nextElementSibling;
        if (sibling && (sibling.tagName === "INPUT" || sibling.tagName === "TEXTAREA")) {
          return sibling;
        }
      }
    }

    // Fallback: match by placeholder
    if (field.placeholder) {
      const el = document.querySelector(`[placeholder="${field.placeholder}"]`);
      if (el) return el;
    }

    return null;
  }

  // ── Main fill function ────────────────────────────────────────────────────
  function fillForm() {
    let filled = 0;

    for (const [param, fieldDef] of Object.entries(FIELD_MAP)) {
      const value = params.get(param);
      if (!value) continue;

      const el = findInput(param, fieldDef.isTextarea);
      if (!el) continue;

      setNativeValue(el, value);
      filled++;
    }

    return filled;
  }

  // ── Wait for React to render the form ────────────────────────────────────
  // React mounts the form asynchronously. Retry up to 20 times (2 seconds).

  let attempts = 0;
  const MAX_ATTEMPTS = 20;

  function tryFill() {
    attempts++;
    const filled = fillForm();

    if (filled > 0) {
      // Show a subtle banner so the admin knows fields were pre-filled
      showBanner(filled);
      return;
    }

    if (attempts < MAX_ATTEMPTS) {
      setTimeout(tryFill, 100);
    }
  }

  function showBanner(count) {
    if (document.getElementById("parkash-autofill-banner")) return;

    const source = params.get("source") || "extension";
    const sourceLabel = {
      amazon: "Amazon India",
      flipkart: "Flipkart",
      google_books: "Google Books",
      snapdeal: "Snapdeal",
    }[source] || source;

    const banner = document.createElement("div");
    banner.id = "parkash-autofill-banner";
    banner.style.cssText = `
      position: fixed;
      top: 16px;
      right: 16px;
      z-index: 9999;
      background: #f59e0b;
      color: #000;
      padding: 12px 18px;
      border-radius: 10px;
      font-family: system-ui, sans-serif;
      font-size: 14px;
      font-weight: 600;
      box-shadow: 0 4px 16px rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      gap: 8px;
      max-width: 320px;
    `;
    banner.innerHTML = `
      <span>📚</span>
      <span>${count} field${count !== 1 ? "s" : ""} pre-filled from ${sourceLabel}. Review and click Add Book.</span>
      <button onclick="this.parentNode.remove()" style="
        margin-left:8px; background:none; border:none;
        cursor:pointer; font-size:16px; line-height:1;
      ">×</button>
    `;
    document.body.appendChild(banner);

    // Auto-dismiss after 6 seconds
    setTimeout(() => banner.remove(), 6000);
  }

  // Start trying after a short initial delay to let React hydrate
  setTimeout(tryFill, 300);
})();
