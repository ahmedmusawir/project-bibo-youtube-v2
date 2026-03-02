# 04 — Streamlit App

Complete reference for the Streamlit UI layer. Covers page structure, session state, sidebar, real-time logging, and how the UI connects to the pipeline.

---

## App Structure

```
app/
├── main.py                  # Entry point / home page
├── state.py                 # Project state management (read/write config.json)
├── utils.py                 # Streamlit utility helpers
├── __init__.py
├── components/
│   ├── sidebar.py           # Shared sidebar component (rendered on every page)
│   └── __init__.py
└── pages/
    ├── 1_inputs.py          # Stage 0: Transcript input
    ├── 2_script.py          # Stage 1: Script generation + approval
    ├── 3_audio.py           # Stage 2: Audio synthesis + approval
    ├── 4_metadata.py        # Stage 3: Metadata generation + approval
    ├── 5_images.py          # Stage 4: Image prompts + image generation + approval
    ├── 6_video.py           # Stage 5: Video composition + approval
    └── __init__.py
```

**Launch command:**
```bash
streamlit run app/main.py
```

**Streamlit config:** `.streamlit/config.toml`
```toml
[server]
scriptRunnerTimeout = 0    # Disabled — transcription can take 10-30 min

[browser]
gatherUsageStats = false
```

---

## Session State

Streamlit's `st.session_state` is used for cross-page state. Key session state keys:

| Key | Type | Description |
|---|---|---|
| `current_project` | `str` | Name of the currently selected project |
| `project_selector` | `str` | Bound to the sidebar selectbox widget |
| `new_project_input` | `str` | Bound to the new project name text input |
| `_project_created` | `str` | Temporary flag set after project creation; triggers success toast on next render |
| `transcription_log` | `str` | Captured stdout from transcription run |
| `script_gen_log` | `str` | Captured stdout from script generation run |
| `audio_gen_log` | `str` | Captured stdout from audio synthesis run |
| `metadata_gen_log` | `str` | Captured stdout from metadata generation run |
| `image_prompt_log` | `str` | Captured stdout from image prompt generation run |
| `image_gen_log` | `str` | Captured stdout from image generation run |
| `video_gen_log` | `str` | Captured stdout from video composition run |
| `edit_mode` | `bool` | Script page edit mode toggle |

**Session state persistence:** Session state persists for the browser session only. It is lost on server restart or browser refresh. Pipeline output files (in `projects/`) persist independently.

---

## Sidebar Component — `app/components/sidebar.py`

The sidebar is rendered on every page via `render_sidebar()`. It provides:

### Project Selector
- Lists all projects from `projects/` directory via `list_projects()`
- Selectbox bound to `st.session_state.current_project`
- On change: updates `current_project` and calls `st.rerun()`
- If no projects exist: shows "No projects yet. Create one below!"

### Create New Project
- Expander: "➕ Create New Project"
- Text input for project name
- On "Create Project" button click:
  1. Calls `create_project(name)` — creates `projects/<name>/` + `config.json`
  2. Sets `st.session_state.current_project = name`
  3. Sets `st.session_state["_project_created"] = name` (for success toast)
  4. Calls `st.rerun()`
- After rerun: success toast appears above the expander
- Error handling: wraps in try/except, shows error + traceback in UI if creation fails

### Pipeline Navigation
Shown only when a project is selected. Displays pipeline stages with status icons:
- `✅` — stage output exists AND is approved
- `⚠️` — stage output exists but NOT approved
- `⭕` — stage output does not exist yet

Navigation uses `st.page_link()` to link to each page file.

---

## Page Architecture

Every page follows the same pattern:

```python
# 1. Add project root to sys.path (required for src/ imports)
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 2. Page config
st.set_page_config(page_title="...", page_icon="...", layout="wide")

# 3. Render shared sidebar
render_sidebar()

# 4. main() function with all page logic
def main():
    if not st.session_state.get("current_project"):
        st.warning("Please select a project")
        return
    # ... page content ...

main()
```

**Why `sys.path` manipulation?** Streamlit runs each page file as a script from its own directory. Adding `project_root` to `sys.path` ensures `from src.xxx import yyy` works correctly regardless of CWD.

---

## Real-Time Logging — `app/utils.py`

