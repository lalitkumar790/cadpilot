# Publish this student edition to GitHub

The prepared folder is ready to push, but first create the empty repository in your GitHub account.

## 1. Create the repository

1. Sign in to https://github.com.
2. Click the **+** menu → **New repository**.
3. Repository name: `cadpilot`.
4. Description: `Student-friendly CADPilot using MCP and Claude Desktop`.
5. Choose **Public** if you intend to share it with all students.
6. Do not initialize it with a README, `.gitignore`, or license (the prepared folder already has a README and `.gitignore`; licensing still needs an owner decision).
7. Click **Create repository**.

## 2. Push the prepared project

Install Git for Windows if necessary. Open PowerShell in the root of this folder (the folder containing `README.md`) and run:

```powershell
git init
git add .
git status
git commit -m "Prepare student-ready CADPilot"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/cadpilot.git
git push -u origin main
```

Replace `YOUR_GITHUB_USERNAME` with your GitHub username. Review `git status` before committing. The `.gitignore` excludes virtual environments, Python caches, generated CAD files, and local logs.

## 3. Verify the public repository

1. Open the repository URL in a private/incognito browser window.
2. Confirm the README displays correctly.
3. Confirm there is no `.venv`, `__pycache__`, `.pyc`, personal config, or CAD document in the repository.
4. Complete the checklist in `LICENSING_AND_RELEASE.md` before announcing the repository to students.
5. Add a GitHub Release only after a live FreeCAD + Claude Desktop test passes.

## 4. Give students this link

Once published, share:

`https://github.com/YOUR_GITHUB_USERNAME/cadpilot`

Students can choose **Code → Download ZIP** and follow the README. They do not need Git to install or use the project.
