# AB Test Analyzer

A simple tool to analyze AB test results and generate insights.

## What it does

This tool helps you:
- Draft AB test
- Analyze AB test data
- Compare test variants
- Helping PM Making a Decision - not making the decision for the PM.
- Update specifc artifacts like Notion or JIRA
- Generate insights from test results

## Project structure

- **drafts/** — One file per test (same name). Test definition in Markdown (hypothesis, metrics, variants).
- **results/** — One file per test (same name). Results in CSV or a short summary in Markdown.
- **decisions/** — One file per test (same name). Decision memo with: test name, area, decision (go/no-go), primary metric + outcome, why, what we learned, next steps.

Same name across drafts, results, and decisions so each test stays linked. You can extend this structure (e.g. experiment log, more folders) and keep iterating.

## How to use

1. Add your test data
2. Run the analyzer
3. Review the insights
