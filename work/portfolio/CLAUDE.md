# CLAUDE.md — CaseFlow AI (React)

## Purpose
CaseFlow AI is Hania Zaki's FlyRank capstone: a real, deployed product where visitors ask a chatbot about her actual projects and get answers grounded in a structured case-study knowledge base. It also carries the "Send the Link" capstone deliverable itself — the note on how to add the next case, the named next case, and the reminder evidence all live inside this repo.

This is the second iteration of the project. The first was a static HTML/CSS/JS build; it was rebuilt in React after the user asked for a "better frontend" — meaning real framework structure, actual animations/transitions, and genuine AI-generated answers rather than only keyword matching.

## Architecture
```
/
├── src/
│   ├── data/cases.js       — the entire knowledge base; the only file a new case touches
│   ├── lib/localReply.js    — keyword-matching fallback, no API needed
│   ├── lib/groqReply.js       — real Llama-3.3-generated answers via Groq, grounded via system prompt built from cases.js
│   ├── App.jsx                 — main UI: welcome, chat log, sidebar, AI-mode key panel
│   ├── App.css                  — design system + animations
│   ├── index.css                  — global resets/fonts
│   └── main.jsx                     — React entry point
├── .github/workflows/deploy.yml  — auto-build + deploy to GitHub Pages on push to main
├── vite.config.js                    — sets `base` for GitHub Pages project-site routing
├── NEXT_CASE.md                        — how to add the next case + what it is
├── CAPSTONE_EVIDENCE.md                  — maps directly to FlyRank's 4 pass criteria
└── CLAUDE.md                               — this file
```

## Two response modes
- **AI (primary):** `chatApi.js` calls a separate serverless backend (`caseflow-vercel/api/chat.js`, deployed on Vercel — switched from an earlier Render attempt after Render started requiring billing details even on its free tier) which holds the Groq API key server-side via an environment variable and proxies requests to `llama-3.3-70b-versatile`. The key never appears in this frontend's code, its git history, or its built JS bundle — confirmed by grepping the production build output for the key prefix and finding nothing.
- **Local (fallback only):** `localReply.js` matches user questions against `title`/`tags`/`id` in `cases.js`. Used automatically if the backend is unreachable, so the site never fully breaks.

Project history note: two earlier iterations were tried and rejected before landing here — (1) visitor-supplied "bring your own key," rejected as too much setup friction for visitors; (2) key hardcoded directly in frontend source, which GitHub's push protection correctly blocked as a leaked secret, and even the fixed version (key as a GitHub Actions build-time secret) was still visible in the deployed JS bundle since there's no server to hide it from a browser-only app. This backend is what actually solves that: the key lives only in Render's environment variables, never touches the frontend at any stage.

## Design / voice
Same warm-editorial system as the original: Fraunces serif for headings, Inter for body, JetBrains Mono for labels/metadata, warm paper/ink palette with live-green/queued-amber status colors. This version adds real motion: a pulsing "live" dot, chip hover lift, message slide-in, and a three-dot typing indicator while waiting on a reply (local or AI).

## Case-study data structure
Each entry in `src/data/cases.js` → `CASES[]`:
```js
{
  id: "kebab-case-id",
  title: "Display Name",
  status: "live",
  tags: ["keyword", "keyword"],
  problem: "...",
  whatIDid: "...",
  whatCameOfIt: "...",
  links: { repo: "https://...", demo: "https://... or null" },
}
```
Top-level `NEXT_CASE` (string export) drives the "queued" panel and both reply modes' "what's next" answer.

## How to add a case
Full steps in `NEXT_CASE.md`. Short version: write the three beats → append one object to `CASES` in `cases.js` → update `NEXT_CASE` → test locally in both modes → git push (GitHub Actions redeploys automatically).

## How the AI "knowledge" updates
No training, no embeddings, no vector store. `groqReply.js` rebuilds its system prompt from `cases.js` on every request — editing that file *is* updating what the model knows and can say.

## Current projects (as of this write-up)
All three are verified from the user directly — content should not be embellished with numbers or claims not explicitly given.
1. **EcoSense AI** — Streamlit energy-consumption prediction/optimization tool built on an existing trained model and scaler. Repo: github.com/Hanizakkk/EcoSense-AI · Live: ecosense-energy.streamlit.app
2. **Campus Management System** — Java, role-based (admin/teacher/student) university management system with CRUD operations, facility status info, and chart-based summaries. Repo: github.com/Hanizakkk/Campus-Management-System
3. **FlyRank internship work** — the internship's own AI/ML assignments and capstone workflow. Repo: github.com/Hanizakkk/flyrank_working-repo. Explicitly framed as internship coursework, not a deployed commercial product.

## Next case
**AI Career Advisor** — not yet built/written up. See `NEXT_CASE.md`.

## Important implementation decisions
- Vite + React, no extra UI/animation libraries — animations are hand-written CSS keyframes/transitions to keep the dependency footprint small and the bundle fast.
- `base` in `vite.config.js` must match the GitHub repo name exactly or the deployed Pages site 404s on all assets — flagged clearly in the README.
- AI mode is opt-in and visitor-supplied-key only; no API key is ever bundled into the built app or committed to the repo.
- Reminder for the next write-up is documented as genuinely set (with screenshot) in `CAPSTONE_EVIDENCE.md` — do not mark future reminder items as done without an actual screenshot on file.
- Do not hardcode project facts into `App.jsx`/`App.css` — everything project-specific belongs in `src/data/cases.js` only.
