---
name: gemastik-latex
description: Use this skill whenever the user is writing, drafting, revising, or fixing a paper/makalah for GEMASTIK (Pagelaran Mahasiswa Nasional Bidang TIK), especially the Data Mining division, in LaTeX. Trigger this for requests like "buatkan makalah gemastik", "perbaiki draft latex gemastik saya", "tulis paper untuk lomba gemastik", revising a .tex file against juri/reviewer feedback, formatting a paper to IEEE two-column GEMASTIK style, or any mention of "Buletin Pagelaran Mahasiswa Nasional Bidang Teknologi Informasi dan Komunikasi". Also use when the user shares juri/reviewer comments (hasil cross eval, catatan revisi) about a GEMASTIK draft and wants it revised. Covers exact formatting rules (margins, fonts, section styles, table/figure captions, references), narrative/register conventions learned from finalist papers, and how to handle missing figures/plots with placeholders.
---

# GEMASTIK Data Mining Paper — LaTeX Writing Skill

Writes and revises GEMASTIK competition papers ("makalah") in LaTeX, matching
the exact IEEE-derived formatting required by the official Word template and
the writing register seen in papers that actually reached the final round.

## Before doing anything

1. Check whether the working directory already has a `.tex` draft (existing
   paper to revise) or reviewer feedback (juri comments / cross-eval notes).
   If revising, read the full existing `.tex` first — don't restart from
   scratch unless asked to.
2. Skim `references/finalist_examples.md` for two full finalist papers, and
   `references/format_rules.md` for the exact GEMASTIK/IEEE formatting spec.
   Both were extracted directly from the official template and two papers
   that passed to the final round — treat them as ground truth over anything
   you might otherwise assume about IEEE formatting.
3. If reviewer feedback is provided (e.g. a `hasilcrosseval.md` or similar),
   read `references/common_juri_complaints.md` — it maps the standard juri
   complaints to concrete fixes, since these recur across cohorts.
4. Always start a new paper from `assets/template.tex`. It already implements
   the full format spec (header banner, two-column title block, IEEE section
   numbering, caption styles, footer). Copy it, don't rebuild from scratch.

## Core workflow

### 1. Gather what you need before writing
Ask the user (or infer from context/memory) for: title, author names +
NRP/student IDs + faculty/institution + emails, corresponding author,
research topic/method, and whether this is a fresh paper or a revision.
If the user has an existing project's context (e.g. from memory of their own
research), use it — don't ask about things you can already infer.

### 2. Structure
GEMASTIK papers require **at minimum four main sections** plus references:
Pendahuluan (Introduction), Metode/Inovasi (Method), Hasil dan Diskusi
(Results and Discussion), and Kesimpulan (Conclusion). Length must be
**4–5 pages** in the two-column format — this is a hard constraint from the
rules, so track page count as you write and trim or expand to fit.

Strong finalist structure (seen in both reference papers) also includes:
- Pendahuluan with an explicit research gap / gap penelitian statement
- A literature/kajian teori or tinjauan pustaka section (can be folded into
  Pendahuluan for shorter papers, or split out as Section II for longer ones)
- Usulan Penelitian (proposed approach) — often merged into Metodologi
- A clear methodology with a numbered dataset/variable table
- Results presented with concrete numbers in tables, not just prose
- Kesimpulan that restates the strongest quantitative result and gives
  concrete Saran (recommendations) for follow-up work

### 3. Writing register — this is where most drafts fail
Read `references/common_juri_complaints.md` in full before drafting prose.
The single most common juri complaint is that text "reads like an AI
translation." Concretely, that means:

- **Don't translate settled technical terms into Indonesian.** Keep terms
  like *fine-tuning*, *chunking*, *embedding*, *overfitting*, *dataset*,
  *framework*, *Low-Rank Adaptation (LoRA)* in their original English form
  (italicized on first use per IEEE style), rather than inventing Indonesian
  equivalents. Spell out acronyms with the English term first, e.g.
  "*Low-Rank Adaptation* (LoRA)" not a translated paraphrase.
- **Write connected, argumentative prose**, not a bullet-by-bullet dump.
  Juri explicitly penalize splitting Pendahuluan into disconnected
  subsections when it could be one flowing argument — each paragraph should
  causally lead to the next ("karena itu…", "namun…", "oleh karena itu…").
  Only use `\subsection` inside Pendahuluan if the paper is long enough to
  need it; for shorter/earlier-stage papers, prefer a single flowing intro.
- **Be concrete about method details.** If the paper mentions scraping,
  state how long, how many rows/samples collected, and one real example of
  the data schema. Vague method descriptions ("kami melakukan scraping data")
  without numbers are a recurring, specific complaint.
