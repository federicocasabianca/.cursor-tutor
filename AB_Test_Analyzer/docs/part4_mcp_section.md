# Part 4 — MCP (Model Context Protocol)

Article section for readers: what MCP is, why it's useful, how it differs from a typical API call, and an example with Statsig.

---

## What is MCP?

**MCP (Model Context Protocol)** is an open protocol that lets an AI assistant use external tools and resources during a conversation. In Cursor, you connect to **MCP servers** (e.g. Statsig, Notion, Jira). Each server exposes **tools** (actions the model can call, like "get experiment details" or "update a page") and optionally **resources** (read-only data the model can fetch). The model sees the list of available tools and their parameters; when you ask something in chat, it can decide to call one or more tools, use the results, and answer or do the next step.

So MCP is the layer between your chat and your company's systems: instead of you calling an API or opening a dashboard, you ask in natural language and the model uses the right tool and gives you the answer or performs the action.

---

## Why is it useful?

- **Live context.** The model can pull current data (e.g. list of experiments, experiment results, a Notion page) instead of relying only on what you pasted or what's in the repo. So you get answers that reflect the real state of your experiments or docs.
- **No re-explaining.** You don't have to describe your experiment setup or copy-paste IDs every time. You say "what's the status of the checkout button test?" and the model can call the right tool, get the data, and answer.
- **Pull and push in one place.** You can both read (get experiment list, get results) and write (update experiment, update a page) from the same chat. That supports a flow like: check results → decide → update the experiment or the log, without leaving the conversation.
- **One integration, same pattern.** Once you've connected one MCP server (e.g. Statsig), the pattern is clear: the model has tools to pull and push; you ask in natural language. You can reuse that mental model for other servers (Notion, Jira, etc.) later.

---

## How is it different from a typical API call?

| Typical API call | MCP in Cursor |
|------------------|----------------|
| You write code (script, app, or curl) that calls an endpoint with a specific URL, method, and payload. | You don't write code. You ask in chat (e.g. "list my experiments" or "update this experiment to decision_made"). |
| You decide which endpoint to call and what parameters to send. | The model sees the available tools (name, description, parameters) and decides which tool to call and with what arguments. |
| You handle the response (parse JSON, show it, act on it). | The model gets the tool result, interprets it, and answers or suggests the next step (e.g. "here are your experiments" or "I've updated the status; do you want to add a row to the experiment log?"). |
| You need docs, API keys, and a dev environment. | You (or your team) set up the MCP server once (e.g. Statsig MCP with credentials). After that, any chat in Cursor can use those tools; no code or curl from you. |

So the main difference is **who does the "integration" work**: with an API, you write and run the integration; with MCP, the model does the call on your behalf based on what you asked. You still need to connect the server and have the right permissions; you just don't write the call yourself.

---

## Example with Statsig

We use **Statsig** as the single integration example: experiments (and optionally gates, dynamic configs) live there, and the co-pilot can read and update them via MCP.

**What the Statsig MCP exposes (conceptually)**

- **List experiments** — Get the list of experiments (e.g. names, IDs, status). Useful for "what experiments do I have?" or "find the checkout experiment."
- **Get experiment details** — Get one experiment by ID: hypothesis, groups, metrics, status, etc. Useful for "what's the setup of experiment X?" or to prepare an update.
- **Get experiment results** — Get results for an experiment. Useful for "what are the results for X?" before writing a decision memo.
- **Update experiment** — Update an experiment (e.g. change status to "decision_made," update description or hypothesis). Useful for "mark this experiment as decision_made" or "update the hypothesis to …."

So the flow is: **pull** (list or get details/results) → use the answer in the conversation → **push** (update experiment or update your local decision memo / experiment log).

**Example prompts (Statsig MCP enabled)**

1. **Pull: list and inspect**
   - *"List my experiments in Statsig."*
   - *"Get the details of the experiment [name or ID]."*
   - *"What are the results for the checkout button color experiment?"*

2. **Use in conversation**
   - *"Using the results from Statsig for [experiment], draft the decision memo and save it to `decisions/<test_name>.md`."*  
   - The model can call get-results, then write the memo using the project structure and, if you have the decision-memo MDC, suggest adding a row to `experiment_log.md`.

3. **Push: update in Statsig**
   - *"Mark the experiment [name/ID] as decision_made in Statsig."*
   - *"Update the experiment [name/ID]: set status to decision_made and add a short description of the outcome."*

4. **End-to-end**
   - *"List experiments that are still active. For the checkout button test, get the results, draft the decision memo in `decisions/checkout_button_color_test.md`, and then mark the experiment as decision_made in Statsig."*

**What you need**

