"""
Utility helpers for the Streamlit app.
"""
import io
import sys
import contextlib
import streamlit as st


@contextlib.contextmanager
def capture_stdout_to_streamlit(container, session_key=None):
    """
    Context manager that captures print() output from pipeline functions
    and displays each line in a Streamlit container in real-time.
    Optionally stores the captured log in st.session_state[session_key].

    Usage:
        log_container = st.empty()
        with capture_stdout_to_streamlit(log_container, session_key="my_log"):
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

        def get_log(self):
            return "\n".join(self._lines)

    writer = StreamlitWriter(container)
    old_stdout = sys.stdout
    sys.stdout = writer
    try:
        yield writer
    finally:
        sys.stdout = old_stdout
        if session_key and writer._lines:
            st.session_state[session_key] = writer.get_log()


def show_process_log(session_key, label="📋 Process Log"):
    """
    Display a stored process log in a collapsible expander.
    Call this on every page that runs a pipeline function.
    """
    if session_key in st.session_state and st.session_state[session_key]:
        with st.expander(label, expanded=False):
            st.code(st.session_state[session_key], language=None)
