# Start Here

## 1. Install it

Pick the host you use.

### ChatGPT — Best experience

Use ChatGPT when you want one visual conversation for references, image generation, review, and saved files.

```bash
codex plugin marketplace add Lemonbrand/make-brand-assets-for-me
```

Restart the desktop app. Open the Plugins Directory, choose Lemonbrand, and install Make Brand Assets For Me. Start a new task after installation.

### Claude Desktop

On a paid Claude plan, open **Customize → Plugins → + → Add marketplace → Add from a repository**. Paste `https://github.com/Lemonbrand/make-brand-assets-for-me`, add it, and install **Make Brand Assets For Me**.

### Claude Code (terminal)

```text
/plugin marketplace add Lemonbrand/make-brand-assets-for-me
/plugin install make-brand-assets-for-me@lemonbrand
```

### Agent Skills hosts

```bash
npx skills add Lemonbrand/make-brand-assets-for-me
```

## 2. Start

Say:

> Help me make my first brand asset.

The plugin will ask for approved examples and guide the first run.

## 3. Set up a brand

Put approved examples in your own project. Then say:

> Use $brand-assets-set-up to set up my brand from these examples.

Review the short brand summary before making images.

## 4. Make the first asset

Say:

> Use $brand-assets-make-one to make one transparent asset for human approval.

You should receive a PNG and an asset receipt.

## 5. Check it

Open the PNG at thumbnail size and full size. Compare it with the three approved examples named in the receipt.
