# Claude Submission Checklist

## Before submission

- Public repository is `https://github.com/Lemonbrand/make-brand-assets-for-me`.
- `.claude-plugin/marketplace.json` validates.
- `plugins/make-brand-assets-for-me/.claude-plugin/plugin.json` validates.
- The five skill folders are inside the plugin and do not reference files outside it.
- The install commands work from a clean Claude Code session.
- The MIT license, privacy URL, terms URL, support email, and repository URL are visible.

## Test

```text
/plugin marketplace add Lemonbrand/make-brand-assets-for-me
/plugin install make-brand-assets-for-me@lemonbrand
/reload-plugins
```

Run one request for each of the seven skills. Confirm that the plugin does not trigger for the three negative cases in `distribution/openai/test-cases.json`.

## Submit

Use Anthropic's public plugin submission form. Paste the copy from `distribution/claude/listing.md`, choose the public GitHub repository, and keep the submission confirmation with the release notes.
