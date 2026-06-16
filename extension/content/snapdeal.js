/**
 * Snapdeal content script
 * Scrapes book details from snapdeal.com book product pages.
 */

(function () {
  "use strict";

  // Only run on product pages
  if (!document.querySelector(".pdp-e-i-head, .buy-box")) return;

  // ── Helpers ────────────────────────────────────────────────────────────────

  function text(selector) {
    const el = document.querySelector(selector);
    return el ? el.textContent.trim() : "";
  }

  function specValue(label) {
    const rows = document.querySelectorAll(
      ".spec-body tr, .product-spec tr, [class*='spec'] tr"
    );
    for (const row of rows) {
      if (row.textContent.toLowerCase().includes(label.toLowerCase())) {
        const val = row.querySelector("td:last-child, .spec-value");
        if (val) return val.textContent.trim();
      }
    }
    // Also check definition lists
    const dls = document.querySelectorAll("dl dt");
    for (const dt of dls) {
      if (dt.textContent.toLowerCase().includes(label.toLowerCase())) {
        const dd = dt.nextElementSibling;
        if (dd) return dd.textContent.trim();
      }
    }
    return "";
  }

  // ── Scraper ────────────────────────────────────────────────────────────────

  function scrape() {
    const title = text(".pdp-e-i-head") || text("h1");

    // Authors
    const authors =
      specValue("Author") ||
      specValue("Writer") ||
      text(".seller-name a");

    // Price
    const priceRaw = text("._1vC4OE, .payBlkBig, .price-val")
      .replace(/[₹,\s]/g, "")
      .trim();

    // Description
    const description =
      text(".pdp-description-details, .product-desc-rating, [class*='description']");

    // Spec values
    const publisher = specValue("Publisher") || specValue("Brand") || specValue("Manufacturer");
    const isbn = specValue("ISBN") || specValue("ISBN-13");
    const language = specValue("Language");
    const edition = specValue("Edition");

    // Categories from breadcrumb
    const breadcrumbs = [...document.querySelectorAll(".breadcrumb a, .breadCrumbWrapper a")]
      .map((a) => a.textContent.trim().toLowerCase())
      .filter((b) => b && !["home", "snapdeal"].includes(b));
    const categories = breadcrumbs.slice(0, 3).join(", ") || "book";

    return {
      source: "snapdeal",
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
      document.querySelector(".buy-box") ||
      document.querySelector(".add-to-cart-container") ||
      document.querySelector(".product-buy");

    if (anchor) anchor.appendChild(btn);
  }

  if (document.readyState === "complete") {
    injectButton();
  } else {
    window.addEventListener("load", injectButton);
  }
})();