- **Never claim results you don't have.** If experiments are incomplete,
  say so explicitly in-text (e.g. "hasil awal" and dedicate a section to
  planned/rancangan eksperimen) rather than writing results prose that
  implies completed experiments. Juri will directly ask "is there actually
  an experiment result yet?" if this is ambiguous — don't let it be
  ambiguous.
- **Support claims with citations**, especially in tinjauan pustaka —
  juri flag ideas as "relevant but needs comparison with more sources."
  Cite 10+ sources for a competitive paper, weighted toward 2023–2026 work.

### 4. Figures and plots — use placeholders, don't fabricate
Claude cannot generate real experimental plots, screenshots of a running
system, or dataset visualizations from data it doesn't have. When the paper
needs a figure (architecture diagram, training curve, results plot,
confusion matrix, etc.) that isn't provided by the user:

1. **Never invent fake data or a fake-looking plot and present it as a real
   result.** This would misrepresent the paper's findings.
2. Insert a placeholder `\includegraphics` pointing to a clearly-named file
   the user needs to supply, e.g. `gambar_arsitektur.png`,
   `plot_hasil_rq2.png`. Use the `placeholderfig` helper defined in
   `assets/template.tex`, which draws a labeled dashed box in place of a
   missing image so the compiled PDF is still legible pre-image.
3. Tell the user explicitly, in your chat response (not just in a code
   comment), which figures are placeholders and what they need to generate
   or provide for each — e.g. "Gambar 1 (arsitektur sistem) masih placeholder
   — silakan buat diagram alur sistem Anda dan simpan sebagai
   `gambar_arsitektur.png` di folder yang sama."
4. If the user does provide real data (a CSV, a metrics table, numbers in
   chat), Claude *can* build a genuine chart from that data using matplotlib
   and embed the real image — that's not fabrication, that's visualizing
   real numbers. Only refuse to fabricate when there's no underlying data.

### 5. Compiling
After writing or editing the `.tex` file, always compile to verify it
builds and check the page count:

```bash
cd /home/claude && pdflatex -interaction=nonstopmode -halt-on-error 02_paper.tex && pdflatex -interaction=nonstopmode -halt-on-error 02_paper.tex
```

Run pdflatex twice (references/labels need a second pass). Always use
`-halt-on-error` — without it, a failed metafont/font-generation step can
hang the command past the execution time limit instead of failing fast.
Check `/home/claude/*.log` for errors if it fails. Common issues, beyond
the usual missing `\end{...}` or unescaped `%`/`&` in table cells:

- **`[text]` as the first token right after a `\\` in a table row** gets
  parsed by LaTeX as an optional argument and throws "Missing number,
  treated as zero." Wrap it in braces, e.g. `{[Kategori]} & ...` instead of
  `[Kategori] & ...`.
- **`\sffamily` or true small caps (`\scshape`/`sc` caption option) without
  the `helvet` package** falls back to Computer Modern bitmap fonts that
  require on-the-fly metafont generation (`mktexpk`). This fails hard in
  sandboxed environments without metafont write access — including this
  one. `template.tex` already works around this by loading
  `\usepackage[scaled=0.92]{helvet}` for real Type1 Helvetica, and by using
  bold instead of true small caps for table captions. If you add any new
  `\sffamily`/`\scshape` usage, keep it inside this workaround or drop it.
- **`\usepackage[indonesian]{babel}`** requires `indonesian.ldf`, which is
  not installed in this environment (or on many minimal TeX Live
  installs). `template.tex` intentionally omits babel — don't add it back
  without first checking `kpsewhich indonesian.ldf` succeeds.

Report the resulting page count to the user; if it's outside 4–5 pages, say
so and offer to trim or expand.

Copy the final PDF and .tex source to `/mnt/user-data/outputs/` and share
both with `present_files` — the user will want the source to keep editing
locally.

## Reference files

- `references/format_rules.md` — exact GEMASTIK/IEEE formatting spec
  (margins, fonts, sizes, heading levels, table/figure/equation/reference
  conventions), extracted from the official template. Read before any
  structural formatting decision.
- `references/finalist_examples.md` — condensed excerpts and structural
  breakdown of two papers that reached the GEMASTIK final round, showing the
  register, section flow, and how they present tables/results/citations.
  Read for tone and structure calibration, not for copying content.
- `references/common_juri_complaints.md` — a checklist derived from real
  juri feedback on a rejected/needs-revision draft, mapping each complaint
  to a concrete fix. Read before drafting or revising prose, and re-check
  the draft against this list before calling it done.
- `assets/template.tex` — ready-to-copy LaTeX skeleton implementing the full
  format spec (fancy header/footer banner, two-column title/intisari block,
  IEEE section numbering via titlesec, caption styles, placeholder-figure
  helper). Start every new paper from this file.
