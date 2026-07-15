# Detailed Playwright TypeScript POM PR review playbook


# PR Review: Playwright TypeScript POM Frameworks

Use this skill when reviewing a pull request that changes a Playwright TypeScript test framework, Page Object Model layer, component object, business workflow object, fixtures, test data, Playwright config, lint/format setup, or CI.

## Review contract

You are a code reviewer, not a framework lecturer.

- Comment only on defects that change reliability, maintainability, type safety, security, or CI confidence.
- Anchor every finding to changed code or an omitted guardrail that the PR should add.
- Prefer one concrete fix over broad advice.
- Do not request enterprise layering for small suites unless the diff creates duplication or leaks UI implementation into business tests.
- Do not ban `getByTestId`; prefer user-facing locators first, but accept test ids as explicit contracts when role/text/label is unstable or unavailable.
- Do not nitpick formatting if a formatter check already enforces it. Do flag missing formatter/linter enforcement when the PR adds or restructures the framework.

## Severity model

Use the highest severity justified by code impact.

- **Blocker**: false positives, known flake source, leaked secrets, broken isolation, disabled PR validation, committed auth state, or tests that cannot run in CI.
- **High**: duplicated framework architecture that will diverge, untyped or unvalidated external data, brittle selectors on core flows, missing awaits, shared state under parallelism.
- **Medium**: maintainability or debuggability issue with a clear failure mode: mixed responsibilities, weak fixture design, missing trace/report config, missing custom messages for opaque assertions.
- **Low**: localized cleanup that reduces confusion but does not affect current behavior. Avoid low comments unless already leaving a higher-impact review.

## Architecture and separation of concerns

Flag when the PR makes the framework harder to scale or changes the abstraction boundary.

### Route POM duplication

Flag repeated behavior across route page objects, especially for SPA components.

Bad signals:

- `PatientsPage`, `TasksPage`, and `UsersPage` each implement their own `search`, `sortByColumn`, `applyFilters`, `clearFilters`, `openModal`, pagination, or table row helpers.
- Page class grows because reusable widgets are copied into route objects.
- A PR adds another route page with logic already present in another page.

Prefer:

- Component objects for reusable UI widgets: `SearchComponent`, `FilterComponent`, `TableComponent`, `PaginationComponent`, `ModalComponent`.
- Route pages compose components and keep route-specific wiring.

Review comment shape:

> This adds a second implementation of table sorting in a route page. The same interaction already exists in `PatientsPage`, so this will diverge when the shared table changes. Extract a `TableComponent` that scopes to this table root and let both pages compose it.

### Business workflow leakage

Flag tests that know too much about UI implementation when a business action exists or is being introduced.

Bad signals:

- Specs chain low-level component calls for business outcomes: `search.search()`, `table.openRow(0)`, `modal.fillForm()`, `modal.save()`.
- Tests mention modal/sidebar/table details for workflows such as creating a patient, assigning a task, inviting a user, or changing a role.
- A UI redesign from modal to side panel would force many spec changes without changing business behavior.

Prefer:

- Business objects or workflow services such as `PatientManagement.createPatient(patient)`.
- Component/page methods remain implementation details beneath the business workflow.

Do not force this for one-off simple tests. Flag it when the PR repeats the workflow or exposes volatile UI details in multiple specs.

### Multiple objects for the same page/class

Flag duplicate instances when they fragment lifecycle or hide setup state.

Bad signals:

- A spec creates `new LoginPage(page)` in `beforeEach`, then creates another `new LoginPage(page)` inside a test.
- A page fixture returns one object but specs create a second instance manually.
- The same component object is created repeatedly with the same root locator instead of being a readonly composed member.
- Objects have constructor side effects such as navigation, data creation, or subscriptions, making duplicate instances observable.

Prefer:

- Typed Playwright fixtures that create one page/business object per test scope.
- Page objects with cheap constructors and explicit methods for navigation/setup.
- Reuse composed component members from the page object.

### Mixed responsibilities

Flag page objects or components that own unrelated concerns.

Bad signals:

- Page object parses `process.env`, loads JSON fixtures, constructs API clients, creates users, and manipulates UI locators.
- Component object performs route navigation, database cleanup, or account provisioning.
- Business object reaches directly into raw locators instead of coordinating page/component APIs.

Prefer:

- `fixtures/` for setup/teardown and dependency injection.
- `api/` for API clients.
- `test-data/` or `factories/` for data builders.
- `schemas/` for runtime validation.
- `pages/` for route-specific UI orchestration.
- `components/` for reusable UI interactions.
- `business/` or `workflows/` for business capabilities.

## Locators

Review locators as contracts. Bad locators are code defects because they create false failures or false positives.

### Prefer resilient Playwright locators

Flag:

