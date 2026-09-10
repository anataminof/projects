"""Bootstrap test to verify pytest is working."""


def test_bootstrap():
    """Verify pytest is configured correctly."""
    assert True


def test_imports():
    """Verify FastAPI can be imported."""
    from fastapi import FastAPI
    app = FastAPI()
    assert app is not None
