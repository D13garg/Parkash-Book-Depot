/**
 * Background service worker
 *
 * Receives scraped book data from content scripts via chrome.runtime.onMessage,
 * then opens (or focuses) the Parkash Book Depot admin Add Book page with the
 * data encoded as URL search params.
 *
 * The autofill.js content script on the dashboard reads those params and fills
 * the form automatically.
 */

// Default dashboard URL — overridable via extension storage
const DEFAULT_DASHBOARD = "https://parkash-book-depot.vercel.app";

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type !== "PARKASH_ADD_BOOK") return;

  const data = message.data;

  // Encode all fields as URL params
  const params = new URLSearchParams();
  if (data.title)       params.set("title",       data.title);
  if (data.authors)     params.set("authors",     data.authors);     // comma separated string
  if (data.publisher)   params.set("publisher",   data.publisher);
  if (data.isbn)        params.set("isbn",         data.isbn);
  if (data.description) params.set("description", data.description);
  if (data.language)    params.set("language",    data.language);
  if (data.price)       params.set("price",       data.price);
  if (data.categories)  params.set("categories",  data.categories);  // comma separated string
  if (data.edition)     params.set("edition",     data.edition);
  params.set("source", data.source || "extension");

  // Read saved dashboard URL from storage (admin may have a custom deployment)
  chrome.storage.sync.get({ dashboardUrl: DEFAULT_DASHBOARD }, ({ dashboardUrl }) => {
    const addBookUrl = `${dashboardUrl.replace(/\/$/, "")}/admin/books/add?${params.toString()}`;

    // If the Add Book page is already open — focus it and reload with new params
    chrome.tabs.query({ url: `${dashboardUrl.replace(/\/$/, "")}/*` }, (tabs) => {
      const existing = tabs.find((t) => t.url?.includes("/admin/books/add"));
      if (existing?.id) {
        chrome.tabs.update(existing.id, { url: addBookUrl, active: true });
      } else {
        chrome.tabs.create({ url: addBookUrl });
      }
    });
  });

  sendResponse({ ok: true });
  return true; // keep channel open for async sendResponse
});
