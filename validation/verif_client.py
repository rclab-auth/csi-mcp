import json
import os
from contextlib import asynccontextmanager
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


class Server:

    # thin wrapper : every model change goes through the MCP tools, as Claude would do it

    def __init__(self, session):

        self.s = session
        self.calls = 0

    async def tool(self, tool_name, **kw):

        self.calls += 1
        res = await self.s.call_tool(tool_name, kw)
        text = res.content[0].text if res.content else ''

        if res.isError:
            raise RuntimeError(f'{tool_name} {kw} -> {text}')

        return json.loads(text) if text.startswith(('{', '[')) else text

    async def api(self, path, **args):

        res = await self.tool('call_api', path=path, args=args)

        if not res['ok']:
            raise RuntimeError(f'{path} {args} -> ret {res["ret"]}')

        return res['outputs']


@asynccontextmanager
async def server(product):

    entry = os.path.join(REPO, product, 'src', product.lower() + '_mcp.py')
    params = StdioServerParameters(command='uv', args=['run', '--script', entry])

    async with stdio_client(params) as (r, w):

        async with ClientSession(r, w) as s:
            await s.initialize()
            yield Server(s)


def compare(rows, name, quantity, got, expected, tol):

    # tol is the accepted relative difference, or the absolute one when the expected value is zero

    if expected == 0:
        diff = abs(got)
        ok = diff <= tol

    else:
        diff = got / expected - 1
        ok = abs(diff) <= tol

    rows.append({'example': name, 'quantity': quantity, 'mcp': got,
                 'published': expected, 'diff': diff, 'ok': ok})
    pct = f'{100 * diff:+.2f} %' if expected != 0 else f'abs {diff:.4g}'
    print(f'  {"OK  " if ok else "FAIL"} {quantity:<40} mcp {got:>12.5g}  published {expected:>12.5g}  {pct}', flush=True)


def save(rows, path):

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=1)