- CSS/XPath selectors for interactive user-visible elements: `.btn.primary`, `//button[3]`, `#root > div:nth-child(2)`.
- Raw `page.locator('button')`, `locator('text=Save')`, or broad text selectors when role/label/test id can identify the element.
- Missing accessible name on `getByRole` when multiple matching roles can exist.
- `first()`, `last()`, or `nth()` without a semantic parent filter.
- Table row selection by index when row text, accessible cell content, or record id is available.

Prefer, in order:

1. `getByRole(role, { name })` for interactive elements.
2. `getByLabel`, `getByPlaceholder`, `getByAltText`, `getByText` where those match the user contract.
3. `getByTestId` for explicit app/test contracts, localization, icon-only controls, dynamic text, or elements without a stable accessible name.
4. Chained and filtered locators scoped to a component root.

Review comment shape:

> This selector depends on DOM depth and button order. The user contract is the accessible button name, so use `page.getByRole('button', { name: 'Save patient' })`. That keeps the test stable if the layout wrapper changes.

### Scope component locators

Flag component classes that search the whole page when they are meant to represent one widget instance.

Bad:

```ts
export class TableComponent {
  constructor(private page: Page) {}
  row(name: string) {
    return this.page.getByRole('row', { name });
  }
}
```

Better:

```ts
export class TableComponent {
  constructor(private root: Locator) {}
  row(name: string) {
    return this.root.getByRole('row', { name });
  }
}
```

Reason: reusable components must be reusable when multiple tables/modals/forms appear on the same route.

## Synchronization and assertions

Flag code that bypasses Playwright's auto-waiting or web-first assertions.

### Flaky synchronization

Flag:

- `page.waitForTimeout(...)` used as synchronization.
- `waitForSelector` before acting on a locator.
- `waitForNavigation` in new code instead of URL, response, or locator assertions appropriate to the action.
- `networkidle` as a readiness signal for app UI.
- `{ force: true }` on clicks/checks unless the PR proves it is testing an intentionally covered control.
- `ElementHandle`, `page.$`, `page.$$`, `$eval`, or `$$eval` for normal UI interactions.

Prefer:

- Locator actions and assertions: `await expect(locator).toBeVisible()`, `toHaveText`, `toHaveURL`, `toHaveCount`, `toBeEnabled`.
- `expect.poll` or `expect.toPass` for non-DOM eventual consistency.
- Route or response waits only when testing network behavior directly.

### Manual assertions

Flag non-retrying UI checks:

```ts
expect(await page.getByText('Saved').isVisible()).toBe(true);
expect(await status.textContent()).toBe('Submitted');
```

Prefer:

```ts
await expect(page.getByText('Saved')).toBeVisible();
await expect(status).toHaveText('Submitted');
```

### Missing business validation

Flag tests that perform actions but never assert the business outcome.

Bad signals:

- Test ends after `save()`, `submit()`, `create()`, or navigation.
- Assertions exist only inside helper methods and are invisible from the spec's intent.
- Assertions verify implementation details instead of the requirement.

Prefer one clear requirement-level assertion in the spec or business workflow, plus lower-level page assertions only for stable state transitions.

## Type safety and runtime schema validation

TypeScript catches authoring mistakes; it does not validate untrusted runtime data.

### TypeScript guardrails

Flag:

- `any`, broad `unknown as X`, non-null assertions on env/config, or `JSON.parse(...) as Type`.
- Untyped fixtures: `base.extend({ userPage: async (...) => ... })` without fixture type parameters.
- Mutable exported state used by tests or page objects.
- Missing `tsc --noEmit` in scripts/CI for a TypeScript Playwright framework.
- `strict: false` or absent strict mode when the PR adds new framework code.

Prefer:

- `import type { Page, Locator } from '@playwright/test'` for types.
- `base.extend<MyFixtures, MyWorkerFixtures>(...)` for typed fixtures.
- `readonly` or `private readonly` locators and dependencies where mutation is not intended.
- `tsc -p tsconfig.json --noEmit` in CI.

### Runtime validation

Flag unvalidated data crossing a trust boundary:

- JSON test fixtures loaded from disk.
- API responses used to drive UI assertions.
- Environment variables.
- CSV/Excel/imported test data.
- Generated or shared test data passed into business workflows.

Bad:

```ts
const patient = JSON.parse(readFileSync('patient.json', 'utf8')) as Patient;
await patientManagement.createPatient(patient);
```

Better:

```ts
const patient = PatientSchema.parse(JSON.parse(readFileSync('patient.json', 'utf8')));
await patientManagement.createPatient(patient);
```

Require schema validation with a library such as Zod, Valibot, io-ts, TypeBox, or an existing repo-standard validator. Do not demand Zod specifically if the repo already has a validator.

## Fixtures, authentication, isolation, and data

