const RAW_BASE = "https://raw.githubusercontent.com/cachemiao/m3u-logos/main/";
const BATCH_SIZE = 54;
const number = new Intl.NumberFormat("zh-CN");

const search = document.querySelector("#search");
const grid = document.querySelector("#grid");
const results = document.querySelector("#results");
const message = document.querySelector("#message");
const pagination = document.querySelector("#pagination");
const more = document.querySelector("#more");
const template = document.querySelector("#card");
const categories = document.querySelector(".categories");
const detail = document.querySelector("#detail");
const detailCopy = document.querySelector("#detail-copy");
const manual = document.querySelector("#manual");
const manualUrl = document.querySelector("#manual-url");
const copyStatus = document.querySelector("#copy-status");
const copyTimers = new WeakMap();

let entries = [];
let matches = [];
let category = "all";
let rendered = 0;
let searchTimer;
let loaded = false;
let composing = false;

function normalize(value) {
  return value.normalize("NFKC").trim().toLowerCase().replaceAll("ß", "ss").replaceAll("ς", "σ");
}

function compact(value) {
  return value.replace(/[\p{P}\p{Z}\s]/gu, "");
}

function prepare(logo) {
  const segments = logo.path.replace(/^\/+/, "").split("/");
  const encoded = segments.map(encodeURIComponent).join("/");
  const file = segments.at(-1);
  const terms = [logo.name, file, logo.category, ...logo.aliases].map(normalize);
  return { logo, file, terms, compactTerms: terms.map(compact), local: "./" + encoded, raw: RAW_BASE + encoded };
}

function setImage(container, entry) {
  const image = container.querySelector("img");
  const placeholder = container.querySelector(".unavailable");
  image.hidden = false;
  placeholder.hidden = true;
  image.onerror = () => {
    image.hidden = true;
    placeholder.hidden = false;
  };
  image.src = entry.local;
}

async function copyUrl(url, button) {
  try {
    await navigator.clipboard.writeText(url);
  } catch {
    manualUrl.value = url;
    if (!manual.open) manual.showModal();
    manualUrl.focus();
    manualUrl.select();
    manualUrl.setSelectionRange(0, url.length);
    return;
  }
  if (!button.isConnected || (button === detailCopy && detailCopy.dataset.url !== url)) return;
  clearTimeout(copyTimers.get(button));
  button.textContent = "Copied!";
  copyStatus.textContent = "已复制原图链接";
  copyTimers.set(button, setTimeout(() => {
    button.textContent = "Copy URL";
    copyStatus.textContent = "";
  }, 1800));
}

function detailField(field, value) {
  const element = document.querySelector("#detail-" + field);
  element.textContent = value;
  element.hidden = element.previousElementSibling.hidden = !value;
}

function showDetails(entry) {
  const { logo, file, local, raw } = entry;
  setImage(detail.querySelector(".detail-image"), entry);
  detail.querySelector("#detail-title").textContent = logo.name;
  detailField("category", logo.category === "tv" ? "TV · 电视" : "Radio · 广播");
  detailField("file", file);
  detailField("size", logo.width + " × " + logo.height);
  detailField("source", logo.source);
  detailField("usage", logo.usage);

  detail.querySelector("#detail-url").value = raw;
  detail.querySelector("#original").href = raw;
  const download = detail.querySelector("#download");
  download.href = local;
  download.download = file;
  detailCopy.dataset.url = raw;
  clearTimeout(copyTimers.get(detailCopy));
  detailCopy.textContent = "Copy URL";
  detail.showModal();
}

function makeCard(entry) {
  const card = template.content.firstElementChild.cloneNode(true);
  const preview = card.querySelector(".preview");
  preview.href = entry.raw;
  preview.setAttribute("aria-label", "打开原图（新标签页） · " + entry.logo.name);
  setImage(preview, entry);
  const name = card.querySelector(".name");
  name.textContent = entry.logo.name;
  name.title = entry.logo.name;
  name.addEventListener("click", () => showDetails(entry));
  const copy = card.querySelector(".copy");
  copy.setAttribute("aria-label", "Copy URL · " + entry.logo.name);
  copy.addEventListener("click", () => copyUrl(entry.raw, copy));
  return card;
}

function appendBatch(focusNew = false) {
  if (rendered >= matches.length) return;
  const next = matches.slice(rendered, rendered + BATCH_SIZE);
  grid.append(...next.map(makeCard));
  rendered += next.length;
  pagination.hidden = rendered >= matches.length;
  if (focusNew || (pagination.hidden && document.activeElement === more)) {
    grid.children[rendered - next.length].querySelector(".name").focus();
  }
}

function filter() {
  clearTimeout(searchTimer);
  if (!loaded) return;
  const tokens = normalize(search.value).split(/\s+/).filter(Boolean).map(value => [value, compact(value)]);
  matches = entries.filter(entry =>
    (category === "all" || category === entry.logo.category) &&
    tokens.every(([value, joined]) => entry.terms.some(term => term.includes(value)) ||
      (joined && entry.compactTerms.some(term => term.includes(joined))))
  );
  grid.replaceChildren();
  rendered = 0;
  results.textContent = number.format(matches.length) + " 个台标";
  message.textContent = "没有匹配的台标，请试试其他关键词或切换分类。";
  message.hidden = matches.length > 0;
  pagination.hidden = true;
  appendBatch();
}

function queueSearch() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(filter, 140);
}

search.addEventListener("compositionstart", () => {
  composing = true;
  clearTimeout(searchTimer);
});
search.addEventListener("compositionend", () => {
  composing = false;
  queueSearch();
});
search.addEventListener("input", () => {
  if (!composing) queueSearch();
});
categories.addEventListener("click", event => {
  const button = event.target.closest("button[data-category]");
  if (!button || category === button.dataset.category) return;
  category = button.dataset.category;
  for (const item of categories.querySelectorAll("button")) {
    item.setAttribute("aria-pressed", String(item === button));
  }
  filter();
});
more.addEventListener("click", () => appendBatch(document.activeElement === more));
if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting) appendBatch();
  }, { rootMargin: "160px" });
  observer.observe(pagination);
}

detailCopy.addEventListener("click", () => copyUrl(detailCopy.dataset.url, detailCopy));
detail.querySelector("#detail-url").addEventListener("focus", event => event.target.select());

async function loadCatalog() {
  try {
    const response = await fetch("./api/v1/logos.json");
    if (!response.ok) throw new Error("Catalog request failed: " + response.status);
    const data = await response.json();
    if (!Array.isArray(data.logos)) throw new Error("Invalid catalog");
    entries = data.logos.map(prepare);
    const tv = entries.filter(entry => entry.logo.category === "tv").length;
    document.querySelector("#tv-total").textContent = number.format(tv);
    document.querySelector("#radio-total").textContent = number.format(entries.length - tv);
    loaded = true;
    filter();
  } catch (error) {
    console.error(error);
    results.textContent = "加载失败";
    message.textContent = "暂时无法加载台标，请刷新页面重试。";
    message.hidden = false;
  }
}

loadCatalog();
