# Skillshare Workspace Guidelines & AI Coding Standards

This file defines the project-scoped rules and practices to be followed when developing or operating within the `skillshare` repository.

## 1. AI Coding & Collaborative Workflow (Crucial)

To ensure high-quality and reliable contributions, adhere strictly to the following steps:

*   **Design Before Coding (设计先行)**:
    *   Do not immediately write code or propose implementation for complex tasks.
    *   First, perform a thorough analysis of the requirements across multiple perspectives (Architecture, Test, Operations, Security, Product).
    *   Clarify: business flows, data flows, module divisions, boundary conditions, exception handling, and potential risks.
    *   Draft a design document (`design.md` or equivalent) and get feedback before implementing.
*   **Decoupled Modules & Clear Interfaces**:
    *   Break problems down into small, single-responsibility modules.
    *   Define input, output, states, lifecycles, and error codes explicitly before implementing logic.
*   **Cautious Abstraction (适度重复，谨慎抽象)**:
    *   Favor moderate duplication of small, localized logic (e.g., separate parsers) over complex inheritance or deep abstractions, as localized code is easier for AI agents to maintain.
    *   Abstract into shared modules only when code has matured and a clear reuse pattern exists.
*   **Independent Review & Testing**:
    *   Do not let the implementing agent perform its own testing and code review. Assign testing and review tasks to independent agent instances (e.g. using `research` or a separate `self` subagent) to avoid self-verification bias.
    *   Prioritize verification of: memory leaks, lock contention, NUMA/cache optimization, and performance regression in performance-critical paths (e.g., DPI flow management, packet dispatch, XML reloads).

## 2. Workspace Technical Architecture & CLI Usage

Understand how the `skillshare` ecosystem operates:

*   **Path Conventions (Windows)**:
    *   Workspace/SSOT path: `%APPDATA%\skillshare` (typically resolves to `c:/Users/lcq/AppData/Roaming/skillshare`).
    *   Target paths for synchronized tools (Cursor, Claude, Codex, OpenCode) reside under the user's home directory (e.g. `C:/Users/<username>/.cursor/skills`).
*   **Synchronization & Execution**:
    *   Always use the local configuration template (`config.windows.yaml` for Windows) when updating configurations, and activate them using `.\setup-config.ps1`.
    *   Synchronize skills to target applications via `skillshare sync --all`. Use `skillshare status` to inspect current synchronization statuses.
*   **GSD Layer Structure**:
    *   **L1 Runtime**: Located in user home (e.g. `~/.codex/get-shit-done/`), updated via `npx @opengsd/gsd-core@latest`.
    *   **L2 Skills**: Upstream GSD skills located in `skills/base/gsd-*/` (tracked via Git), updated via `skillshare update --group base`.
    *   **L3 Merlynr Customizations**: Customized stack located in `skills/merlynr-dev-stack` and `gsd-ns-*` namespaces. Do not overwrite custom stack configurations during GSD updates.
