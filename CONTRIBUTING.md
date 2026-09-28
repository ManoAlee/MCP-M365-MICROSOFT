# Contributing to Enterprise Microsoft 365 MCP Server

Thank you for your interest in contributing to the **Enterprise Microsoft 365 MCP Server**!

---

## Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free environment for everyone. Please treat all contributors with respect.

---

## Security & Confidentiality (Crucial)

- **NEVER submit Pull Requests containing production credentials, tenant IDs, client secrets, passwords, or personal data (PII).**
- Always use standard mock values (`contoso.com`, `00000000-0000-0000-0000-000000000000`).
- Ensure all tests pass with standard mocks.

---

## Development Workflow

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/MCP-M365-MICROSOFT.git
   cd MCP-M365-MICROSOFT
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
   pip install -e .
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-new-tool
   ```
5. **Run tests**:
   ```bash
   python -m unittest discover tests
   ```
6. **Commit with clean conventional commits**:
   ```bash
   git commit -m "feat(tools): add message encryption audit tool"
   ```
7. **Push to your fork and submit a Pull Request**.
