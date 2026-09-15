# SRC9060 GitHub Profile — Setup

This package combines the premium README design with two self-hosted GitHub Actions: one for a local metrics dashboard and one for the animated contribution snake. This avoids relying on the broken external GitHub stats, trophy, and activity-graph image services shown in the previous version.

## 1. Repository

Use your public profile repository:

`https://github.com/SRC9060/SRC9060`

The repository name must match the GitHub username exactly.

## 2. Replace your current profile files

Copy this package into the `SRC9060/SRC9060` repository. It contains:

```text
README.md
SETUP.md
.github/workflows/metrics.yml
.github/workflows/snake.yml
```

## 3. Push

```bash
git add .
git commit -m "Fix GitHub profile analytics and snake"
git push
```

## 4. Run both workflows once

On GitHub open **Actions** and run:

- **Generate GitHub Metrics**
- **Generate Contribution Snake**

The metrics workflow commits `profile/metrics.svg`, `profile/achievements.svg`, and `profile/activity.svg` into your repository. The snake workflow publishes the animated snake SVGs to the `output` branch.

## 5. Why the empty sections are fixed

The previous README depended on several third-party image endpoints. If one of those services is unavailable, GitHub shows only the broken-image alt text. The updated profile generates the important visuals inside your own repository instead.

The snake is the actual animated contribution-grid game: it moves across your GitHub contribution cells and eats them.

## 6. Important

You need to run each workflow once after pushing. After that, the scheduled workflows refresh the assets automatically.
