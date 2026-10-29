"use strict";
(() => {
  const payload = JSON.parse(document.getElementById("hb-payload").textContent);
  const base = payload.records;
  const clone = value => JSON.parse(JSON.stringify(value));
  const drafts = base.map(clone);
  const allowedEditable = ["reviewer_id", "review_status", "dimension_ratings", "exposure_label", "workflow_label", "rationale", "evidence_references", "context_notes", "reviewed_at_utc"];
  const $ = id => document.getElementById(id);
  let index = 0;
  let dirty = false;
  const label = value => value.replaceAll("_", " ").replace(/^./, c => c.toUpperCase());
  const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  function notify(text, error = false, id = "message") {
    $(id).textContent = text;
    $(id).className = error ? "error" : "";
  }
  function options(select, labels) {
    const empty = document.createElement("option"); empty.value = ""; empty.textContent = "Choose a judgment…"; select.append(empty);
    labels.forEach(value => { const option = document.createElement("option"); option.value = value; option.textContent = label(value); select.append(option); });
  }
  payload.dimensions.forEach(item => {
    const div = document.createElement("div"); div.className = "dimension";
    const heading = document.createElement("label"); heading.htmlFor = "dim-" + item.id; heading.textContent = label(item.id);
    const select = document.createElement("select"); select.id = "dim-" + item.id; options(select, payload.dimension_labels);
    const help = document.createElement("p"); help.className = "question"; help.textContent = item.question;
    div.append(heading, select, help); $("dimensions").append(div);
  });
  options($("exposure"), payload.exposure_labels); options($("workflow"), payload.workflow_labels);
  $("slot-badge").textContent = "Reviewer " + payload.slot + " · Offline";
  $("scenario").textContent = payload.capability_scope;
  $("source-notice").textContent = payload.source_notice;
  $("run-meta").textContent = "Run " + payload.run_id + " · " + payload.rubric_version;
  function readForm() {
    const row = drafts[index];
    if (row.review_status === "completed") return;
    payload.dimensions.forEach(item => { row.dimension_ratings[item.id] = $("dim-" + item.id).value || null; });
    row.exposure_label = $("exposure").value || null; row.workflow_label = $("workflow").value || null;
    row.rationale = $("rationale").value || null;
    row.evidence_references = $("evidence").value.split(/\r?\n/).map(value => value.trim()).filter(Boolean);
    row.context_notes = $("context").value || null;
  }
  function isDraft(row, position) { return row.review_status !== "completed" && !same(row, base[position]); }
  function renderList() {
    const query = $("search").value.toLowerCase(); const filter = $("filter").value;
    $("task-list").replaceChildren();
    drafts.forEach((row, position) => {
      const done = row.review_status === "completed";
      if (filter === "completed" && !done || filter === "unfinished" && done) return;
      if (!(row.occupation_title + " " + row.task_text + " " + row.task_id).toLowerCase().includes(query)) return;
      const button = document.createElement("button"); button.type = "button";
      button.className = "task-nav" + (position === index ? " active" : "") + (done ? " done" : "");
      button.setAttribute("aria-current", position === index ? "true" : "false");
      const status = document.createElement("span"); status.textContent = "Task " + (position + 1) + (done ? " · Completed" : isDraft(row, position) ? " · Draft" : "");
      const title = document.createElement("div"); title.textContent = row.occupation_title;
      button.append(status, title); button.addEventListener("click", () => go(position)); $("task-list").append(button);
    });
    const completed = drafts.filter(row => row.review_status === "completed").length;
    $("progress").textContent = completed + " of " + base.length;
    $("progress-bar").max = base.length; $("progress-bar").value = completed;
  }
  function render() {
    const row = drafts[index]; const done = row.review_status === "completed";
    $("task-position").textContent = "Task " + (index + 1) + " of " + base.length;
    $("task-meta").textContent = row.occupation_code + " · " + row.split;
    $("occupation-title").textContent = row.occupation_title; $("task-text").textContent = row.task_text;
    $("task-source").textContent = "Source task " + row.task_id + " · " + row.release_id;
    payload.dimensions.forEach(item => { const select = $("dim-" + item.id); select.value = row.dimension_ratings[item.id] || ""; select.disabled = done; });
    $("exposure").value = row.exposure_label || ""; $("workflow").value = row.workflow_label || "";
    $("rationale").value = row.rationale || ""; $("evidence").value = row.evidence_references.join("\n"); $("context").value = row.context_notes || "";
    ["exposure", "workflow", "rationale", "evidence", "context"].forEach(id => { $(id).disabled = done; });
    $("task-status").textContent = done ? "Completed" : isDraft(row, index) ? "Draft · not completed" : "Not completed";
    $("task-status").className = "status" + (done ? " completed" : "");
    $("complete").disabled = done; $("reopen").disabled = !done;
    $("previous").disabled = index === 0; $("next").disabled = index === base.length - 1;
    if (done) $("reviewer").value = row.reviewer_id;
    renderList();
  }
  function go(position) { readForm(); index = position; notify(""); render(); }
  $("previous").addEventListener("click", () => go(Math.max(0, index - 1)));
  $("next").addEventListener("click", () => go(Math.min(base.length - 1, index + 1)));
  $("search").addEventListener("input", renderList); $("filter").addEventListener("change", renderList);
  document.querySelector('label[for="import-file"]').addEventListener("keydown", event => {
    if (event.key === "Enter" || event.key === " ") { event.preventDefault(); $("import-file").click(); }
  });
  $("review-form").addEventListener("input", () => { readForm(); dirty = true; });
  $("review-form").addEventListener("change", () => { readForm(); dirty = true; renderList(); });
  $("review-form").addEventListener("submit", event => {
    event.preventDefault(); readForm(); const row = drafts[index];
    const reviewer = $("reviewer").value.trim();
    if (!reviewer) return notify("Enter a reviewer pseudonym before completing a task.", true);
    const other = drafts.find(value => value.review_status === "completed" && value.reviewer_id.toLowerCase() !== reviewer.toLowerCase());
    if (other) return notify("Use the same reviewer pseudonym throughout this response file.", true);
    if (Object.values(row.dimension_ratings).some(value => !value) || !row.exposure_label || !row.workflow_label) return notify("Choose every judgment. Use insufficient evidence where context is missing.", true);
    if (!row.rationale || row.rationale.trim().length < 20) return notify("Add a substantive rationale of at least 20 characters.", true);
    if (!row.evidence_references.length) return notify("Add at least one specific evidence reference.", true);
    row.reviewer_id = reviewer; row.review_status = "completed"; row.reviewed_at_utc = new Date().toISOString();
    dirty = true; render(); notify("Review completed. Download a backup to preserve it outside this tab.");
  });
  $("reopen").addEventListener("click", () => {
    drafts[index].review_status = "unreviewed"; drafts[index].reviewer_id = null; drafts[index].reviewed_at_utc = null;
    dirty = true; render(); notify("Reopened as a draft. It will stay blank in response exports until completed again.");
  });
  function download(name, data, type) {
    const url = URL.createObjectURL(new Blob([data], {type})); const anchor = document.createElement("a");
    anchor.href = url; anchor.download = name; document.body.append(anchor); anchor.click(); anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  $("export-draft").addEventListener("click", () => {
    readForm(); download("humanbridge-" + payload.run_id + "-" + payload.slot + "-draft.json", JSON.stringify({format:"humanbridge-review-draft-v1",run_id:payload.run_id,slot:payload.slot,reviewer_id:$("reviewer").value.trim(),records:drafts}, null, 2), "application/json");
    dirty = false; notify("Draft backup downloaded. It includes unfinished edits.", false, "export-message");
  });
  $("export-response").addEventListener("click", () => {
    readForm(); const responses = drafts.map((row, position) => row.review_status === "completed" ? row : base[position]);
    const count = responses.filter(row => row.review_status === "completed").length;
    download("humanbridge-" + payload.run_id + "-" + payload.slot + "-responses.jsonl", responses.map(row => JSON.stringify(row)).join("\n") + "\n", "application/x-ndjson");
    notify("Exported " + count + " completed reviews. Unfinished drafts were exported as blank records; keep a draft backup for those edits.", false, "export-message");
  });
  function validateImported(row, original, completedAllowed = true) {
    if (!row || typeof row !== "object" || Array.isArray(row) || !same(Object.keys(row).sort(), Object.keys(original).sort())) throw new Error("Imported record fields differ from this blind queue.");
    for (const key of Object.keys(original).filter(key => !allowedEditable.includes(key))) if (!same(row[key], original[key])) throw new Error("Imported source identity or task text changed.");
    if (!row.dimension_ratings || !same(Object.keys(row.dimension_ratings).sort(), payload.dimensions.map(item => item.id).sort())) throw new Error("Imported dimension fields differ.");
    for (const value of Object.values(row.dimension_ratings)) if (value !== null && !payload.dimension_labels.includes(value)) throw new Error("Invalid dimension label.");
    for (const [key, labels] of [["exposure_label",payload.exposure_labels],["workflow_label",payload.workflow_labels]]) if (row[key] !== null && !labels.includes(row[key])) throw new Error("Invalid review label.");
    if (!["unreviewed","completed"].includes(row.review_status)) throw new Error("Invalid review status.");
    for (const key of ["rationale","context_notes","reviewer_id","reviewed_at_utc"]) if (row[key] !== null && typeof row[key] !== "string") throw new Error("Invalid review text field.");
    if (!Array.isArray(row.evidence_references) || row.evidence_references.some(value => typeof value !== "string" || !value.trim())) throw new Error("Invalid evidence references.");
    if (row.review_status === "completed") {
      if (!completedAllowed || !row.reviewer_id?.trim() || !row.rationale || row.rationale.trim().length < 20 || !row.evidence_references.length || Object.values(row.dimension_ratings).some(value => value === null) || !row.exposure_label || !row.workflow_label || !row.reviewed_at_utc || !/(Z|\+00:00)$/.test(row.reviewed_at_utc) || Number.isNaN(Date.parse(row.reviewed_at_utc))) throw new Error("Incomplete completed review.");
    } else if (row.reviewer_id !== null || row.reviewed_at_utc !== null) throw new Error("A draft cannot claim a completed reviewer identity or timestamp.");
  }
  $("import-file").addEventListener("change", async event => {
    try {
      const file = event.target.files[0]; if (!file) return;
      if (file.size > 10_000_000) throw new Error("Review file exceeds the 10 MB limit.");
      const text = (await file.text()).trim(); let records; let reviewer = "";
      let packet = null;
      try { const candidate = JSON.parse(text); if (candidate?.format === "humanbridge-review-draft-v1") packet = candidate; } catch { /* JSONL is parsed below. */ }
      if (packet) {
        if (!same(Object.keys(packet).sort(), ["format","run_id","slot","reviewer_id","records"].sort())) throw new Error("Unexpected draft wrapper fields.");
        if (packet.format !== "humanbridge-review-draft-v1" || packet.run_id !== payload.run_id || packet.slot !== payload.slot || typeof packet.reviewer_id !== "string") throw new Error("Draft belongs to another run or reviewer slot.");
        records = packet.records; reviewer = packet.reviewer_id;
      } else records = text.split(/\r?\n/).filter(line => line.trim()).map(line => JSON.parse(line));
      if (!Array.isArray(records) || records.length !== base.length) throw new Error("Imported queue has missing or extra tasks.");
      const keyed = new Map(records.map(row => [row.task_key,row])); if (keyed.size !== base.length) throw new Error("Duplicate task keys.");
      const ordered = base.map(original => { const row = keyed.get(original.task_key); validateImported(row, original); return clone(row); });
      const identities = new Set(ordered.filter(row => row.review_status === "completed").map(row => row.reviewer_id.trim().toLowerCase()));
      if (identities.size > 1) throw new Error("One response file must use one reviewer pseudonym.");
      const completed = ordered.find(row => row.review_status === "completed");
      ordered.forEach((row, position) => { drafts[position] = row; }); $("reviewer").value = completed ? completed.reviewer_id : reviewer;
      dirty = true; render(); notify("Imported locally. Nothing was sent to a server.", false, "export-message");
    } catch (error) { notify(error.message, true, "export-message"); }
    finally { event.target.value = ""; }
  });
  window.addEventListener("beforeunload", event => { if (dirty) { event.preventDefault(); event.returnValue = ""; } });
  render();
})();