- Statsig MCP server configured in Cursor (and any required credentials).
- Your experiment names or IDs so you can refer to them in chat (the model can use "list experiments" to find them if you don't remember the ID).

**What you get**

- No switching to the Statsig dashboard or writing scripts to fetch/update. You ask; the model calls the right tool and reports back or performs the update. Same pattern for other MCP servers (e.g. Notion): pull company context, use it in the chat, push updates when you're ready.

**Try these once MCP is configured**

Copy-paste these into chat (replace the experiment name with one you have in Statsig):

1. *"How is the checkout button color experiment doing? Give me status and results."*  
   The model can list or fetch that experiment and return status plus a short summary of results.

2. *"List my experiments in Statsig and tell me which ones are still running."*  
   You get a list and a filter on active/running experiments.

3. *"What’s the current status of [experiment name] in Statsig — setup, primary metric, and latest results?"*  
   You get details and results in one answer.

4. *"Is there an experiment on [topic, e.g. checkout or homepage]? If yes, how is it doing?"*  
   The model can search the list by name/topic and then report status and results.

---

## Step-by-step: configuring an MCP server

You need two things: a **config file** that tells Cursor how to run or reach the MCP server, and **credentials or access** on the third-party side (Statsig, Notion, etc.). The config is the same kind of file for every server; what you do in the third-party tool depends on the tool.

### 1. Where the config lives

- **Project-level:** `.cursor/mcp.json` in the project root. Good when you want the same MCP setup for everyone on the repo (e.g. "this project uses Statsig MCP"). Credentials should not go in this file if the repo is shared — use env vars or a global config for secrets.
- **Global (user):** `~/.cursor/mcp.json` (macOS/Linux) or the path Cursor uses on your OS for user config. Good for credentials and for servers you use across all projects (e.g. your Notion or Statsig).

You can use both: project config for which servers to use, global for secrets; or put everything in one place if you prefer.

### 2. What goes in `mcp.json`

The file has a single object with a key `mcpServers`. Each server has a name (e.g. `statsig`, `notion`) and a config that tells Cursor how to start or connect to it.

**Local server (command/stdio)** — Cursor runs a command (e.g. `npx` or `python`); the process speaks MCP over stdio. You need the server package or script installed.

```json
{
  "mcpServers": {
    "statsig": {
      "command": "npx",
      "args": ["-y", "@statsig/mcp-server"],
      "env": {
        "STATSIG_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

- **command** — The executable (e.g. `npx`, `python`).
- **args** — Arguments (e.g. package name for npx, or path to a Python script).
- **env** — Environment variables the server needs. Use this for API keys or secrets; avoid committing real keys if the file is in the repo.

**Remote server (HTTP)** — Some MCP servers run elsewhere and expose an HTTP endpoint. In that case the config uses a URL and possibly headers for auth (exact shape depends on Cursor’s version; check the docs for your server).

### 3. What to do on the third-party tool

Each tool is different, but the idea is the same: the MCP server will call that tool’s API on your behalf, so the API must allow your credentials to do what you need.

- **Statsig:** Create an API key in the Statsig console (or your org’s settings) with permissions to read and, if you want updates from Cursor, write experiments. Put that key in the `env` block (e.g. `STATSIG_API_KEY`) in `mcp.json`. The exact key name depends on the Statsig MCP server you use.
- **Notion:** Typically OAuth or an integration token. Create an integration in Notion, get the token, and (if required) share the pages or databases you care about with that integration. Put the token in `env` as the Notion MCP server expects.
- **Others (Jira, Slack, etc.):** Same pattern: create an app or token in the third-party product with the right scopes, then pass it via `env` (or the config the server documents).

So: **in Cursor you define *how* to run the MCP server and what env to pass; in the third-party tool you create the key/token and permissions.** The MCP server’s docs will say which env vars it needs and what permissions the key must have.

### 4. Apply and restart

- Save `mcp.json` (in the project or in your user directory, depending on where you put it).
- **Restart Cursor fully** — MCP servers are loaded at startup, so a full restart is needed for new or changed config to take effect.
- After restart, the new server should appear in Cursor’s MCP/tools list, and the model will be able to call its tools when you chat.

### Quick checklist

1. Create or edit `mcp.json` (project: `.cursor/mcp.json` or user config path).
2. Add the server under `mcpServers` with `command`/`args` (and `env` for secrets) or the HTTP config if applicable.
3. In the third-party tool (Statsig, Notion, etc.), create the API key or token with the right permissions.
4. Put the key/token in `env` in `mcp.json` (or in your environment if the server reads from there).
5. Restart Cursor and confirm the server is available.

---

## Conclusion

That’s it for this part: you have project rules (`.cursorrules` and MDC), live data via MCP, and one integration (e.g. Statsig) so you can ask in chat instead of switching context. In the next article we’ll put it together—combine MCP and MDC in a single flow—and use **skills** to turn repeated actions into one-step commands so you don’t have to spell everything out each time.
