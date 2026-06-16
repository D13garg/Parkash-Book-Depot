/**
 * Flipkart content script
 * Scrapes book details from flipkart.com book product pages.
 */

(function () {
  "use strict";

  // Only run on product pages
  if (!document.querySelector(".B_NuCI, ._35KyD6")) return;

  // ── Helpers ────────────────────────────────────────────────────────────────

  function text(selector) {
    const el = document.querySelector(selector);
    return el ? el.textContent.trim() : "";
  }

  function specValue(label) {
    const rows = document.querySelectorAll("._14cfVK, .RmoJze, table tr");
    for (const row of rows) {
      const t = row.textContent;
      if (t.toLowerCase().includes(label.toLowerCase())) {
        const val = row.querySelector("._21lJbe, td:last-child, ._3bB6-d");
        if (val) return val.textContent.trim();
      }
    }
    return "";
  }

  // ── Scraper ────────────────────────────────────────────────────────────────

  function scrape() {
    const title = text(".B_NuCI") || text("._35KyD6") || text("h1");

    // Authors from spec table
    const authors = specValue("Author") || specValue("Authors");

    // Price — Flipkart shows ₹ separated from digits sometimes
    const priceEl = document.querySelector("._30jeq3, ._16Jk6d");
    const priceRaw = priceEl
      ? priceEl.textContent.replace(/[₹,\s]/g, "").trim()
      : "";

    // Description
    const description =
      text("._1AN87F div, .block-content, ._3WLfl4") ||
      text("[class*='description']");

    // Spec table values
    const publisher = specValue("Publisher") || specValue("Publication");
    const isbn = specValue("ISBN") || specValue("ISBN-13") || specValue("ISBN-10");
    const language = specValue("Language");
    const edition = specValue("Edition");

    // Categories from breadcrumb
    const breadcrumbs = [
      ...document.querySelectorAll("._3GnUzp a, ._1pckTg a"),
    ]
      .map((a) => a.textContent.trim().toLowerCase())
      .filter((b) => b && !["home", "flipkart"].includes(b));
    const categories = breadcrumbs.slice(0, 3).join(", ") || "book";

    return {
      source: "flipkart",
      title,
      authors,
      publisher,
      isbn,
      description: description.slice(0, 1000),
      language: language || "English",
      price: priceRaw,
      categories,
      edition,
    };
  }

  // ── Button injection ───────────────────────────────────────────────────────

  function injectButton() {
    if (document.getElementById("parkash-add-btn")) return;

    const btn = document.createElement("div");
    btn.id = "parkash-add-btn";
    btn.style.cssText = "margin-top:12px;";
    btn.innerHTML = `
      <button style="
        width: 100%;
        padding: 10px 18px;
        background: #f59e0b;
        color: #000;
        font-weight: 700;
        font-size: 14px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-family: system-ui, sans-serif;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
      ">
        📚 Add to Parkash Book Depot
      </button>
    `;

    btn.querySelector("button").addEventListener("click", () => {
      const data = scrape();
      if (!data.title) {
        alert("Could not scrape book title. Make sure you are on a book product page.");
        return;
      }
      chrome.runtime.sendMessage({ type: "PARKASH_ADD_BOOK", data });
    });

    const anchor =
      document.querySelector("._3Ckfv5") ||
      document.querySelector("._3pPFEf") ||
      document.querySelector("[class*='_2kHMtA']");

    if (anchor) anchor.parentNode.insertBefore(btn, anchor.nextSibling);
  }

  if (document.readyState === "complete") {
    injectButton();
  } else {
    window.addEventListener("load", injectButton);
  }
})();