### `capture_stdout_to_streamlit(container, session_key)`

A context manager that intercepts `sys.stdout` during pipeline execution and streams each `print()` line to a Streamlit `st.empty()` container in real-time.

```python
log_container = st.empty()
with capture_stdout_to_streamlit(log_container, session_key="my_log"):
    some_pipeline_function(...)
```

**How it works:**
1. Creates a `StreamlitWriter` (subclass of `io.TextIOBase`)
2. Replaces `sys.stdout` with the writer
3. Each `write()` call appends the line to an internal list
4. Re-renders the entire accumulated log as a `st.code()` block on every new line
5. On exit: restores original `sys.stdout`; saves accumulated log to `st.session_state[session_key]`

**Why `st.code()` not `st.text()`?** Code blocks have monospace font and scroll, making them better for log output.

### `show_process_log(session_key, label)`

Renders the stored log in a collapsible expander. Called at the bottom of every page that runs a pipeline function.

```python
show_process_log("script_gen_log", "📋 Script Generation Log")
```

---

## Page-by-Page Reference

### `app/pages/1_inputs.py` — Inputs

**Two input modes (tabs):**

**Tab 1: Paste Text**
- `st.text_area` for raw content
- "💾 Save as Transcript" button → writes to `projects/<name>/0_transcript.txt`
- Shows character count

**Tab 2: YouTube URL**
- URL validation: checks for `youtube.com/watch` or `youtu.be/`
- "🎥 Transcribe Video" button (disabled if URL invalid)
- On click:
  1. Force-loads `.env` from project root with `override=True`
  2. Lazy-imports `src.transcription.transcribe_youtube_audio`
  3. Runs transcription inside `capture_stdout_to_streamlit` context
  4. On success: `st.rerun()` to show transcript preview
- Shows existing transcript preview if `0_transcript.txt` exists

---

### `app/pages/2_script.py` — Script

**Model Configuration Section:**
- AI model selector at top of page (below project header)
- Dropdown shows available summarization LLM models from `config.json`
- Save button appears when selection differs from current model
- Models: gemini-3-flash-preview, gemini-3-pro-preview, gemini-2.5-pro, gemini-2.5-flash

**Pre-generation state:**
- Shows transcript preview (word count + collapsible view)
- "🎬 Create YouTube Script" button → calls `summarize_transcript()`

**Post-generation state:**
- Shows script stats: words, characters, estimated duration (words/150)
- **View mode:** Renders script in styled HTML div with scroll
- **Edit mode:** `st.text_area` for direct editing + "💾 Save Changes" button
  - Saving resets approval if content changed
- **Regenerate:** Re-runs `summarize_transcript()`, resets approval
- **Approval section:** Approve / Revoke buttons

---

### `app/pages/3_audio.py` — Audio

**Prerequisites check:** Script must exist AND be approved.

**Voice Configuration Section:**
- Voice selector at top of page
- Dropdown shows available TTS voices from `config.json`
- Displays voice label and language
- Save button appears when selection differs from current voice
- Voices: Studio-O (Female), Studio-M (Male), Neural2-D (Male), Neural2-F (Female)

**Pre-generation state:**
- Shows script preview
- "🎵 Generate Audio" button → calls `synthesize_speech()`

**Post-generation state:**
- `st.audio()` player for in-browser playback
- Audio stats: file size, duration, voice used
- Regenerate button (resets approval)
- Approval section

---

### `app/pages/4_metadata.py` — Metadata

**Prerequisites check:** Script must exist AND be approved.

**Model Configuration Section:**
- AI model selector at top of page (below project header)
- Dropdown shows available prompting LLM models from `config.json`
- Note: "Used for generating titles, descriptions, hashtags, and thumbnails"
- Save button appears when selection differs from current model
- Models: gemini-3-flash-preview, gemini-2.5-pro, gemini-2.5-flash

**Pre-generation state:**
- "📋 Generate Metadata" button → calls `generate_metadata()`

**Post-generation state:**
- **Titles section:** Numbered list with 🔄 regenerate button in header
  - Individual regenerate: calls `regenerate_titles()`, keeps description/hashtags
