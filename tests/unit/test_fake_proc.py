"""Tests for the FakePopen fixture."""

from tests.fixtures.fake_proc import FakePopen


def test_default_state_is_alive_and_pending():
    p = FakePopen(returncode=0, stdout="ok", stderr="")
    assert p.poll() is None
    assert p.is_alive() is True


def test_terminate_marks_dead_and_increments_counter():
    p = FakePopen(returncode=0, stdout="", stderr="")
    p.terminate()
    assert p.terminate_calls == 1
    assert p.kill_calls == 0
    assert p.is_alive() is False


def test_kill_marks_dead_and_increments_counter():
    p = FakePopen(returncode=0, stdout="", stderr="")
    p.kill()
    assert p.kill_calls == 1
    assert p.terminate_calls == 0
    assert p.is_alive() is False


def test_communicate_returns_configured_io():
    p = FakePopen(returncode=2, stdout="hello", stderr="warn")
    out, err = p.communicate()
    assert out == "hello"
    assert err == "warn"


def test_poll_returns_returncode_after_dead():
    p = FakePopen(returncode=3, stdout="", stderr="")
    p.terminate()
    assert p.poll() == 3


def test_terminal_call_after_dead_is_noop_for_counters_but_idempotent():
    p = FakePopen(returncode=0, stdout="", stderr="")
    p.terminate()
    p.terminate()
    p.kill()
    assert p.terminate_calls == 2
    assert p.kill_calls == 1
