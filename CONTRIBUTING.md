# Contributing to SirDeep

Welcome to **SirDeep**! We are thrilled that you want to help build and improve the flagship open-source community engine for [OpenWinter](https://github.com/opensourcewinter).

Our mission is simple: **Build together. Share freely. Keep technology open.**

Whether you are fixing a typo, optimizing audio streaming pipelines, adding a new AI provider, or strengthening security watchdogs, your contributions are deeply appreciated.

---

## 📜 Table of Contents
1. [Code of Conduct](#-code-of-conduct)
2. [How Can I Contribute?](#-how-can-i-contribute)
3. [Development Environment Setup](#-development-environment-setup)
4. [Coding Standards & Conventions](#-coding-standards--conventions)
5. [Git Workflow & Commit Conventions](#-git-workflow--commit-conventions)
6. [Submitting a Pull Request](#-submitting-a-pull-request)
7. [Reporting Bugs & Security Issues](#-reporting-bugs--security-issues)

---

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful, inclusive, and constructive in all discussions, code reviews, and community interactions.

---

## 💡 How Can I Contribute?

* **Report Bugs**: Open a detailed issue on GitHub using our Bug Report template.
* **Suggest Enhancements**: Propose new features or architectural improvements.
* **Submit Pull Requests**: Implement bug fixes, new modules, or documentation updates.
* **Write Tests & Docs**: Improve code coverage, add examples, or refine tutorials.

---

## 🛠️ Development Environment Setup

### 1. Prerequisites
* **Python**: 3.11 or higher
* **FFmpeg**: Required for the radio streaming engine (ensure it is accessible on your system `PATH`)
* **Git**: Installed and configured with your name and email

### 2. Fork and Clone
```bash
# Clone your fork
git clone https://github.com/<your-username>/sirdeep.git
cd sirdeep

# Add the official repository as upstream
git remote add upstream https://github.com/opensourcewinter/sirdeep.git
```

### 3. Create a Virtual Environment
```bash
# On Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

# On Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Local Configuration
```bash
cp .env.example .env
cp config/config.example.yaml config/config.yaml
```
> [!IMPORTANT]
> Never commit `.env` or `config/config.yaml` containing real tokens or production secrets. These are explicitly ignored by `.gitignore`.

---

## 🎨 Coding Standards & Conventions

To maintain a clean and reliable codebase, please adhere to these standards:

### 1. Python Style
* Follow **PEP 8** guidelines.
* Use 4 spaces for indentation (no tabs).
* Maximum line length: **100 characters** (soft limit: 120 characters for long string literals).
* Always use **type hints** for function signatures:
  ```python
  async def get_user_xp(user_id: int) -> int:
      ...
  ```

### 2. Asynchronous Architecture
* SirDeep is built entirely on `asyncio` and `discord.py` v2.4+.
* **Never execute blocking I/O calls** (e.g. `requests.get()`, `time.sleep()`, or synchronous file writes) directly in the event loop. Always use `aiohttp`, `asyncio.sleep()`, or run blocking operations in an executor (`loop.run_in_executor`).

### 3. Zero-Trust Security Practices
* **Input Sanitization**: Treat all user inputs (chat prompts, usernames, stream URLs) as untrusted.
* **SSRF Prevention**: Validate all remote URLs against strict protocol whitelists (`http`, `https`).
* **Resource Bounds**: Bound all image processing dimensions and memory allocations (`Image.MAX_IMAGE_PIXELS`).

---

## 🔀 Git Workflow & Commit Conventions

We follow the **[Conventional Commits](https://www.conventionalcommits.org/)** specification:

### Commit Format
```text
<type>(<optional scope>): <short description>

[optional body]

[optional footer(s)]
```

### Allowed Types
* `feat`: A new feature or capability (e.g., `feat(radio): add volume attenuation slider`)
* `fix`: A bug fix (e.g., `fix(audit): handle NoneType in channel deletion logs`)
* `docs`: Documentation updates (e.g., `docs(readme): add docker deployment diagram`)
* `style`: Code style changes (formatting, missing semi-colons, no logic change)
* `refactor`: Code refactoring without changing behavior
* `perf`: Performance improvements
* `test`: Adding or updating test cases
* `chore`: Build processes, tooling, or repository maintenance

---

## 🚀 Submitting a Pull Request

1. **Create a topic branch** from `main`:
   ```bash
   git checkout -b feat/add-deepseek-provider
   ```
2. **Make your changes** and test thoroughly on your private Discord test server.
3. **Commit your changes** with descriptive commit messages:
   ```bash
   git commit -m "feat(ai): support DeepSeek API via OpenAI-compatible endpoint"
   ```
4. **Rebase on upstream main** before pushing:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```
5. **Push to your fork**:
   ```bash
   git push origin feat/add-deepseek-provider
   ```
6. **Open a Pull Request** on GitHub against `opensourcewinter/sirdeep:main`.
7. Fill out the PR template describing the purpose, changes made, and verification steps.

---

## 🔒 Reporting Bugs & Security Issues

* For **general bugs and feature requests**, please open a public [GitHub Issue](https://github.com/opensourcewinter/sirdeep/issues).
* For **security vulnerabilities**, **DO NOT** create a public issue. Follow our private disclosure process detailed in [SECURITY.md](SECURITY.md).

---

Thank you for helping make **SirDeep** and **OpenWinter** great! Happy coding! ❄️
