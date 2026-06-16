/**
 * Amazon India content script
 * Scrapes book details from amazon.in product pages and injects the
 * "Add to Parkash" button below the Add to Cart button.
 */

(function () {
  "use strict";

  // Only run on book product pages
  if (!document.querySelector("#productTitle")) return;

  // ── Helpers ────────────────────────────────────────────────────────────────

  function text(selector) {
    const el = document.querySelector(selector);
    return el ? el.textContent.trim() : "";
  }

  function tableValue(label) {
    const rows = document.querySelectorAll(
      "#detailBullets_feature_div li, #productDetails_techSpec_section_1 tr, #productDetails_detailBullets_sections1 tr"
    );
    for (const row of rows) {
      const rowText = row.textContent;
      if (rowText.toLowerCase().includes(label.toLowerCase())) {
        const valueEl = row.querySelector("span:last-child, td:last-child");
        if (valueEl) return valueEl.textContent.replace(/[\u200e\u200f]/g, "").trim();
      }
    }
    return "";
  }

  // ── Scraper ────────────────────────────────────────────────────────────────

  function scrape() {
    const title = text("#productTitle");

    // Authors — byline has "by Author1, Author2"
    const bylineEl = document.querySelector("#bylineInfo");
    const authorsRaw = bylineEl
      ? [...bylineEl.querySelectorAll(".author .contributorNameID, .author a")]
          .map((a) => a.textContent.trim())
          .filter(Boolean)
          .join(", ")
      : "";

    // Price — strip ₹ symbol and commas
    const priceRaw = text(".a-price-whole").replace(/[,₹]/g, "").trim()
      || text("#price").replace(/[,₹]/g, "").trim();

    // Description
    const descEl = document.querySelector(
      "#bookDescription_feature_div noscript, #bookDescription_feature_div .a-expander-content"
    );
    const description = descEl ? descEl.textContent.trim() : "";

    // Table values
    const publisher = tableValue("Publisher") || tableValue("Brand");
    const isbn = tableValue("ISBN-13") || tableValue("ISBN-10");
    const language = tableValue("Language");
    const edition = tableValue("Edition") || tableValue("Item model number");

    // Categories from breadcrumb
    const breadcrumbs = [...document.querySelectorAll("#wayfinding-breadcrumbs_feature_div a")]
      .map((a) => a.textContent.trim().toLowerCase())
      .filter((b) => b && b !== "books");
    const categories = breadcrumbs.slice(0, 3).join(", ") || "book";

    return {
      source: "amazon",
      title,
      authors: authorsRaw,
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
    btn.innerHTML = `
      <button style="
        width: 100%;
        padding: 10px 18px;
        margin-top: 10px;
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
        transition: opacity 0.2s;
      " onmouseover="this.style.opacity=0.85" onmouseout="this.style.opacity=1">
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

    // Insert after the add-to-cart button area
    const anchor =
      document.querySelector("#addToCart_feature_div") ||
      document.querySelector("#buy-now-button") ||
      document.querySelector("#rightCol");

    if (anchor) anchor.appendChild(btn);
  }

  // Wait for the buy box to be rendered
  if (document.readyState === "complete") {
    injectButton();
  } else {
    window.addEventListener("load", injectButton);
  }
})();
