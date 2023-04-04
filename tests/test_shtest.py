import pytest
from sphinxcontrib.shtest import ShTest, ShTestError


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
