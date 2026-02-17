"""
Utility helpers for the Streamlit app.
"""
import io
import sys
import contextlib
import streamlit as st


@contextlib.contextmanager
def capture_stdout_to_streamlit(container):
    """
    Context manager that captures print() output from pipeline functions
    and displays each line in a Streamlit container in real-time.

    Usage:
        log_container = st.empty()
        with capture_stdout_to_streamlit(log_container):
            some_pipeline_function(...)
    """
    class StreamlitWriter(io.TextIOBase):
        def __init__(self, container):
            self._container = container
            self._lines = []

        def write(self, text):
            if text and text.strip():
                self._lines.append(text.strip())
                # Show all accumulated lines as a code block
                self._container.code("\n".join(self._lines), language=None)
            return len(text) if text else 0

        def flush(self):
            pass

    writer = StreamlitWriter(container)
    old_stdout = sys.stdout
    sys.stdout = writer
    try:
        yield writer
    finally:
        sys.stdout = old_stdout
