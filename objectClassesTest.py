"""
A short tour of pytest's main features.

Run it from this folder with:
    pytest objectClassesTest.py            # run everything
    pytest objectClassesTest.py -v         # verbose: show each test name + result
    pytest objectClassesTest.py -k basic   # only tests whose name contains "basic"
    pytest objectClassesTest.py -x         # stop at the first failure
    pytest objectClassesTest.py -s         # don't capture stdout (let print() show)

pytest discovers tests automatically: files named test_*.py / *_test.py,
functions named test_*, and classes named Test* (with no __init__).
"""

import pytest


# ---------------------------------------------------------------------------
# 1. THE PLAIN ASSERT
# pytest uses Python's built-in `assert`. No special assertEqual methods.
# On failure it rewrites the assert to show you the actual values involved.
# ---------------------------------------------------------------------------
def test_basic_assert():
    result = 2 + 3
    assert result == 5


# ---------------------------------------------------------------------------
# 2. TESTING FOR EXCEPTIONS
# `pytest.raises` asserts that a block raises the expected exception.
# `match=` additionally checks the error message against a regex.
# The test FAILS if the exception is NOT raised.
# ---------------------------------------------------------------------------
def test_raises_exception():
    with pytest.raises(ZeroDivisionError):
        1 / 0

    with pytest.raises(ValueError, match="invalid literal"):
        int("not a number")


# ---------------------------------------------------------------------------
# 3. APPROXIMATE COMPARISONS
# Floating-point math is imprecise, so `pytest.approx` compares within a
# tolerance instead of demanding exact equality.
# ---------------------------------------------------------------------------
def test_approx():
    assert 0.1 + 0.2 == pytest.approx(0.3)


# ---------------------------------------------------------------------------
# 4. PARAMETRIZE — run the SAME test with MANY inputs
# Each tuple becomes a separate test case (and shows up separately in -v),
# so one failing input doesn't hide the others.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "value, expected",
    [
        (2, 4),
        (3, 9),
        (4, 16),
        (5, 25),
    ],
)
def test_squares(value, expected):
    assert value * value == expected


# ---------------------------------------------------------------------------
# 5. FIXTURES — reusable setup (and teardown)
# A fixture is a function that builds something a test needs. A test just
# names it as an argument and pytest injects the return value.
# Code after `yield` runs as teardown once the test finishes.
# ---------------------------------------------------------------------------
@pytest.fixture
def sample_list():
    data = [1, 2, 3]          # setup: runs before the test
    yield data                # the value handed to the test
    data.clear()              # teardown: runs after the test


def test_fixture_usage(sample_list):
    sample_list.append(4)
    assert sample_list == [1, 2, 3, 4]


# ---------------------------------------------------------------------------
# 6. FIXTURE SCOPE
# `scope` controls how often a fixture is rebuilt: "function" (default, once
# per test), "class", "module" (once per file), or "session" (once per run).
# Great for expensive setup like a DB connection you want to share.
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def shared_config():
    return {"balloons": 10, "max_pumps": 100}


def test_config_reads(shared_config):
    assert shared_config["balloons"] == 10


# ---------------------------------------------------------------------------
# 7. MARKERS — tag tests to select or alter behavior
# ---------------------------------------------------------------------------

# skip: never run this test.
@pytest.mark.skip(reason="feature not implemented yet")
def test_not_ready():
    assert False

# skipif: skip only when a condition holds (e.g. Python version, OS).
@pytest.mark.skipif(pytest.__version__ < "1.0", reason="needs modern pytest")
def test_conditional():
    assert True

# xfail: we KNOW this fails. It's reported as "xfail" (expected failure),
# not as an error. If it unexpectedly passes, it shows as "xpass".
@pytest.mark.xfail(reason="known bug in the math")
def test_known_bug():
    assert 1 + 1 == 3

# custom marker: tag a group of tests, then run just them with
#   pytest -m slow
# (Register custom markers in pytest.ini to avoid warnings.)
@pytest.mark.slow
def test_tagged():
    assert sum(range(1000)) == 499500


# ---------------------------------------------------------------------------
# 8. GROUPING TESTS IN A CLASS
# Class named Test* groups related tests. Handy for shared organization;
# fixtures can be scoped to the class too.
# ---------------------------------------------------------------------------
class TestBalloonMath:
    def test_inflate_increases(self):
        size = 0
        size += 5
        assert size == 5

    def test_pop_resets(self):
        size = 42
        size = 0
        assert size == 0


# ---------------------------------------------------------------------------
# 9. CAPTURING PRINTED OUTPUT
# The built-in `capsys` fixture captures stdout/stderr so you can assert on
# what your code printed. (Use `pytest -s` to see prints during a run.)
# ---------------------------------------------------------------------------
def test_capture_output(capsys):
    print("Balloon popped!")
    captured = capsys.readouterr()
    assert captured.out == "Balloon popped!\n"


# ---------------------------------------------------------------------------
# 10. TEMPORARY FILES/DIRS
# The `tmp_path` fixture gives each test a fresh, isolated temp directory
# (a pathlib.Path) that pytest cleans up automatically.
# ---------------------------------------------------------------------------
def test_tmp_path(tmp_path):
    f = tmp_path / "score.txt"
    f.write_text("100")
    assert f.read_text() == "100"


# ---------------------------------------------------------------------------
# NEXT STEP
# Once you fill in objectClasses.py with your balloon-game classes, import
# them here (e.g. `from objectClasses import Balloon`) and replace these
# demo asserts with real tests of that behavior.
# ---------------------------------------------------------------------------
