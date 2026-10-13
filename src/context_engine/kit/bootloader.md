<!-- context-engine kit 0.5 begin -->
framework: 0.5

This repo runs the context-engineering framework through `context-engine`. Its rules are the file
imported on the next line, which the framework owns: an upgrade replaces it whole, so it is never
edited here, and this repo's own rules go in this file, outside these markers. If those rules are
not in your context, read that file; if it is missing, run the engine's lint
(`<engine-python> -m context_engine lint`), which names the fix.

@docs/framework/contract.md
<!-- context-engine kit 0.5 end -->

## Gate

`<this repo's own test command> && context-engine lint`, from the repo root.
