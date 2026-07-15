---
name: pr-review-playwright-pom-typescript
description: Review Playwright TypeScript POM pull requests. Use when PRs touch Playwright tests, page/component/business objects, fixtures, test data, locators, Playwright config, auth storage, lint/format setup, or CI for E2E tests; audit architecture, locator, synchronization, type/runtime validation, isolation/auth, and guardrail defects.
---

# PR Review: Playwright TypeScript POM Frameworks

## Goal

Audit Playwright TypeScript framework PRs for reliability, maintainability, type safety, security, or CI defects. Each finding needs code evidence, a failure mode, and a concrete fix.

When a signal appears, read `references/review-playbook.md` for rules and examples.

## Use this skill when

- A PR changes Playwright tests, page/component/business objects, fixtures, test data, E2E API helpers, auth storage, Playwright config, lint/format config, or CI.
- The request asks about POM architecture, SPA framework scaling, locators, type safety, schema validation, flaky synchronization, or PR guardrails.

## Do not use this skill when

- The PR has no Playwright framework/test impact.
- The review is only UI design, unit tests, Selenium/Cypress, or formatter output already enforced by CI.

## Audit steps

1. **Scope** the changed files. Completion criterion: every changed file is either marked Playwright-relevant or explicitly out of scope.
2. **Inspect** every Playwright-relevant change against the must-check signals. Completion criterion: each signal is either not present or converted into a finding with evidence.
3. **Emit** only code-impacting findings. Completion criterion: every comment states severity, failure mode, changed-line evidence, and a concrete fix.

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

```md
[Severity] Problem: <failure mode>
Evidence: <changed line/pattern>
Fix: <specific code/design change>
```

If clean, say no code-impacting findings and list the checked areas: architecture, locators, sync/assertions, type/runtime validation, fixtures/isolation/auth, and CI guardrails.