- **Description section:** Code block with copy button, 🔄 regenerate button in header
  - Individual regenerate: calls `regenerate_description()`, keeps titles/hashtags
  - Edit expander: text area for manual editing + save button
- **Hashtags section:** Code block with copy button (space-separated)
- **Full regenerate button:** At bottom, regenerates all metadata sections
- **Approval section:** Approve / Revoke buttons

**YouTube Thumbnail Generation:**
- **Image model selector:** Dropdown for Imagen model selection
  - Shows: imagen-4.0-ultra-generate-001 (best for text), imagen-4.0-generate-001, imagen-4.0-fast-generate-001
  - Save button appears when selection differs from current
- **Generate button:** "🎨 Generate Thumbnail" → calls `create_thumbnail()`
  - Generates catchy text overlay using prompting LLM
  - Creates image prompt with text embedding instructions
  - Generates 16:9 thumbnail using selected Imagen model
- **Post-generation display:**
  - Full-width thumbnail preview
  - Shows embedded text overlay
  - View image prompt expander
  - Download button (PNG)
  - 🔄 Regenerate button
- **Generation log:** Collapsible expander shows AI generation process

---

### `app/pages/5_images.py` — Images

**Prerequisites check:** Script AND audio must exist AND be approved.

**Model Configuration Section:**
- **Image Prompt Generation Model:** Dropdown for prompting LLM selection
  - Models: gemini-3-flash-preview, gemini-2.5-pro, gemini-2.5-flash
  - Save button appears when selection differs from current
- **Image Generation Model:** Dropdown for Imagen model selection
  - Models: imagen-4.0-ultra-generate-001, imagen-4.0-generate-001, imagen-4.0-fast-generate-001
  - Save button appears when selection differs from current

**Two-step process:**

**Step 1: Image Prompts**
- "🎨 Generate Image Prompts" button → calls `generate_image_prompts()`
- Shows generated prompts with count and timing info
- Prompts are editable (saved back to `3_image_prompts.json`)

**Step 2: Image Generation**
- "🖼️ Generate Images" button → calls `create_images_from_prompts()`
- Shows image grid after generation
- Individual image regeneration (per-prompt)
- Approval section

---

### `app/pages/6_video.py` — Video

**Prerequisites check:** Audio AND images must exist AND be approved.

**Pre-generation state:**
- "🎬 Compose Video" button → calls `compose_video()`
- Warning: "10-15 minutes for longer videos"

**Post-generation state:**
- Video stats: file size, format
- Video player: `st.video(bytes)` — reads file bytes from project folder
- Download button: `st.download_button()` with `video/mp4` MIME type
- Regenerate button (resets approval)
- Approval section with congratulations message on approval

---

## Approval Flow

The approval system enforces sequential pipeline progression:

```
Script approved?
    → Audio page unlocked
Audio approved?
    → Images page unlocked
Images approved?
    → Video page unlocked
```

Metadata generation is independent — it only requires script approval and does not block any other stage.

Approvals are persisted in `projects/<name>/config.json` and survive server restarts.

---

## `app/state.py` — State Management

Pure Python module (no Streamlit dependency). Provides all project CRUD operations.

| Function | Description |
|---|---|
| `get_project_root()` | Returns `Path(__file__).resolve().parent.parent` — always the app root |
| `get_project_path(name)` | Returns `project_root / "projects" / name` |
| `list_projects()` | Returns sorted list of directory names in `projects/` |
| `create_project(name)` | Creates directory + default `config.json` |
| `load_project_config(name)` | Reads `config.json`; returns default dict if missing |
| `save_project_config(name, config)` | Writes `config.json` |
| `get_approval_status(name, stage)` | Returns bool from `config.approvals[stage]` |
| `set_approval(name, stage, approved)` | Updates and saves approval status |
| `stage_file_exists(name, stage)` | Checks if stage output file/dir exists |
| `get_stage_status(name, stage)` | Returns `{"exists": bool, "approved": bool}` |
| `get_all_stages_status(name)` | Returns status dict for all 5 stages |

**Stage-to-file mapping:**
```python
{
    "script":   "1_summary.txt",
    "audio":    "2_audio.mp3",
    "metadata": "4_metadata.json",
    "images":   "5_images",        # directory — checked for non-empty
    "video":    "6_final_video.mp4"
}
```
