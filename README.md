# Playwright TypeScript POM PR Review Skill

A PR review skill for Playwright TypeScript Page Object Model frameworks.

Use it to review pull requests that change Playwright tests, page objects, component objects, business/workflow objects, fixtures, test data, locators, Playwright config, auth storage, lint/format setup, or CI for end-to-end tests.

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

Current eval results:

| Metric | Result |
| --- | ---: |
| Eval cases | 10 |
| Positive trigger cases | 5 |
| Negative trigger cases | 5 |
| Trigger runs | 20 |
| Trigger pass rate | 20/20 (100.0%) |
| Outcome cases | 5 |
| With-skill expected checks covered | 23/23 (100.0%) |
| Without-skill expected checks covered | 15/23 (65.2%) |
| Skill delta | +8 checks |

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
