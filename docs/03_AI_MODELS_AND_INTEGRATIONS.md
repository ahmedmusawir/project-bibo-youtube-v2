# 03 — AI Models and Integrations

Complete reference for every AI service VidGen connects to, how authentication works, which models are active, and what alternate routes exist.

---

## Authentication Architecture

All Google Cloud services use **Application Default Credentials (ADC)**. The service account JSON file is the single credential for all Google services.

```
GOOGLE_APPLICATION_CREDENTIALS=/path/to/cyberize-vertex-api.json
```

This one credential covers:
- Google Cloud Speech-to-Text
- Google Cloud Text-to-Speech
- Google Cloud Storage (for STT audio staging)
- Google Vertex AI (Imagen image generation)

The Gemini LLM (via `langchain-google-genai`) uses a separate **API key**:
```
GOOGLE_API_KEY=your_gemini_api_key
```

---

## Active AI Services

### 1. Google Gemini LLM — Script Generation

| Property | Value |
|---|---|
| **Library** | `langchain-google-genai` → `ChatGoogleGenerativeAI` |
| **Auth** | `GOOGLE_API_KEY` |
| **Module** | `src/summarization.py` |
| **Default model** | `gemini-3-flash-preview` (set in `config/config.json`) |
| **Temperature** | `0.5` |
| **max_output_tokens** | NOT SET — uses model default (prevents truncation) |
| **Chain type** | `create_stuff_documents_chain` (LangChain) |

**Available models (switchable via UI):**
```json
["gemini-3-flash-preview", "gemini-3-pro-preview", "gemini-2.5-pro", "gemini-2.5-flash"]
```

**How to switch:** Change `llm_summarization.current` in `config/config.json`, or use the model selector in the Streamlit UI (Script page settings).

---

### 2. Google Gemini LLM — Metadata + Image Prompts

| Property | Value |
|---|---|
| **Library** | `langchain-google-genai` → `ChatGoogleGenerativeAI` |
| **Auth** | `GOOGLE_API_KEY` |
| **Modules** | `src/metadata_generation.py`, `src/image_prompting.py` |
| **Default model** | `gemini-2.5-flash` (set in `config/config.json`) |
| **Temperature** | `0.8` |
| **Chain type** | LCEL: `prompt \| llm \| StrOutputParser()` |

**Available models (switchable via UI):**
```json
["gemini-3-flash-preview", "gemini-2.5-pro", "gemini-2.5-flash"]
```

**Note:** A separate `llm_prompting` config key exists for metadata/image prompting, independent of the summarization LLM. This allows using a faster/cheaper model for prompting while using a more capable model for script generation.

---

### 3. Google Cloud Speech-to-Text

| Property | Value |
|---|---|
| **Library** | `google-cloud-speech` |
| **Auth** | ADC via `GOOGLE_APPLICATION_CREDENTIALS` |
| **Module** | `src/transcription.py` |
| **API** | `long_running_recognize` (async) |
| **Model** | `latest_long` (optimized for long-form content) |
| **Encoding** | FLAC, 16kHz, mono |
| **Timeout** | 3600 seconds (60 minutes) |
| **GCS staging** | Always required — audio is always uploaded to GCS before transcription |

**GCS bucket:** Set via `GOOGLE_STT_BUCKET` env var. The bucket must exist and the service account must have `storage.objects.create` and `storage.objects.delete` permissions.

**Staging file lifecycle:**
1. FLAC file uploaded to `gs://<bucket>/transcription-temp/<uuid>.flac`
2. STT operation runs against GCS URI
3. FLAC blob deleted after transcription completes

---

### 4. Google Cloud Text-to-Speech

| Property | Value |
|---|---|
| **Library** | `google-cloud-texttospeech` |
| **Auth** | ADC via `GOOGLE_APPLICATION_CREDENTIALS` |
| **Module** | `src/text_to_speech.py` |
| **API** | `synthesize_speech` (synchronous, chunked) |
| **Output format** | MP3 |
| **Chunk limit** | 4500 characters per API call |

**Default voice:** `en-US-Neural2-D` (Male, Neural2 quality)

