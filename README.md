# ComfyUI API Toolkit

Four AI services. Sixty-eight nodes. One install. Zero excuses.

ComfyUI API Toolkit bundles Kling AI, ElevenLabs, Google Gemini, and a Utils collection into a single custom node pack so you can stop juggling half a dozen plugins and actually make things. Each service lives in its own module discovered automatically from the filesystem -- add a folder under `services/` and it just works. If you don't have a particular SDK installed, that service quietly sits out instead of torching your entire ComfyUI startup. The rest keeps working. You're welcome.

---

## What's Inside

```
ComfyUI API Toolkit v1.3.0
├── Kling AI         32 nodes   (video, image, audio, effects)
├── ElevenLabs       15 nodes   (TTS, voice cloning, music, transcription)
├── Google Gemini    20 nodes   (entire API covered -- text, image, audio, video, embeddings)
└── Utils             1 node    (pixel art resize)
                  ----------
                    68 nodes total
```

---

## Services

### Kling AI -- 32 nodes

Kling does a lot. Embarrassingly a lot. Video from text, video from images, extend existing videos, lip sync, avatar generation, virtual try-on, motion control, effects, upscaling, audio generation, TTS, and voice cloning. If it involves moving pixels or making sound, there's probably a node for it.

**Video**
- Kling Text to Video
- Kling Image to Video
- Kling Video Omni
- Kling Video Extend
- Kling Lip Sync
- Kling Advanced Lip Sync
- Kling Motion Control
- Kling Avatar Generation

**Image**
- Kling Image Generation
- Kling Image Omni
- Kling Image Extend
- Kling Virtual Try-On
- Kling AI Multi-Shot
- Kling Image Recognize

**Audio**
- Kling Text to Audio
- Kling Text to Speech
- Kling TTS Advanced
- Kling Video to Audio
- Kling Voice Clone

**Effects & Upscaling**
- Kling Video Effects
- Kling Effect Templates
- Kling AI Upscale

**Utilities**
- Kling AI Authentication
- Kling Video Loader
- Kling Raw File Loader
- Kling Raw File Saver
- Kling AI Asset Upload
- Kling AI Element
- Kling Camera Control
- Kling Voice Selector
- Kling AI Cloud Uploader
- Kling Fast Video Saver

---

### ElevenLabs -- 15 nodes

The gold standard for AI voice. Text to speech, speech to speech, voice cloning, voice design, sound effects, music generation, audio isolation, transcription, and multi-speaker dialogue. If you're still using robotic TTS from 2019, this pack is an intervention.

- ElevenLabs - API Key
- ElevenLabs - Voice Selector
- ElevenLabs - Fetch Voices
- ElevenLabs - Voice Clone
- ElevenLabs - Voice Design
- ElevenLabs - Voice Create
- ElevenLabs - Text to Speech
- ElevenLabs - TTS with Timestamps
- ElevenLabs - Speech to Speech
- ElevenLabs - Sound Effects
- ElevenLabs - Audio Isolation
- ElevenLabs - Speech to Text
- ElevenLabs - Text to Dialogue
- ElevenLabs - Music Generation
- ElevenLabs - Account Info

---

### Google Gemini -- 20 nodes

The Gemini service went from "a few image nodes" to covering the entire Gemini API. That means text, vision, image generation via both Gemini and Imagen, image editing, inpainting, outpainting, TTS with 30+ voices, music generation via Lyria, video generation via Veo, and embeddings. If Google offers it through their API, there's a node for it now.

**Config -- 6 nodes**
- Gemini API Key
- Gemini Model Selector
- Gemini Safety Settings
- Gemini Thinking Config
- Gemini List Available Models -- queries your API key for what's actually accessible to your account
- Gemini Token Counter

**Text -- 4 nodes**
- Gemini Text Generation -- 33 model options across Gemini 3 previews, 2.5, 2.0, and the full Gemma family
- Gemini Prompt Refiner
- Gemini Multi-Turn Chat
- Gemini Structured Output -- JSON-schema constrained generation

**Image -- 6 nodes**
- Gemini Vision Analysis
- Gemini Image Generation -- Nano Banana / 2 / Pro via generate_content
- Imagen Image Generation -- Imagen 4 Ultra / Standard / Fast via generate_images
- Gemini Image Edit
- Gemini Inpaint
- Gemini Outpaint

