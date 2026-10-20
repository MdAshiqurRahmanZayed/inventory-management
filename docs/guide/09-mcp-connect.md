# Connect Claude to Your Inventory

Finished **[08-mcp-setup.md](08-mcp-setup.md)**? You should have an API key, be in the MCP User group, and have a connector set up for you. Now wire up a client.

**Don't have an API key yet?** See **[08-mcp-setup.md, step 2](08-mcp-setup.md#2-generate-yourself-an-odoo-api-key)** for the exact click-by-click flow (Settings > your profile > Account Security tab > New API Key > confirm your password > name it and pick a duration > copy the key shown — it's only shown once).

## Check the server is actually reachable first

```bash
curl http://localhost:8069/mcp/health
```
Should return `{"status": "ok", "server": "inventory-mcp", "version": "1.0.0"}`. If this fails, the connector problem is at the server/network level, not the client config below — fix this first.

## Claude Code

Add to the project's `.mcp.json` (keep this file out of version control — it has your API key in it):
```json
{
  "mcpServers": {
    "inventory": {
      "type": "http",
      "url": "http://localhost:8069/mcp/",
      "headers": { "Authorization": "Bearer <your-api-key>" }
    }
  }
}
```
Replace `<your-api-key>` with the key from step 2 of setup. Claude Code picks this up automatically — no restart needed, just start a new session in that project.

## Claude Desktop

Claude Desktop doesn't speak this HTTP transport directly — it needs a small bridge, [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) (requires Node.js installed). Add this to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "inventory": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8069/mcp/", "--header", "Authorization:Bearer <your-api-key>"]
    }
  }
}
```
Restart Claude Desktop after saving — it won't pick up config changes live.

(These two examples are kept identical, on purpose, to the ones in the main `README.md`'s MCP connector section — one source of truth for the JSON, so they don't quietly drift apart over time.)

## Troubleshooting

**Claude Desktop pops open a browser asking you to log in / authorize, instead of just connecting with your API key.** This is `mcp-remote` getting confused by a stale cached OAuth registration from a *previous* connection attempt to the exact same URL (possibly from a different project, if you've ever pointed it at `localhost:8069` before for something else). Fix: quit Claude Desktop, delete the matching files under `~/.mcp-auth/mcp-remote-v1/` for that URL (look for files whose content mentions `"issuer": "http://localhost:8069"`), reopen.

**Nothing happens / the assistant says it has no tools.** Re-check the health check above, and confirm the API key in your config is current (not an old, revoked one) and matches the format `Bearer <key>` exactly, including the space after "Bearer".