**Available voices (switchable via UI):**
```json
[
  {"id": "en-US-Studio-O",  "label": "Female (Studio-O)", "lang": "en-US"},
  {"id": "en-US-Studio-M",  "label": "Male (Studio-M)",   "lang": "en-US"},
  {"id": "en-US-Neural2-D", "label": "Male (Neural2-D)",  "lang": "en-US"},
  {"id": "en-US-Neural2-F", "label": "Female (Neural2-F)","lang": "en-US"}
]
```

**Voice tiers:**
- **Studio voices** (`Studio-O`, `Studio-M`): Highest quality, most natural. Higher cost.
- **Neural2 voices** (`Neural2-D`, `Neural2-F`): High quality, slightly lower cost.

**How to switch:** Change `tts.current_voice` and `tts.current_lang` in `config/config.json`, or use the voice selector in the Streamlit UI (Audio page settings).

**Full voice list:** See `docs/vertex_voice_list.txt` for all available Google TTS voices.

---

### 5. Google Vertex AI — Imagen 4 (Image Generation)

| Property | Value |
|---|---|
| **Library** | `vertexai`, `google-cloud-aiplatform` |
| **Auth** | ADC via `GOOGLE_APPLICATION_CREDENTIALS` |
| **Module** | `src/image_creation.py` |
| **API** | `ImageGenerationModel.generate_images()` |
| **Aspect ratio** | `16:9` |
| **Watermark** | `add_watermark=False` |
| **Images per prompt** | 1 |
| **Output format** | PNG |

**Default model:** `imagen-4.0-ultra-generate-001`

**Available models (switchable via UI):**
```json
["imagen-4.0-ultra-generate-001", "imagen-4.0-generate-001", "imagen-4.0-fast-generate-001"]
```

**Model tiers:**
- `ultra`: Highest quality, slowest, most expensive
- `generate`: Balanced quality/speed
- `fast`: Fastest, lower quality — useful for drafts

**Vertex AI initialization:**
```python
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
)
```

---

## LangChain Integration

VidGen uses LangChain as the orchestration layer for all LLM calls. Key packages:

| Package | Version | Usage |
|---|---|---|
| `langchain-core` | `>=0.1.27` | `ChatPromptTemplate`, `StrOutputParser` |
| `langchain-community` | `>=0.0.24` | `TextLoader` (loads transcript files as Documents) |
| `langchain-google-genai` | `>=0.0.8` | `ChatGoogleGenerativeAI` (Gemini connector) |
| `langchain-classic` | latest | `create_stuff_documents_chain` (for summarization) |

**Chain patterns used:**

1. **Stuff Documents Chain** (summarization):
   ```python
   chain = create_stuff_documents_chain(llm, prompt)
   result = chain.invoke({"context": docs})
   ```

2. **LCEL Pipe Chain** (metadata, image prompts):
   ```python
   chain = prompt | llm | StrOutputParser()
   result = chain.invoke({"context": text})
   ```

---

## Model Configuration System

All model selections are stored in `config/config.json` and managed by `src/utils/config.py`. This enables:

- **Runtime model switching** from the Streamlit UI without restarting the server
- **Per-task model selection** (different models for script vs. metadata vs. images)
- **Easy upgrades** — add a new model to the `available` list and it appears in the UI dropdown

The config file is read fresh on every pipeline call (not cached at module level), so changes take effect immediately.

---

## Alternate AI Routes (Kept Open)

See `docs/08_ALTERNATE_AI_ROUTES.md` for full details on OpenAI and Anthropic integrations that are implemented but not active in the current pipeline.

**Summary of alternate routes:**

| Service | Module | Status | Notes |
|---|---|---|---|
| OpenAI Whisper | `src/transcription_openai.py` | Inactive | Alternate STT via Whisper API with 10-min chunking |
| OpenAI TTS | `src/text_to_speech_openai.py` | Inactive | `tts-1-hd` model, `onyx` voice, 4096 char chunks |
| Anthropic Claude | `src/summarization-anthropic.py` | Inactive | `claude-3-5-sonnet-20240620` for script generation |
| Anthropic Claude | `src/image_prompting-anthropic.py` | Inactive | Claude for image prompt generation |

These routes are preserved for future use. Switching to them requires updating the import in the relevant page file and ensuring the API key env var is set.
