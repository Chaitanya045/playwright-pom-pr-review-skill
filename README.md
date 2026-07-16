# Playwright TypeScript POM PR Review Skill

A PR review skill for Playwright TypeScript Page Object Model frameworks.

Use it to review pull requests that change Playwright tests, page objects, component objects, business/workflow objects, fixtures, test data, locators, Playwright config, auth storage, lint/format setup, or CI for end-to-end tests.

## Install

```bash
npx skills add Chaitanya045/playwright-pom-pr-review-skill
```

## What it checks

The skill focuses only on code-impacting issues:

- POM architecture and separation of concerns
- Route page duplication in SPA test frameworks
- Component object and business workflow boundaries
- Brittle locators and weak locator scoping
- Flaky synchronization and non-web-first assertions
- TypeScript type-safety gaps
- Missing runtime schema validation for test data, env, and API inputs
- Playwright fixtures, isolation, auth-state, and parallelism problems
- CI, linting, formatting, and Playwright config guardrails

## Skill structure

```text
SKILL.md                         # lean model-facing skill entrypoint
references/review-playbook.md    # detailed checklist and examples
evals/cases.json                 # trigger and outcome eval cases
scripts/score_skill_evals.py     # deterministic eval scorer
scripts/validate_skill.py        # repository validation harness
tests/fixtures/                  # synthetic PR fixture for smoke testing
docs/eval-results.md             # recorded eval results
docs/validation.md               # validation numbers
LICENSE                          # MIT license
```

## Why the skill is split

`SKILL.md` is intentionally short for progressive disclosure. It contains the trigger, audit steps, completion criteria, priorities, and must-check signals.

The longer review playbook lives in `references/review-playbook.md` so the agent loads detailed guidance only when needed.

## Evaluation results

Tested with the session model `openai-codex/gpt-5.5` through the local eval harness using `completion(model="default")`.

### Summary

| Metric | With skill | Without skill | Difference |
| --- | ---: | ---: | ---: |
| Expected checks covered | 23/23 (100.0%) | 15/23 (65.2%) | +8 checks |
| Coverage points | 100.0 | 65.2 | +34.8 |

| Routing metric | Result |
| --- | ---: |
| Eval cases | 10 |
| Positive trigger cases | 5 |
| Negative trigger cases | 5 |
| Trigger runs | 20 |
| Trigger pass rate | 20/20 (100.0%) |
| Outcome cases | 5 |

### Coverage bar

```text
With skill     ███████████████████████ 23/23 100.0%
Without skill  ███████████████░░░░░░░░ 15/23  65.2%
Delta          ████████░░░░░░░░░░░░░░░ +8 checks
```


### Per-case coverage

| Eval case | Expected checks | With skill | Without skill |
| --- | ---: | ---: | ---: |
| bad framework diff | 11 | 11 | 5 |
| locator flake snippet | 3 | 3 | 2 |
| schema fixture snippet | 3 | 3 | 3 |
| SPA architecture snippet | 3 | 3 | 2 |
| auth and CI snippet | 3 | 3 | 3 |

Full report: [`docs/eval-results.md`](docs/eval-results.md)

## Validation results

Current validation results:

| Metric | Result |
| --- | ---: |
| Validation checks | 12 |
| Passed checks | 12 |
| Failed checks | 0 |
| Skill words | 479 |
| Reference words | 2144 |
| Quick checklist items | 16 |
| Research sources | 14 |
| Research high-impact signals | 20 |

Full report: [`docs/validation.md`](docs/validation.md)

## Running the checks

Score eval outputs:

```bash
python scripts/score_skill_evals.py
```

Validate the skill repository:

```bash
python scripts/validate_skill.py
```


## License

MIT. See [`LICENSE`](LICENSE).
