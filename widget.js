/* First Church of the Nazarene, Mount Vernon: interactive sermon notes widget.
   The layout and behavior live here and rarely change.
   Each week's sermon lives in content.json next to this file. */
(function () {
  var script = document.currentScript ||
    document.querySelector('script[src*="sermon-notes/widget.js"]') ||
    document.querySelector('script[src*="widget.js"]');
  var base = script.src.replace(/[^/]*$/, "");
  var root = document.getElementById("bb-week-root");
  if (!root) {
    root = document.createElement("div");
    root.id = "bb-week-root";
    script.parentNode.insertBefore(root, script);
  }
  root.className = "bb-week";

  var TEMPLATE = "  <style>\n    #bb-week-root {\n      --bb-accent: #14141A;   /* <- change this one value to match your brand color */\n      --bb-ink-soft: #68686F;\n      --bb-line: #E1E1E4;\n      --bb-fill-bg: rgba(0,0,0,0.025);\n\n      max-width: 640px;\n      margin: 0 auto;\n      padding: 12px 20px 64px;\n      background: transparent;\n      color: inherit;\n      font-family: inherit;\n      line-height: 1.5;\n      text-align: left;\n      box-sizing: border-box;\n    }\n    #bb-week-root * { box-sizing: border-box; font-family: inherit; }\n\n    #bb-week-root h1, #bb-week-root h2, #bb-week-root h3 {\n      font-weight: 700;\n      margin: 0;\n      color: inherit;\n      letter-spacing: -0.01em;\n    }\n\n    /* Header */\n    .bb-header { margin-bottom: 8px; }\n    .bb-series { font-size: 13px; color: var(--bb-accent); font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }\n    .bb-meta { font-size: 13px; color: var(--bb-ink-soft); margin-top: 3px; }\n    .bb-title { font-size: 34px; margin-top: 10px; line-height: 1.12; letter-spacing: -0.02em; }\n    .bb-scripture { font-size: 15px; color: var(--bb-ink-soft); margin-top: 6px; }\n\n    .bb-blocks-title { font-size: 17px; margin: 28px 0 12px; }\n    .bb-blocks-list {\n      list-style: decimal;\n      margin: 0 0 34px;\n      padding: 16px 18px 16px 40px;\n      background: var(--bb-fill-bg);\n      border-left: 3px solid var(--bb-accent);\n      font-size: 15px;\n    }\n    .bb-blocks-list li { padding: 4px 0; }\n\n    .bb-rule { border: none; border-top: 1px solid var(--bb-line); margin: 36px 0; }\n\n    /* Outline */\n    .bb-outline-title { font-size: 21px; }\n    .bb-outline-ref { font-size: 13px; color: var(--bb-ink-soft); margin: 5px 0 18px; }\n    .bb-point { margin-bottom: 16px; }\n    .bb-point-head { display: flex; justify-content: space-between; gap: 12px; font-size: 16px; font-weight: 700; }\n    .bb-point-ref { color: var(--bb-ink-soft); font-weight: 400; font-size: 13px; white-space: nowrap; }\n    .bb-subpoints { margin: 12px 0 0 4px; padding-left: 16px; border-left: 2px solid var(--bb-line); }\n    .bb-subpoint { margin-bottom: 12px; font-size: 15px; }\n    .bb-subpoint-title { font-weight: 700; }\n    .bb-subpoint-detail { color: var(--bb-ink-soft); font-size: 13px; margin-top: 3px; }\n    .bb-subpoint-detail::before { content: \"\\2192\\00a0\"; color: var(--bb-accent); font-weight: 700; }\n\n    /* Inline fill-in blank (for underlined words in the source notes) */\n    .bb-blank {\n      display: inline-block;\n      min-width: 70px;\n      padding: 0 3px 1px;\n      border-bottom: 1.5px solid var(--bb-ink-soft);\n      outline: none;\n      color: inherit;\n    }\n    .bb-blank:focus { border-bottom-color: var(--bb-accent); }\n    .bb-blank:empty::before { content: \"\\00a0\"; }\n\n    /* Box-style fill-in areas (for discussion answers and free notes) */\n    .bb-fill {\n      min-height: 44px;\n      margin-top: 7px;\n      padding: 11px 13px;\n      background: var(--bb-fill-bg);\n      border: 1px solid var(--bb-line);\n      border-radius: 2px;\n      font-size: 15px;\n      color: inherit;\n      outline: none;\n    }\n    .bb-fill:focus { border-color: var(--bb-accent); }\n    .bb-fill:empty::before {\n      content: attr(data-placeholder);\n      color: #999;\n    }\n    .bb-fill.bb-fill-tall { min-height: 90px; }\n\n    /* Discussion sections */\n    .bb-section-title { font-size: 19px; }\n    .bb-discussion-title { font-size: 17px; }\n    .bb-section-intro { font-size: 13px; color: var(--bb-ink-soft); margin: 6px 0 16px; }\n    .bb-question { margin-bottom: 18px; }\n    .bb-question-text { font-size: 15px; margin-bottom: 5px; }\n\n    /* Actions */\n    .bb-actions {\n      display: flex;\n      gap: 10px;\n      margin-top: 40px;\n      padding-top: 22px;\n      border-top: 1px solid var(--bb-line);\n    }\n    .bb-btn {\n      font-size: 14px;\n      font-weight: 700;\n      padding: 11px 20px;\n      border-radius: 2px;\n      border: 1px solid var(--bb-accent);\n      background: var(--bb-accent);\n      color: #fff;\n      cursor: pointer;\n      text-align: left;\n      letter-spacing: 0.01em;\n    }\n    .bb-btn.bb-btn-secondary {\n      background: transparent;\n      color: var(--bb-accent);\n    }\n    .bb-btn:hover { opacity: 0.85; }\n    .bb-hint {\n      font-size: 13px;\n      font-weight: 600;\n      color: #B3241C;\n      margin-top: 16px;\n      padding: 10px 14px;\n      border: 1.5px solid #B3241C;\n      border-radius: 2px;\n    }\n\n    @media (max-width: 480px) {\n      #bb-week-root { padding: 12px 14px 44px; }\n      .bb-title { font-size: 26px; }\n      .bb-actions { flex-direction: column; }\n      .bb-btn { width: 100%; }\n    }\n\n    /* Print \u2014 mimics the original sermon-notes document layout */\n    @media print {\n      #bb-week-root {\n        --bb-ink-soft: #000;\n        --bb-accent: #000;\n        --bb-line: #000;\n        background: #fff;\n        padding: 0;\n        max-width: 100%;\n        color: #000;\n        font-family: Georgia, \"Times New Roman\", Times, serif;\n      }\n      .bb-actions, .bb-hint { display: none; }\n\n      /* Empty fields print truly blank, never showing placeholder text */\n      .bb-fill { background: #fff; border: 1px solid #999; }\n      .bb-fill:empty::before { content: \"\"; }\n      .bb-blank:empty::before { content: \"\\00a0\"; }\n\n      /* Two-column letterhead: scripture left, series/date/title stacked right */\n      .bb-header {\n        display: grid;\n        grid-template-columns: 1fr auto;\n        column-gap: 24px;\n        margin-bottom: 4px;\n      }\n      .bb-scripture { grid-column: 1; grid-row: 1 / span 3; font-size: 15px; margin: 0; font-style: normal; }\n      .bb-series { grid-column: 2; grid-row: 1; text-align: right; font-size: 20px; text-transform: none; letter-spacing: normal; }\n      .bb-meta { grid-column: 2; grid-row: 2; text-align: right; font-size: 13px; margin-top: 2px; }\n      .bb-title { grid-column: 2; grid-row: 3; text-align: right; font-size: 15px; font-weight: 400; margin-top: 2px; letter-spacing: normal; }\n\n      .bb-blocks-title { font-size: 16px; margin: 20px 0 8px; }\n      .bb-blocks-list {\n        background: transparent;\n        border-left: none;\n        padding: 0 0 0 24px;\n        margin: 0 0 20px;\n      }\n\n      .bb-blank { border-bottom-color: #000; }\n\n      .bb-subpoint-detail { color: #000; }\n      .bb-outline-ref { color: #000; }\n\n      /* Discussion guide starts on its own page, like the source doc */\n      .bb-rule { break-before: page; border-top: none; margin: 0 0 24px; }\n      .bb-discussion-title::before { content: \"\\2610\\00a0\\00a0\"; }\n\n      .bb-question, .bb-point { break-inside: avoid; }\n    }\n  </style>\n\n<div class=\"bb-header\">\n    <div class=\"bb-series\" data-bind=\"series\"></div>\n    <div class=\"bb-meta\" data-bind=\"weekDate\"></div>\n    <h1 class=\"bb-title\" data-bind=\"sermonTitle\"></h1>\n    <div class=\"bb-scripture\" data-bind=\"scripture\"></div>\n  </div>\n\n  <h2 class=\"bb-blocks-title\" data-bind=\"buildingBlocksTitle\"></h2>\n  <ol class=\"bb-blocks-list\" data-bind=\"buildingBlocks\"></ol>\n\n  <div data-bind=\"outline\"></div>\n\n  <hr class=\"bb-rule\">\n\n  <h2 class=\"bb-section-title\" style=\"margin-bottom:4px;\">Small group discussion</h2>\n  <div class=\"bb-section-intro\" style=\"margin-bottom:18px;\">Fill in your answers below, then print or download to keep them.</div>\n\n  <div data-bind=\"discussion\"></div>\n\n  <div class=\"bb-actions\">\n    <button class=\"bb-btn\" data-action=\"print\">Print</button>\n    <button class=\"bb-btn bb-btn-secondary\" data-action=\"download\">Download PDF</button>\n  </div>\n  <div class=\"bb-hint\">Nothing here is saved automatically \u2014 print or download before you close this page.</div>";

  // Bust caches every 5 minutes so a new week shows up quickly.
  var stamp = Math.floor(Date.now() / 300000);
  // data-content lets the preview page load next week's draft instead.
  var contentUrl = new URL(script.getAttribute("data-content") || "content.json", base).href;
  fetch(contentUrl + "?v=" + stamp)
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (content) { root.innerHTML = TEMPLATE; render(content, root); })
    .catch(function () {
      root.innerHTML = '<p style="text-align:center;color:#68686F">Sermon notes could not load. Please refresh the page.</p>';
    });

  function render(content, root) {
    // ============================================================
    // TEMPLATE — builds the page from the content object above.
    // ============================================================

    

    function el(tag, props, children) {
      const node = document.createElement(tag);
      if (props) Object.assign(node, props);
      (children || []).forEach(c => c && node.appendChild(c));
      return node;
    }

    function blank() {
      return el("span", { className: "bb-blank", contentEditable: "true" });
    }

    // Splits a "{blank}" template string into text nodes and fill-in
    // blank spans, and appends them to container in order.
    function appendTemplate(container, template) {
      const parts = template.split("{blank}");
      parts.forEach((part, i) => {
        if (part) container.appendChild(document.createTextNode(part));
        if (i < parts.length - 1) container.appendChild(blank());
      });
    }

    function fillBox(placeholder, tall) {
      const box = el("div", {
        className: "bb-fill" + (tall ? " bb-fill-tall" : ""),
        contentEditable: "true"
      });
      box.setAttribute("data-placeholder", placeholder);
      return box;
    }

    // Header fields
    root.querySelector('[data-bind="series"]').textContent = content.series;
    root.querySelector('[data-bind="weekDate"]').textContent = content.weekDate;
    root.querySelector('[data-bind="sermonTitle"]').textContent = content.sermonTitle;
    root.querySelector('[data-bind="scripture"]').textContent = content.scripture;

    const blocksTitleEl = root.querySelector('[data-bind="buildingBlocksTitle"]');
    const blocksList = root.querySelector('[data-bind="buildingBlocks"]');
    if (content.buildingBlocks && content.buildingBlocks.length) {
      blocksTitleEl.textContent = content.buildingBlocksTitle;
      content.buildingBlocks.forEach(template => {
        const li = el("li");
        appendTemplate(li, template);
        blocksList.appendChild(li);
      });
    } else {
      blocksTitleEl.style.display = "none";
      blocksList.style.display = "none";
    }

    // Outline
    const outlineWrap = root.querySelector('[data-bind="outline"]');
    outlineWrap.appendChild(el("h2", { className: "bb-outline-title", textContent: content.outline.title }));
    outlineWrap.appendChild(el("div", { className: "bb-outline-ref", textContent: content.outline.reference }));

    content.outline.points.forEach(point => {
      const pointDiv = el("div", { className: "bb-point" });
      pointDiv.appendChild(el("div", { className: "bb-point-head" }, [
        el("span", { textContent: point.label }),
        el("span", { className: "bb-point-ref", textContent: point.ref })
      ]));
      if (point.subpoints) {
        const subWrap = el("div", { className: "bb-subpoints" });
        point.subpoints.forEach(sp => {
          const spDiv = el("div", { className: "bb-subpoint" });
          const titleDiv = el("div", { className: "bb-subpoint-title" });
          appendTemplate(titleDiv, sp.template);
          spDiv.appendChild(titleDiv);
          if (sp.detail) {
            const detailDiv = el("div", { className: "bb-subpoint-detail" });
            appendTemplate(detailDiv, sp.detail);
            spDiv.appendChild(detailDiv);
          }
          subWrap.appendChild(spDiv);
        });
        pointDiv.appendChild(subWrap);
      }
      outlineWrap.appendChild(pointDiv);
    });

    const notesLabel = el("div", { className: "bb-question-text", textContent: "My notes", style: "margin-top:16px;font-weight:700;" });
    const notesBox = fillBox(content.outline.notesPlaceholder, true);
    notesBox.setAttribute("data-role", "my-notes");
    outlineWrap.appendChild(notesLabel);
    outlineWrap.appendChild(notesBox);

    // Discussion sections
    const discussionWrap = root.querySelector('[data-bind="discussion"]');
    content.discussion.forEach(section => {
      const sectionDiv = el("div", { style: "margin-bottom:28px;" });
      sectionDiv.appendChild(el("h3", { className: "bb-discussion-title", textContent: section.title }));
      if (section.intro) sectionDiv.appendChild(el("div", { className: "bb-section-intro", textContent: section.intro }));

      section.questions.forEach(q => {
        const qDiv = el("div", { className: "bb-question" });
        qDiv.appendChild(el("div", { className: "bb-question-text", textContent: q }));
        const box = fillBox("Type your answer...");
        box.setAttribute("data-question", q);
        box.setAttribute("data-section", section.title);
        qDiv.appendChild(box);
        sectionDiv.appendChild(qDiv);
      });
      discussionWrap.appendChild(sectionDiv);
    });

    // Actions
    root.querySelector('[data-action="print"]').addEventListener("click", () => {
      // Print only this widget, not the whole church website page around it —
      // and do it in a plain isolated window so behavior is consistent across
      // Chrome, Safari, and Firefox regardless of the host page's own styles.
      const styleEl = root.querySelector("style");
      const printContent = root.cloneNode(true);
      printContent.querySelector(".bb-actions")?.remove();
      printContent.querySelector(".bb-hint")?.remove();
      printContent.querySelectorAll("[contenteditable]").forEach(node => node.removeAttribute("contenteditable"));

      const printWindow = window.open("", "_blank", "width=800,height=1000");
      if (!printWindow) {
        alert("Your browser blocked the print window. Please allow pop-ups for this page and try again.");
        return;
      }
      const pdoc = printWindow.document;
      pdoc.title = content.series + " " + content.sermonTitle;
      pdoc.head.appendChild(styleEl.cloneNode(true));
      pdoc.body.appendChild(printContent);

      const triggerPrint = () => {
        printWindow.focus();
        printWindow.print();
      };
      // Safari can be slow to lay out a freshly built window before print()
      // reflects it correctly, so wait for load with a short fallback timer.
      if (pdoc.readyState === "complete") {
        setTimeout(triggerPrint, 150);
      } else {
        printWindow.addEventListener("load", () => setTimeout(triggerPrint, 150));
      }
    });

    // Lazy-loads the PDF library only when someone actually clicks download,
    // so the page doesn't depend on it just to render.
    function ensureJsPDF() {
      if (window.jspdf && window.jspdf.jsPDF) return Promise.resolve(window.jspdf.jsPDF);
      return new Promise((resolve, reject) => {
        const s = document.createElement("script");
        s.src = "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js";
        s.onload = () => resolve(window.jspdf.jsPDF);
        s.onerror = () => reject(new Error("jsPDF failed to load"));
        document.head.appendChild(s);
      });
    }

    root.querySelector('[data-action="download"]').addEventListener("click", async () => {
      let JsPDF;
      try {
        JsPDF = await ensureJsPDF();
      } catch (e) {
        alert("Couldn't load the PDF generator. Check your connection and try again.");
        return;
      }

      const doc = new JsPDF({ unit: "pt", format: "letter" });
      const marginLeft = 54;
      const maxWidth = doc.internal.pageSize.getWidth() - marginLeft * 2;
      const pageBottom = doc.internal.pageSize.getHeight() - 54;
      const lineHeight = 15;
      let y = 60;

      function ensureSpace(need) {
        if (y + need > pageBottom) {
          doc.addPage();
          y = 60;
        }
      }

      function addWrapped(text, fontSize, weight, gapAfter) {
        doc.setFont("helvetica", weight);
        doc.setFontSize(fontSize);
        const lines = doc.splitTextToSize(text, maxWidth);
        lines.forEach(line => {
          ensureSpace(lineHeight);
          doc.text(line, marginLeft, y);
          y += lineHeight;
        });
        y += gapAfter || 0;
      }

      addWrapped(content.series + " — " + content.weekDate, 16, "bold", 4);
      addWrapped(content.sermonTitle + " (" + content.scripture + ")", 12, "normal", 18);

      // Renders a node's text with any empty blanks shown as a visible line,
      // instead of silently disappearing, so the PDF is a full overview
      // whether or not someone filled everything in.
      function textWithBlanks(node) {
        const clone = node.cloneNode(true);
        clone.querySelectorAll(".bb-blank").forEach(b => {
          if (!b.textContent.trim()) b.textContent = "_____";
        });
        return clone.innerText.trim();
      }

      if (content.buildingBlocks && content.buildingBlocks.length) {
        addWrapped(content.buildingBlocksTitle, 13, "bold", 6);
        Array.from(blocksList.children).forEach((li, i) => {
          addWrapped((i + 1) + ". " + textWithBlanks(li), 11, "normal", 4);
        });
        y += 10;
      }

      addWrapped(content.outline.title, 13, "bold", 2);
      addWrapped(content.outline.reference, 10, "normal", 8);
      root.querySelectorAll(".bb-point").forEach(pointEl => {
        const head = pointEl.querySelector(".bb-point-head");
        if (head) {
          const labelText = head.querySelector("span:not(.bb-point-ref)")?.textContent.trim() || "";
          const refText = head.querySelector(".bb-point-ref")?.textContent.trim() || "";
          addWrapped((labelText + "  " + refText).trim(), 11, "bold", 4);
        }
        pointEl.querySelectorAll(".bb-subpoint").forEach(sp => {
          const titleEl = sp.querySelector(".bb-subpoint-title");
          const detailEl = sp.querySelector(".bb-subpoint-detail");
          if (titleEl) addWrapped(textWithBlanks(titleEl), 11, "normal", 2);
          if (detailEl) addWrapped(textWithBlanks(detailEl), 10, "normal", 8);
        });
      });
      y += 6;

      const myNotes = root.querySelector('[data-role="my-notes"]').innerText.trim();
      addWrapped("My Notes", 12, "bold", 2);
      addWrapped(myNotes || "_______________________________________________", 11, "normal", 18);

      addWrapped("Small Group Discussion", 13, "bold", 8);
      content.discussion.forEach(section => {
        addWrapped(section.title, 12, "bold", 2);
        if (section.intro) addWrapped(section.intro, 10, "normal", 4);
        section.questions.forEach(q => {
          const box = Array.from(root.querySelectorAll(".bb-fill[data-question]"))
            .find(b => b.getAttribute("data-question") === q && b.getAttribute("data-section") === section.title);
          const answer = box ? box.innerText.trim() : "";
          addWrapped(q, 11, "bold", 2);
          addWrapped(answer || "_______________________________________________", 11, "normal", 10);
        });
        y += 6;
      });

      const filename = content.series.toLowerCase().replace(/\s+/g, "-") + "-" +
        content.weekDate.split("·")[0].trim().toLowerCase().replace(/\s+/g, "-") + "-notes.pdf";
      doc.save(filename);
    });
  }
})();
