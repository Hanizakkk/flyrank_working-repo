# Next Case

## Where it goes
The next case study is added as a new object inside `src/data/cases.js`, in the `CASES` array. Nothing in `App.jsx`, `App.css`, or the AI/local reply logic needs to change — the chatbot, sidebar, and AI system prompt all read straight from that file.

## The next piece of work
**AI Career Advisor**

Set in one place: `export const NEXT_CASE = "..."` at the top of `src/data/cases.js`.

## Structure to fill in (Problem → What I Did → What Came of It)

```js
{
  id: "ai-career-advisor",
  title: "AI Career Advisor",
  status: "live",
  tags: ["add", "relevant", "keywords"],
  problem: "One or two sentences: what gap or need this addressed.",
  whatIDid: "The actual build approach, stack, and key decisions.",
  whatCameOfIt: "The result — what it does now, or what it unblocked.",
  links: {
    repo: "https://github.com/Hanizakkk/REPO-NAME",
    demo: "https://your-demo-link (or null)",
  },
},
```

## Exact steps to add it

1. **Choose the completed work** — confirm the AI Career Advisor build is far enough along to describe honestly.
2. **Write the three beats** — Problem / What I Did / What Came of It, in plain sentences, no invented numbers.
3. **Add the entry** — paste the object above into the `CASES` array in `src/data/cases.js`, filled in.
4. **Update `NEXT_CASE`** — set it to whatever the *following* project will be.
5. **Test locally** — `npm run dev`, ask the chatbot about the new case by name (both with and without AI mode enabled), confirm the sidebar lists it.
6. **Deploy** — commit and push to `main`. If the GitHub Actions workflow is set up (see README), the live site redeploys automatically. No manual rebuild step.

## How the chatbot's knowledge updates
- **Local mode:** `src/lib/localReply.js` matches questions against each case's `title`, `tags`, and `id` from `cases.js`.
- **AI mode:** `src/lib/groqReply.js` builds a system prompt directly from every case in `cases.js` each time the app loads — there's no separate training step, no embeddings, no vector store. Editing `cases.js` *is* updating both modes' knowledge.
