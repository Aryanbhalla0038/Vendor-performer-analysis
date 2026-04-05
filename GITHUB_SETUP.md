# GitHub Setup & Deployment Guide

Complete instructions for uploading your Vendor Performance Analysis project to GitHub and setting up CI/CD.

## Table of Contents

1. [Initial GitHub Setup](#initial-github-setup)
2. [Uploading Project](#uploading-project)
3. [Making Project Public](#making-project-public)
4. [GitHub Pages Documentation](#github-pages-documentation)
5. [CI/CD Setup](#cicd-setup)
6. [Security & Best Practices](#security--best-practices)

---

## Initial GitHub Setup

### Step 1: Create GitHub Account

If you don't have one: https://github.com/signup

### Step 2: Create New Repository

1. Go to https://github.com/new
2. Repository name: `vendor-performance-analysis`
3. Description: "Data pipeline and BI dashboard for vendor KPI analysis"
4. Choose: **Public** (for portfolio) or **Private** (for confidential)
5. Check "Add a README file"
6. Add .gitignore: **Python**
7. Choose License: **MIT License** (recommended)
8. Click "Create repository"

### Step 3: Install Git

**Windows:**
```bash
# Using Chocolatey
choco install git

# Or download from
https://git-scm.com/download/win
```

**Mac:**
```bash
brew install git
```

**Linux:**
```bash
sudo apt-get install git
```

### Step 4: Configure Git

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global core.autocrlf true  # Windows
```

---

## Uploading Project

### Option A: Simple Upload (Recommended for First Time)

```bash
# Navigate to project directory
cd "c:\Users\HP\Desktop\project vendor\vendor-performance-analysis"

# Initialize git
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit: Vendor performance analysis project v1.0"

# Add remote repository (replace USERNAME with your GitHub username)
git remote add origin https://github.com/USERNAME/vendor-performance-analysis.git

# Push to GitHub (may prompt for authentication)
git branch -M main
git push -u origin main
```

### Option B: Using SSH (More Secure)

#### Setup SSH Keys

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub  # Copy output
```

#### Add to GitHub

1. Go to GitHub Settings → SSH and GPG keys
2. Click "New SSH key"
3. Paste public key
4. Click "Add SSH key"

#### Push with SSH

```bash
git remote add origin git@github.com:USERNAME/vendor-performance-analysis.git
git branch -M main
git push -u origin main
```

### Step 5: Verify Upload

Visit: `https://github.com/YOUR_USERNAME/vendor-performance-analysis`

You should see all project files!

---

## Making Project Public

### Portfolio Setup

1. Go to your GitHub profile: `https://github.com/YOUR_USERNAME`
2. Consider adding project to your profile README:

```markdown
## Featured Projects

### [Vendor Performance Analysis](https://github.com/YOUR_USERNAME/vendor-performance-analysis)
- Data pipeline for vendor KPI analysis
- Python, SQL, Power BI, DAX
- Real-time dashboarding and reporting
```

### Share on LinkedIn

```
🎯 Excited to share my latest project!

Vendor Performance Analysis - A complete data pipeline & BI dashboard for vendor performance tracking.

Key components:
✓ Python ETL pipeline with data validation
✓ SQL Server integration  
✓ Power BI dashboards with custom DAX measures
✓ Real-time KPI monitoring

Check it out: [GitHub Link]

#DataEngineering #Analytics #PowerBI #Python
```

---

## GitHub Pages Documentation

Create a project website using GitHub Pages:

### Step 1: Enable GitHub Pages

1. Go to repo settings
2. Scroll to "GitHub Pages"
3. Select: Source → `main` branch
4. Folder: `/docs`
5. Click "Save"

### Step 2: Create index.md

Add to `docs/index.md`:

```markdown
# Vendor Performance Analysis

**Live Documentation:** https://your-username.github.io/vendor-performance-analysis/

## Quick Links

- [Installation & Setup](QUICKSTART.md)
- [Architecture Overview](ARCHITECTURE.md)
- [Data Dictionary](DATA_DICTIONARY.md)
- [DAX Measures Reference](DAX_MEASURES.md)
- [GitHub Repository](https://github.com/your-username/vendor-performance-analysis)

## Key Features

- ✅ Automated ETL Pipeline
- ✅ 4 Core KPI Metrics
- ✅ Power BI Integration
- ✅ Data Quality Validation
- ✅ Comprehensive Test Suite

## Quick Start

```bash
pip install -r requirements.txt
python src/main.py
```

Results saved to: `data/processed/vendor_analysis_results.xlsx`

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.9+ |
| Data Processing | Pandas, NumPy |
| Database | SQL Server |
| BI Tool | Power BI |
| Formulas | DAX |

## Contact & Support

- **GitHub Issues:** Report bugs and feature requests
- **Pull Requests:** Contribute improvements
- **Email:** your.email@example.com
```

### Step 3: Deploy

```bash
git add docs/
git commit -m "Add GitHub Pages documentation"
git push origin main
```

Visit: `https://your-username.github.io/vendor-performance-analysis/`

---

## CI/CD Setup

### GitHub Actions for Automated Testing

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Automated Releases

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        body: |
          Release notes for ${{ github.ref }}
          See CHANGELOG.md for details
```

### Activate Actions

1. Go to GitHub repo
2. Click "Actions" tab
3. Workflows should appear automatically
4. Click "Enable" on any workflow

---

## Security & Best Practices

### 1. Protect Sensitive Data

Never commit:
- `.env` files with real credentials
- API keys, tokens, passwords
- Private configuration files

Ensure `.gitignore` has:
```
.env
.env.local
secrets.yaml
config.local.yaml
*.key
```

### 2. Use GitHub Secrets for CI/CD

For deployment:

1. Go to Settings → Secrets and variables
2. Add secrets for:
   - `DB_PASSWORD`
   - `API_KEYS`
   - `DEPLOYMENT_TOKENS`

Use in workflows:
```yaml
- name: Deploy
  env:
    DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
  run: deploy.sh
```

### 3. Branch Protection

1. Go to Settings → Branches
2. Select main branch
3. Enable:
   - "Require pull request reviews"
   - "Require status checks to pass"
   - "Require branches to be up to date"

### 4. Semantic Versioning

Tag releases:
```bash
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0
```

Format: `v{major}.{minor}.{patch}`

### 5. CHANGELOG

Create `CHANGELOG.md`:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-04-05

### Added
- Initial release of Vendor Performance Analysis
- ETL pipeline with data validation
- 4 core KPI calculations
- Power BI dashboard integration
- Comprehensive test suite

### Features
- On-time delivery tracking
- Defect rate analysis
- Lead time variance
- Cost variance monitoring
```

---

## Maintenance Workflow

### Making Updates

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes, commit
git add .
git commit -m "Add new feature: description"

# Push to GitHub
git push origin feature/new-feature

# Create Pull Request on GitHub
# After review, merge to main

# Tag release
git tag -a v1.1.0 -m "Version 1.1.0"
git push origin v1.1.0
```

### Keeping Repository Clean

```bash
# Update from GitHub
git fetch origin
git pull origin main

# Delete old local branches
git branch -d feature-branch

# Prune remote tracking branches
git remote prune origin
```

---

## Portfolio Presentation Tips

### 1. Project README

Write compelling README that includes:
- ✅ What problem it solves
- ✅ How it works (with diagrams)
- ✅ Tech stack used
- ✅ Installation instructions
- ✅ Usage examples
- ✅ Results/metrics
- ✅ Future enhancements

### 2. Add Badges

```markdown
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests Passing](https://github.com/USERNAME/vendor-performance-analysis/workflows/Tests/badge.svg)]()
```

### 3. Screenshots/GIFs

Add demo images in `docs/screenshots/`:
- Dashboard preview
- Sample output
- Architecture diagram

Reference in README:
```markdown
![Dashboard Preview](docs/screenshots/dashboard.png)
```

### 4. Contributing Guidelines

Create `CONTRIBUTING.md`:

```markdown
# Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Code Style

- Use `black` formatter
- Follow PEP 8
- Add type hints
- Write docstrings
```

### 5. License

Ensure LICENSE file exists (MIT recommended for open source).

---

## Final Verification Checklist

- [ ] All files pushed to GitHub
- [ ] README.md displays correctly  
- [ ] QUICKSTART.md provides clear instructions
- [ ] .gitignore prevents credential leaks
- [ ] Documentation is complete in `docs/`
- [ ] Code has proper comments
- [ ] Tests pass locally
- [ ] GitHub Pages working (if enabled)
- [ ] README includes links to GitHub
- [ ] Project appears in GitHub profile

---

## Troubleshooting

### Can't push to GitHub

```bash
# Check remote
git remote -v

# Fix if needed
git remote set-url origin https://github.com/USERNAME/vendor-performance-analysis.git

# Try again with PAT (Personal Access Token)
# https://github.com/settings/tokens
```

### Large files not pushing

```bash
# Remove large files from git history
git rm --cached large_file.xlsx
git filter-branch --tree-filter 'rm -f large_file.xlsx' HEAD

# Or use Git LFS
git lfs install
git lfs track "*.xlsx"
```

---

## Next Steps

1. ✅ Create repository on GitHub
2. ✅ Push your project
3. ✅ Setup GitHub Pages
4. ✅ Configure CI/CD
5. ✅ Share on LinkedIn/Portfolio
6. ✅ Enable discussions for community

**Congratulations!** Your project is now on GitHub! 🎉
