# MCP under Agent Plugins 1.0.0

How this plugin declares MCP servers, and why `mcp.json` looks smaller than you
might expect.

Spec: <https://agent-plugins.org/specification> ·
schema: <https://agent-plugins.org/schemas/1.0.0/mcp.schema.json>

## Where MCP config lives

| File | Read by | Servers |
|---|---|---|
| `mcp.json` | any conformant Agent Plugins client | `gcloud` |
| `.mcp.json` | Claude Code | `gcloud`, `toolbox` |
| `mcp_config.json` | Antigravity | `gcloud`, `toolbox` |
| `gemini-extension.json` | Gemini CLI extension runtime | `gcloud`, `toolbox` |

`mcp.json` is the portable one and is deliberately a **subset**. `make manifest`
fails the build if it ever declares a server the harness manifests don't have,
or if a shared server's `command` drifts.

## Two rules that shape the file

**1. Only two placeholders expand.**

`${PLUGIN_ROOT}` and `${PLUGIN_DATA}` are substituted in `args`, `env` values and
`cwd`. *Every other `${...}` is passed through literally* — it is not an
environment-variable reference. So this, which reads correctly:

```json
"env": { "CLOUDSDK_CORE_PROJECT": "${GCP_PROJECT_ID}" }
```

…would set the project to the literal 18-character string `${GCP_PROJECT_ID}`,
and every gcloud call would fail against a project that cannot exist.

`mcp.json` therefore declares **no `env` at all**. Clients may pass the ambient
environment through to subprocesses, and `gcloud-mcp` already reads both the
project and Application Default Credentials from it. Set them the normal way
before launching your client:

```bash
gcloud auth application-default login
export CLOUDSDK_CORE_PROJECT="your-project-id"
```

**2. Transport is explicit.** The schema discriminates on `type`, so a server
entry without `"type": "stdio"` (or `streamable-http`) matches no branch of the
`oneOf` and is skipped. Failures are isolated: a server that won't start does not
stop the plugin's skills from loading.

## Toolbox is an opt-in

The [GenAI Toolbox](https://mcp-toolbox.dev) server needs `--config <path>`
pointing at a `tools.yaml` that describes *your* databases. That path is
user-specific, and no Agent Plugins placeholder can express it — `${PLUGIN_ROOT}`
points at the installed plugin, which is the wrong place for user data.

Rather than ship a server guaranteed to fail on first run, `mcp.json` omits it.
Add it to your own client config when you need BigQuery, Cloud SQL, Spanner or
AlloyDB tools:

```json
{
  "mcpServers": {
    "toolbox": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@toolbox-sdk/server", "--stdio", "--config", "/absolute/path/to/tools.yaml"]
    }
  }
}
```

Verified 2026-07-23: `@toolbox-sdk/server` resolves, accepts stdio mode, and
validates its config path. Note the earlier `uvx toolbox-core` form is wrong —
that package ships no CLI.

If you want it self-contained instead, place `tools.yaml` in the client-managed
data directory and use `"--config", "${PLUGIN_DATA}/tools.yaml"`. That is
spec-legal and portable, but the server stays down until you put the file there.

## Verifying

```bash
make spec   # transport discriminator, closed field sets, placeholder expansion
uvx check-jsonschema \
  --schemafile https://agent-plugins.org/schemas/1.0.0/mcp.schema.json mcp.json
```
