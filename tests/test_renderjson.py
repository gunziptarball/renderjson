import json
import pathlib

import hvac
import pytest
from typer.testing import CliRunner

from renderjson import __version__, main


class TestApp:
    @pytest.fixture
    def token_path(self, tmpdir):
        path = pathlib.Path(tmpdir / ".vault-token")
        path.write_text("SECRET")
        return path

    @pytest.fixture
    def hvac_client(self, mocker, token_path):
        client_cls = mocker.patch.object(hvac, "Client")
        yield client_cls.return_value
        client_cls.assert_called_once_with(
            url="https://vault.your-org.com", token="SECRET"
        )

    @pytest.fixture
    def vault_secret(self, hvac_client, json_data) -> str:
        hvac_client.read.return_value = {
            "data": {"hyphenated-value": "ouch!", "underscored_value": "thank you."},
            "refresh_interval": "24h",
        }
        yield "secret/path"
        hvac_client.read.assert_called_once_with("secret/path")

    @pytest.fixture
    def cli_runner(self):
        return CliRunner()

    @pytest.fixture
    def json_data(self) -> str:
        return json.dumps({"foo": 1234, "bar": "baz", "bang": {"pow": "soda"}})

    @pytest.fixture
    def template_string(self) -> str:
        return "{{ foo + 1000 }} bottles of {{ bang.pow }} on the wall"

    @pytest.mark.parametrize("args", ([], ["--help"]))
    def test_help(self, cli_runner, args):
        result = cli_runner.invoke(main.app, args)
        assert result.stdout.startswith("Usage: renderjson")

    def test_render_from_stdin(self, cli_runner, json_data, template_string):
        result = cli_runner.invoke(
            app=main.app,
            args=[template_string],
            input=json_data,
        )
        assert result.exit_code == 0
        assert result.output == "2234 bottles of soda on the wall\n"

    @pytest.mark.parametrize("strip_newline", (True, False))
    def test_render_from_path(
        self, cli_runner, strip_newline, tmpdir, json_data, template_string
    ):
        template_path = pathlib.Path(tmpdir) / "template.jinja2"
        template_path.write_text(template_string)

        args = [str(template_path)]
        if strip_newline:
            args += ["-s"]

        result = cli_runner.invoke(main.app, args=args, input=json_data)

        assert result.exit_code == 0
        assert result.output == "2234 bottles of soda on the wall" + (
            "\n" if not strip_newline else ""
        )

    def test_render_from_vault_secret(self, vault_secret, cli_runner, token_path):
        result = cli_runner.invoke(
            main.app,
            args=[
                "-v",
                "secret/path",
                "--vault-url",
                "https://vault.your-org.com",
                "--vault-token",
                str(token_path),
                "Hyphens make me say \"{{ data['hyphenated-value'] }}\"  "
                "No hyphens please, and {{ underscored_value }}",
            ],
        )
        assert result.exit_code == 0
        assert (
            result.stdout
            == 'Hyphens make me say "ouch!"  No hyphens please, and thank you.\n'
        )


def test_version():
    assert __version__ == "0.1.0"