**Audio -- 2 nodes**
- Gemini Text-to-Speech -- 30+ prebuilt voices across 3 TTS models
- Gemini Music Generation -- Lyria 3 Clip and Pro

**Video -- 1 node**
- Gemini Video Generation -- Veo 3.1, 3.0, 2.0, preview, fast, and lite variants

**Embeddings -- 1 node**
- Gemini Text Embeddings -- 768 to 3072 dimensions with task-type optimization

#### Full model coverage

| Category | Models |
|----------|--------|
| Gemini text / multimodal | 13 models (Gemini 3 previews, 2.5, 2.0, latest aliases) |
| Gemma open models | 8 models (3-1b through 4-31b) |
| Gemini image gen | 3 Nano Banana models |
| Imagen | 3 Imagen 4 models (Ultra, Standard, Fast) |
| TTS | 3 TTS models + 30 prebuilt voices |
| Embeddings | 2 embedding models |
| Video | 6 Veo models |
| Music | 2 Lyria models |
| Specialized | Robotics ER, Computer Use, Deep Research, TTS previews |

---

### Utils -- 1 node

**Pixel Art Resize**
Resizes images to pixel art with proper palette locking across frames for animations. Uses Floyd-Steinberg dithering and scipy KDTree acceleration so palette matching doesn't take all day.

---

## Features Worth Knowing About

**Auto-discovery for services**
Services are discovered from the filesystem. Drop a folder under `services/` and it loads. Nothing to register, nothing to hardcode.

**Graceful service fallback**
Don't have `google-genai` installed? Gemini nodes don't load. Everything else does. Same deal for Kling and ElevenLabs. Install what you need, ignore what you don't.

**Shared retry logic with exponential backoff**
All API nodes retry on transient failures. They back off intelligently instead of hammering the API until it blocks you. Rate limits happen; the nodes handle it.

**API keys are password-masked**
Your keys don't show up in plaintext in your workflow. Share screenshots without accidentally donating your API credits to strangers.

**Environment variable fallback**
Set `KLING_ACCESS_KEY` + `KLING_ACCESS_SECRET`, `ELEVENLABS_API_KEY`, or `GEMINI_API_KEY` in your environment and the auth nodes will pick them up automatically. Good for automation, good for not hardcoding secrets.

**IS_CHANGED on all API nodes**
ComfyUI caches node outputs. API nodes that cache are useless. Every API node here implements IS_CHANGED so you get fresh results every time you queue, not whatever you got the last time.

**Tooltips on every parameter**
Hover over any input and there's a tooltip explaining what it does. Shockingly underrated feature.

**Output directory auto-creation**
If your output path doesn't exist, it gets created. No silent failures because someone forgot to mkdir.

**Cloud uploader auto-fallback**
The cloud uploader tries catbox first, falls back to tmpfiles if it fails. Assets get uploaded regardless.

---

## Installation

**ComfyUI Manager (easiest)**
Search for "API Toolkit" and install. Done.

**Registry**
```bash
comfy node registry-install comfyui-api-toolkit
```

**Manual**
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/IxMxAMAR/ComfyUI-API-Toolkit
cd ComfyUI-API-Toolkit
pip install -r requirements.txt
```

---

## Dependencies

Install all services at once:
```bash
pip install requests PyJWT soundfile scipy "google-genai>=0.8.0"
```

Or pick what you actually use:
```bash
# Kling only
pip install requests PyJWT

# ElevenLabs only
pip install requests soundfile scipy

# Gemini only
pip install "google-genai>=0.8.0"
```

The pack uses optional dependencies, so you're not forced to install Google's SDK just because you want to run some TTS.

---

## Also Available Separately

Prefer to install just one service? Each service is published as its own standalone package:

| Package | Service |
|---------|---------|
| ComfyUI-Kling-Direct | Kling AI |
| ComfyUI-ElevenLabs-Pro | ElevenLabs |
| ComfyUI-NanoBanana2 | Google Gemini |

Same nodes, same quality, just smaller installs if you only need one thing.

---

## Requirements

- ComfyUI (recent enough to support custom nodes, which if you're reading this you probably already have)
- Python 3.10+
- API keys for whichever services you want to use

---

## License

MIT. Use it, fork it, build on it.

---

Made by [IxMxAMAR](https://github.com/IxMxAMAR)