### Fixture design

Flag:

- Repeated setup/teardown copied across files instead of reusable fixtures.
- `let pageObject` globals assigned in hooks when a typed fixture would express the dependency.
- Cleanup split from setup in a way that can be skipped or forgotten.
- Heavy fixture setup that runs for tests that do not need it.

Prefer Playwright fixtures because they are reusable, on-demand, composable, isolated between tests, and type-safe in TypeScript.

### Isolation and parallelism

Flag:

- Shared `page`, `context`, POM, account, or mutable data across tests.
- UI setup in `beforeAll` using a shared page.
- Tests that depend on execution order or data left by previous tests.
- Parallel tests that mutate the same server-side entity/account.

Prefer:

- One browser context per test through Playwright fixtures.
- Unique data per test or per worker.
- Worker-scoped authenticated state only when tests in that worker can safely share it.

### Authentication state

Flag:

- `playwright/.auth/*.json`, storage state files, cookies, tokens, or headers committed to the repo.
- Missing `.gitignore` entry for auth state when the PR adds storage-state auth.
- One shared account for tests that mutate server-side state in parallel.

Prefer:

- `playwright/.auth` in `.gitignore`.
- Setup project for shared auth when tests do not mutate server-side state.
- One account/storage state per worker when tests mutate shared server state.
- Auth via API request when supported and faster than UI login.

## CI, linting, formatting, and Playwright config

Flag missing guardrails when the PR introduces or materially changes the framework.

### CI must prove the framework runs

Expected PR checks:

- Install dependencies with the repo's lockfile command.
- Install Playwright browsers and system dependencies, or use the official Playwright Docker image.
- Run `npx playwright test` or the repo's equivalent script.
- Run `tsc --noEmit` for TypeScript checks.
- Run ESLint and formatter checks when configured.
- Upload Playwright HTML report, traces, screenshots, or JUnit output on failure or always as appropriate.

### Playwright config should protect CI

Flag missing or weakened config:

- `forbidOnly: !!process.env.CI` absent.
- Retries enabled locally without reason, or no CI retry policy for known E2E flake handling.
- Trace disabled in CI; prefer `trace: 'on-first-retry'` for debuggability without always-on overhead.
- Uncontrolled `workers` in resource-constrained CI; prefer `workers: process.env.CI ? 1 : undefined` unless the CI is intentionally sharded or sized for parallelism.
- No `baseURL`, `webServer`, `testDir`, `projects`, or reporter when the framework relies on those conventions.

### ESLint and formatter review

Flag absence or bypass of:

- `eslint-plugin-playwright` recommended config or equivalent Playwright-specific rules.
- `@typescript-eslint/no-floating-promises` or equivalent missing-await protection.
- Rules/checks catching `test.only`, skipped tests, `page.pause`, `waitForTimeout`, `force`, raw locators, ElementHandle usage, and non-web-first assertions.
- Prettier or equivalent formatter check for TypeScript test/framework files.

Do not leave style comments when formatter output would handle them. Ask for the formatter check instead.

## Quick scan checklist

Before finalizing the review, scan the diff for these code-impacting mistakes:

1. Duplicate route POM logic that should be a component object.
2. Specs exposing modal/table/button mechanics instead of business intent.
3. Multiple instances of the same page/component object in one test path.
4. Page objects mixing UI, API, env parsing, data factories, and cleanup.
5. CSS/XPath/index selectors where role/label/text/test id would be stable.
6. Unscoped component locators that break with multiple widget instances.
7. Hard waits, `force`, `networkidle`, `waitForSelector`, or ElementHandles.
8. Manual non-retrying assertions instead of web-first assertions.
9. Tests that act but do not assert the requirement.
10. `any`, unsafe casts, untyped fixtures, absent strict TypeScript checks.
11. Runtime data used without schema validation.
12. Shared page/context/POM/global state across tests.
13. Auth state committed or not ignored.
14. Shared accounts/data in parallel state-mutating tests.
15. Missing PR CI for install, browser setup, tests, typecheck, lint, format.
16. Missing Playwright config safety: `forbidOnly`, trace-on-retry, CI workers/reporters.

## Output style

Use concise review comments with this structure:

1. **Problem**: name the failure mode.
2. **Evidence**: changed line or pattern.
3. **Fix**: specific replacement or target design.

Template:

````md
[High] This introduces a flake: `waitForTimeout(2000)` guesses when the save has completed. If the API is slower, the next assertion can race; if it is faster, CI still waits. Replace it with the user-visible contract:

```ts
await patientPage.save();
await expect(patientPage.toast).toHaveText('Patient saved');
```
````

If the PR is clean, say so briefly and mention the meaningful areas checked: architecture layering, locators, fixtures/isolation, type/runtime validation, and CI guardrails.
