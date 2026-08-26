# Portfolio — GitHub Pages setup

## First-time setup (do this once)

1. Go to [github.com](https://github.com) and log in (create a free account if you don't have one).
2. Click **New repository**. Name it `your-username.github.io` — replace `your-username` with your actual GitHub username, exactly, or your site won't work at the root URL.
3. Set it to **Public**, don't add a README (you already have one), then click **Create repository**.
4. On the new repo's page, click **Add file → Upload files**, and drag in `index.html` and this `README.md`.
5. Commit the upload (green button).
6. Go to **Settings → Pages** in the repo. Under "Build and deployment," source should be "Deploy from a branch," branch `main`, folder `/root`. Save.
7. Wait ~1 minute, then visit `https://your-username.github.io` — your site is live.

## Adding a new case study (every time you ship something)

1. On GitHub, open `index.html` in your repo and click the pencil icon (Edit).
2. Find the `<div class="ticket empty" data-log="LOG 01">` block (or the last one you added).
3. Copy that whole block, paste it right below itself, and change `LOG 01` → `LOG 02`.
4. Remove `class="ticket empty"` → just `class="ticket"`, and change `Next up` to `Shipped` (or similar) in `<span class="status">`.
5. Fill in the three beats — Problem / What I did / What came of it — and swap the stack tags.
6. Commit the change directly on GitHub (or from your computer with `git push` if you're using a local clone).
7. Site updates automatically within a minute.

No rebuild, no new tooling — just duplicate, fill in three lines, push.
