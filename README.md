# ComfyUI API Toolkit

Three AI services. Sixty nodes. One install. Zero excuses.

ComfyUI API Toolkit bundles Kling AI, ElevenLabs, and Google Gemini into a single custom node pack so you can stop juggling half a dozen plugins and actually make things. Each service lives in its own plugin module, so if you don't have a particular SDK installed, that service quietly sits out instead of torching your entire ComfyUI startup. The rest keeps working. You're welcome.

---

## What's Inside

```
ComfyUI API Toolkit
├── Kling AI         32 nodes   (video, image, audio, effects)
├── ElevenLabs       15 nodes   (TTS, voice cloning, music, transcription)
└── Google Gemini    13 nodes   (image gen/edit, text, vision, chat)
                  ----------
                    60 nodes total
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

### Google Gemini -- 13 nodes

Gemini brings multimodal generation to the party: image generation with multi-reference support, image editing, inpainting, outpainting, vision analysis, text generation, prompt refinement, multi-turn chat, and structured JSON output. Thinking mode is configurable. Safety settings are configurable. Whether you configure them is up to you.

**Config**
- Gemini API Key
- Gemini Model Selector
- Gemini Safety Settings
- Gemini Thinking Config

**Text**
- Gemini Text Generation
- Gemini Prompt Refiner
- Gemini Multi-Turn Chat
- Gemini Structured Output (JSON)

**Image**
- Gemini Vision Analysis
- Gemini Image Generation
- Gemini Image Edit
- Gemini Inpaint
- Gemini Outpaint

---

## Features Worth Knowing About

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
