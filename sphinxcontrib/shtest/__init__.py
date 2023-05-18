from __future__ import annotations
import doctest
from docutils.nodes import document, literal_block, Node
from docutils.parsers.rst import directives
from pathlib import Path
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.environment import BuildEnvironment
from sphinx.errors import SphinxError
from sphinx.util.docutils import SphinxDirective
from sphinx.util.logging import getLogger
import subprocess
import tempfile
import textwrap
import types
from typing import Iterable, List, Optional


LOGGER = getLogger(__name__)


class ShTest:
    """
    Shell test.

    Args:
        command: Command to execute.
        want: Expected output.
        want_returncode: Expected returncode.
        stderr: Read from stderr instead of stdout.
        source: Source file in which the test is declared.
        lineno: Line number where the test is declared.
        cwd: Working directory.
        tempdir: Use a temporary working directory.
    """
    def __init__(self, command: str, want: str, want_returncode: int = 0,
                 stderr: bool = False, source: Optional[str] = None, lineno: Optional[int] = None,
                 cwd: Optional[str] = None, tempdir: bool = False) -> None:
        self.command = command
        self.want = want if want.endswith("\n") else want + "\n"
        self.want_returncode = want_returncode
        self.stderr = stderr
        self.source = source
        self.lineno = lineno
        self.cwd = cwd
        self.tempdir = tempdir

        if self.cwd and self.tempdir:
            raise ShTestError(f"{self.format_location(self.source, self.lineno)}\n`cwd` and "
                              "`tempdir` cannot be used together")

        # Resolve the working directory relative to the source document.
        if self.source and self.cwd:
            self.cwd = (Path(self.source).parent / self.cwd).resolve()
        elif self.source:
            self.cwd = Path(self.source).parent

    def run(self) -> None:
        kwargs = {
            "args": self.command,
            "text": True,
            "shell": True,
            "stderr" if self.stderr else "stdout": subprocess.PIPE,
        }
        process: subprocess.CompletedProcess
        if self.tempdir:
            with tempfile.TemporaryDirectory() as tempdir:
                process = subprocess.run(**kwargs, cwd=tempdir)
        else:
            process = subprocess.run(**kwargs, cwd=self.cwd)
        got = strip_colors(process.stderr if self.stderr else process.stdout)

        # Create a prefix for messages.
        parts = [
            self.format_location(self.source, self.lineno),
            "Failed sh test:",
            textwrap.indent(self.command, "    "),
        ]
        failed = False

        # Check the output.
        optionflags = doctest.COMPARISON_FLAGS
        checker = doctest.OutputChecker()
        if not checker.check_output(self.want, got, optionflags):
            example = types.SimpleNamespace(want=self.want)
            diff = checker.output_difference(example, got, optionflags)
            parts.append(diff)
            failed = True

        # Check the status code.
        if process.returncode != self.want_returncode:
            parts.append(f"Expected return code: {self.want_returncode}\nGot: {process.returncode}")
            failed = True
        if failed:
            raise ShTestError("\n".join(parts))

    @classmethod
    def from_node(cls, node: Node) -> Iterable[ShTest]:
        """
        Iterate over all sub-tests of a given node.
        """
        kwargs = {
            "stderr": node["stderr"],
            "source": node.source,
            "cwd": node["cwd"],
            "tempdir": node["tempdir"],
            "want_returncode": node["returncode"],
        }
        command = None
        want = None
        lineno = node["lineno"]
        for i, line in enumerate(node.astext().splitlines()):
            # This line starts a new command.
            if line.startswith("$"):
                # If a command is already active, yield it.
                if command:
                    yield ShTest(command, "\n".join(want), lineno=lineno, **kwargs)
                command = line.lstrip("$ ")
                want = []
            elif command:
                want.append(line)
            elif i == 0 and line.startswith("#"):
                pass  # We ignore a first line that starts with a comment character.
            else:
                raise ShTestError(f"{cls.format_location(node.source, lineno)}\nExpected a command "
                                  f"starting with `$` but got `{line}`")
            lineno += 1
        yield ShTest(command, "\n".join(want), lineno=lineno, **kwargs)

    @classmethod
    def format_location(cls, source: str, lineno: int) -> str:
        return f"File \"{source}\", line {lineno}"


class ShTestError(SphinxError):
    category = 'ShTest error'


class ShTestDirective(SphinxDirective):
    has_content = True
    option_spec = {
        "returncode": int,
        "stderr": directives.flag,
        "cwd": str,
        "tempdir": directives.flag,
    }

    def run(self) -> List[Node]:
        # Display the content unchanged but set attributes on the literal block. We will use these
        # attributes to construct test objects.
        content = '\n'.join(self.content)
        node = literal_block(
            content, content, shtest=True, language="bash", lineno=self.lineno,
            stderr="stderr" in self.options, cwd=self.options.get("cwd"),
            returncode=self.options.get("returncode", 0), tempdir="tempdir" in self.options,
        )
        return [node]


class ShDirective(SphinxDirective):
    """
    Displays shell command output in the documentation.
    """
    required_arguments = 1
    optional_arguments = float("inf")
    has_content = False
    option_spec = {
        "stderr": directives.flag,
        "hide-cmd": directives.flag,
        "cwd": str,
    }

    def run(self) -> List[Node]:
        # Run the command and display the output.
        parent = Path(self.state.document["source"]).parent
        cwd = (parent / cwd) if (cwd := self.options.get("cwd")) else parent
        stderr = "stderr" in self.options
        args = " ".join(self.arguments)
        kwargs = {
            "args": args,
            "shell": True,
            "text": True,
            "stderr" if stderr else "stdout": subprocess.PIPE,
        }
        process = subprocess.run(**kwargs)
        content = process.stderr if stderr else process.stdout
        if "hide-cmd" not in self.options:
            content = f"$ {args}\n{content}"
        node = literal_block(content, content, language="bash")
        return [node]


class ShTestBuilder(Builder):
    """
    Runs shell command test snippets in the documentation.
    """
    name = "shtest"

    def __init__(self, app: Sphinx, env: BuildEnvironment = None) -> None:
        super().__init__(app, env)
        self.passed = []
        self.failed = []

    def write_doc(self, docname: str, doctree: document) -> None:
        # Iterate over all nodes and process them.
        nodes = doctree.findall(lambda node: isinstance(node, literal_block)
                                and node.attributes.get("shtest"))
        for node in nodes:
            for test in ShTest.from_node(node):
                test.run()

    def get_outdated_docs(self) -> str | Iterable[str]:
        return self.env.found_docs

    def prepare_writing(self, docnames: set[str]) -> None:
        pass

    def get_target_uri(self, docname: str, typ: str = None) -> str:  # pragma: no cover
        return ""


def setup(app: Sphinx) -> None:
    app.add_directive("sh", ShDirective)
    app.add_directive("shtest", ShTestDirective)
    app.add_builder(ShTestBuilder)


def strip_colors(text: str) -> str:
    try:
        import colorama

        for ansi_codes in [colorama.Fore, colorama.Back]:
            for code in vars(ansi_codes).values():
                text = text.replace(code, "")
        return text
    except ImportError:  # pragma: no cover
        return text
