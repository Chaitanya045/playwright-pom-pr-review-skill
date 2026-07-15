---
name: pr-review-playwright-pom-typescript
description: Use when reviewing pull requests that change Playwright TypeScript Page Object Model frameworks, page/component/business objects, fixtures, test data, locators, Playwright config, lint/format setup, or CI for end-to-end tests. Check only code-impacting defects in architecture, locator stability, synchronization, type/runtime validation, isolation/auth, and PR guardrails; do not use for non-Playwright app code or generic style review.
---

# PR Review: Playwright TypeScript POM Frameworks

## Goal

Review Playwright TypeScript framework PRs for defects that change reliability, maintainability, type safety, security, or CI confidence. Do not produce generic best-practice essays. Every comment must cite changed code, explain the failure mode, and propose a concrete fix.

For the full checklist and examples, read `references/review-playbook.md`.

## Use this skill when

- The PR changes Playwright tests, page objects, component objects, business/workflow objects, fixtures, test data, API helpers used by E2E tests, auth storage, Playwright config, lint/format config, or CI.
- The review asks about POM architecture, SPA test framework scaling, locator quality, type safety, schema validation, flaky synchronization, or PR guardrails.

## Do not use this skill when

- The PR is unrelated product code with no Playwright framework/test impact.
- The request is a UI design review, unit-test-only review, Selenium/Cypress review, or generic formatting pass.
- A formatter/linter already owns the issue and there is no missing enforcement to review.

## Review priorities

1. **Blocker**: false positives, known flake sources, leaked auth state/secrets, shared browser state, committed `.auth` files, disabled CI validation.
2. **High**: duplicated route POM logic, brittle selectors on core flows, hard waits/forced actions, untyped fixtures, unsafe casts, unvalidated JSON/env/API data.
3. **Medium**: mixed responsibilities, weak fixture composition, missing trace/report config, unclear business-level assertions.
4. **Low**: localized maintainability cleanup. Avoid low comments unless paired with higher-impact findings.

## Must-check signals

- Route pages duplicating reusable SPA components instead of composing component objects.
- Specs exposing UI mechanics where a business/workflow object should express intent.
- Multiple objects for the same page/component in one test path, especially with `any` or mutable globals.
- CSS/XPath/index locators where role/label/text/test id contracts are available.
- `waitForTimeout`, `waitForSelector`, `waitForNavigation`, `networkidle`, `force: true`, `ElementHandle`, `$`, `$$`, `$eval`, or manual `isVisible()` assertions.
- Missing web-first assertions for business outcomes.
- `JSON.parse(...) as Type`, untyped env/config reads, non-null assertions, missing schema validation for runtime data.
- Shared `page`/`context`/POM state, `beforeAll` UI state, order-dependent tests, shared accounts for parallel state-mutating tests.
- Committed `playwright/.auth` or missing `.gitignore` for auth state.
- Missing `tsc --noEmit`, Playwright ESLint rules, `@typescript-eslint/no-floating-promises`, formatter checks, `forbidOnly`, trace-on-retry, browser install, and PR CI execution.

## Output format

For each finding:

```md
[Severity] Problem: <failure mode>
Evidence: <changed line/pattern>
Fix: <specific code/design change>
```

If clean, say no code-impacting findings and list the meaningful areas checked: architecture, locators, sync/assertions, type/runtime validation, fixtures/isolation/auth, and CI guardrails.
