import colorama
from pathlib import Path
import pytest
import shutil
from sphinx.application import Sphinx
from sphinxcontrib.shtest import ShTest, ShTestError, strip_colors
from typing import Optional


@pytest.mark.parametrize("test, match", [
    (ShTest("true", ""), None),
    (ShTest("false", "", 1), None),
    (ShTest("true", "", 1), "Expected return code: 1"),
    (ShTest("false", ""), "Expected return code: 0"),
    (ShTest("echo hello", "hello"), None),
    (ShTest("echo hello", "world"), r"Expected:\n\s+world"),
])
def test_shtest(test: ShTest, match: str) -> None:
    if match:
        with pytest.raises(ShTestError, match=match):
            test.run()
    else:
        test.run()


def test_strip_colors() -> None:
    colored = f"{colorama.Fore.GREEN}hello {colorama.Fore.RED}world{colorama.Fore.RESET}"
    assert strip_colors(colored) == "hello world"


@pytest.mark.parametrize("document_name, match", [
    ("true", None),
    ("false", "Expected return code: 0"),
    ("false-1-tempdir", None),
    ("multiple", None),
    ("no-command", "Expected a command starting with"),
    ("tempdir-and-cwd", "`cwd` and `tempdir` cannot"),
    ("cwd", None),
    ("sh", None),
])
@pytest.mark.parametrize("builder", ["html", "shtest"])
def test_directive_build(tmp_path: Path, document_name: str, match: Optional[str], builder: str) \
        -> None:
    # Copy data to a temporary directory and add a header.
    (tmp_path / "conf.py").write_text("extensions = ['sphinxcontrib.shtest']")
    document = (Path(__file__).parent / "rst" / document_name).with_suffix(".rst")

    text = document.read_text()
    (tmp_path / "index.rst").write_text("\n".join([
        document_name,
        "=" * len(document_name),
        "",
        text
    ]))

    # Run the builder.
    outdir = tmp_path / "_build"
    app = Sphinx(tmp_path, tmp_path, outdir, tmp_path / "doctreedir", builder)
    if match and builder == "shtest":
        with pytest.raises(ShTestError, match=match):
            app.build()
    else:
        app.build()
        if builder == "html":
            # Copy the result to the output directory for inspection.
            html = Path(__file__).parent / "html"
            html.mkdir(exist_ok=True)
            html = (html / document_name).with_suffix(".html")
            shutil.copy(outdir / "index.html", html)
