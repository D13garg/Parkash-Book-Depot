/**
 * Google Books content script
 * Scrapes book details from books.google.com product pages.
 */

(function () {
  "use strict";

  // Only run on individual book pages
  if (!window.location.href.includes("books.google.com/books")) return;
  if (!document.querySelector(".qrShPb, #bookcover_rrsr")) return;

  // ── Helpers ────────────────────────────────────────────────────────────────

  function text(selector) {
    const el = document.querySelector(selector);
    return el ? el.textContent.trim() : "";
  }

  function metaValue(label) {
    const rows = document.querySelectorAll(".metadata_row, tr");
    for (const row of rows) {
      if (row.textContent.toLowerCase().includes(label.toLowerCase())) {
        const val = row.querySelector(".metadata_value, td:last-child, .w1Ysud");
        if (val) return val.textContent.trim();
      }
    }
    return "";
  }

  // ── Scraper ────────────────────────────────────────────────────────────────

  function scrape() {
    const title = text(".qrShPb span") || text("h1");

    // Authors
    const authorEls = document.querySelectorAll(".YMEQtf a, .Z1L9Pc a");
    const authors = [...authorEls].map((a) => a.textContent.trim()).join(", ");

    // Description
    const description =
      text("#synopsistext") ||
      text(".nv-quotes-description") ||
      text("[id*='description']");

    // Metadata table
    const publisher = metaValue("Publisher");
    const isbn = metaValue("ISBN");
    const language = metaValue("Language");
    const edition = metaValue("Edition");

    // Page count for reference (not a form field but useful)
    const pages = metaValue("Pages");

    // Categories from genre links
    const genreEls = document.querySelectorAll(".Hv4hgb a, [class*='genre'] a");
    const categories =
      [...genreEls]
        .map((a) => a.textContent.trim().toLowerCase())
        .filter(Boolean)
        .slice(0, 3)
        .join(", ") || "book";

    return {
      source: "google_books",
      title,
      authors,
      publisher,
      isbn,
      description: description.slice(0, 1000),
      language: language || "English",
      price: "",           // Google Books doesn't reliably show retail price
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
        gap: 8px;
        white-space: nowrap;
      ">
        📚 Add to Parkash Book Depot
      </button>
    `;

    btn.querySelector("button").addEventListener("click", () => {
      const data = scrape();
      if (!data.title) {
        alert("Could not scrape book title. Make sure you are on a book page.");
        return;
      }
      chrome.runtime.sendMessage({ type: "PARKASH_ADD_BOOK", data });
    });

    const anchor =
      document.querySelector(".PZPZlf") ||
      document.querySelector(".gb-button-container") ||
      document.querySelector("#bookcover_rrsr");

    if (anchor) anchor.parentNode.insertBefore(btn, anchor.nextSibling);
  }

  if (document.readyState === "complete") {
    injectButton();
  } else {
    window.addEventListener("load", injectButton);
  }
})();
