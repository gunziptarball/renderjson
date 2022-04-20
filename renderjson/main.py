import json
import pathlib
import sys

import jinja2
import typer

app = typer.Typer(name="renderjson", no_args_is_help=True)


@app.command(name="renderjson")
def main(
    template: str,
    vault: str = typer.Option(
        None, "-v", "--vault", help="vault secret to render with"
    ),
    vault_url: str = typer.Option(
        None, "--vault-url", envvar="VAULT_URL", show_envvar=True
    ),
    vault_token_path: pathlib.Path = typer.Option(
        pathlib.Path.home() / ".vault-token", "--vault-token"
    ),
    strip: bool = typer.Option(False, "-s", "--strip", help="strip newline at end"),
):
    """
    Render a Jinja2 template with some JSON (or from a vault secret)
    """
    p = pathlib.Path(template)
    if p.is_file():
        template = p.read_text()
    if vault is not None:
        data: dict = _data_from_vault(vault, vault_url, vault_token_path)["data"]
        data["data"] = data
    else:
        data: dict = json.load(sys.stdin)
    typer.echo(jinja2.Template(template).render(**data), nl=not strip)


def _data_from_vault(vault, vault_url, vault_token_path) -> dict:
    import hvac

    token = vault_token_path.read_text().strip()
    vault_client = hvac.Client(url=vault_url, token=token)
    return vault_client.read(vault)
