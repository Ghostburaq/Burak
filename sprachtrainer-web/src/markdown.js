// Kleiner Markdown-Renderer: escaped zuerst alles, erlaubt dann nur
// Überschriften, fett, kursiv, durchgestrichen, Code, Listen, Tabellen.
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

function inline(s) {
  return esc(s)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/~~([^~]+)~~/g, "<del>$1</del>")
    .replace(/(^|[^*\w])\*([^*\s][^*]*)\*(?!\w)/g, "$1<em>$2</em>");
}

const cells = (row) => row.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());

export function md(src) {
  const lines = src.replace(/\r/g, "").split("\n");
  const out = [];
  let list = null;
  let para = [];
  const flushPara = () => { if (para.length) { out.push(`<p>${para.map(inline).join("<br>")}</p>`); para = []; } };
  const flushList = () => { if (list) { out.push(`</${list}>`); list = null; } };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/^\s*\|.*\|\s*$/.test(line) && /^\s*\|?[\s:|-]+\|?\s*$/.test(lines[i + 1] || "") && lines[i + 1].includes("-")) {
      flushPara(); flushList();
      const head = cells(line);
      i += 1;
      const rows = [];
      while (i + 1 < lines.length && /^\s*\|.*\|\s*$/.test(lines[i + 1])) rows.push(cells(lines[++i]));
      out.push(`<div class="tbl"><table><thead><tr>${head.map((c) => `<th>${inline(c)}</th>`).join("")}</tr></thead><tbody>${rows.map((r) => `<tr>${r.map((c) => `<td>${inline(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`);
      continue;
    }
    let m;
    if ((m = /^(#{1,4})\s+(.*)$/.exec(line))) {
      flushPara(); flushList();
      const n = Math.min(m[1].length + 2, 5);
      out.push(`<h${n}>${inline(m[2])}</h${n}>`);
    } else if (/^\s*(---|\*\*\*)\s*$/.test(line)) {
      flushPara(); flushList(); out.push("<hr>");
    } else if ((m = /^\s*[-*•]\s+(.*)$/.exec(line))) {
      flushPara();
      if (list !== "ul") { flushList(); out.push("<ul>"); list = "ul"; }
      out.push(`<li>${inline(m[1])}</li>`);
    } else if ((m = /^\s*\d+[.)]\s+(.*)$/.exec(line))) {
      flushPara();
      if (list !== "ol") { flushList(); out.push("<ol>"); list = "ol"; }
      out.push(`<li>${inline(m[1])}</li>`);
    } else if ((m = /^\s*>\s?(.*)$/.exec(line))) {
      flushPara(); flushList(); out.push(`<blockquote>${inline(m[1])}</blockquote>`);
    } else if (!line.trim()) {
      flushPara(); flushList();
    } else {
      flushList(); para.push(line);
    }
  }
  flushPara(); flushList();
  return out.join("");
}

// Für die Sprachausgabe: Markdown-Zeichen entfernen.
export function plain(src) {
  return src
    .replace(/~~[^~]+~~/g, "")
    .replace(/[*_`#>|]/g, " ")
    .replace(/^\s*[-•]\s+/gm, "")
    .replace(/\s+/g, " ")
    .trim();
}
