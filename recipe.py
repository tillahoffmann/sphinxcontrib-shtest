from cook import create_task
from cook.contexts import create_group


create_task(
    "pip:compile",
    action="pip-compile -v --resolver=backtracking",
    targets=["requirements.txt"],
    dependencies=["requirements.in", "setup.py"],
)
create_task("pip:sync", dependencies=["requirements.txt"], action="pip-sync")

with create_group("build"):
    create_task(
        "docs:shtest",
        action="rm -rf docs/_build && sphinx-build -b shtest . docs/_build",
    )
    create_task("docs:html", action="sphinx-build -W . docs/_build")
    create_task("lint", action="black --check .")
    create_task(
        "tests",
        action="pytest -v --cov=sphinxcontrib.shtest --cov-report=term-missing "
        "--cov-report=html --cov-fail-under=100",
    )
    sdist = create_task("package:sdist", action="python setup.py sdist")
    create_task(
        "package:check",
        dependencies=[sdist],
        action="twine check --strict dist/*.tar.gz",
    )
