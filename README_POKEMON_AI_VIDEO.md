# Pokémon AI Video Generator

> Create photorealistic Pokémon nature documentaries in the style of David Attenborough's *Planet Earth*

Transform any Pokémon into a 90-second cinematic documentary through an 8-step automated production pipeline powered by AI.

## 🎬 Overview

This project implements a complete production workflow for generating high-quality nature documentaries featuring Pokémon as if they were real creatures. Using cutting-edge AI tools, the system creates:

- 📸 Photorealistic images of Pokémon and environments
- 🎥 Animated 10-second video clips with subtle "breathing photograph" motion
- 🎙️ David Attenborough-style narration
- 🔊 Atmospheric sound effects
- 🎞️ Final 90-second assembled documentary

### Key Features

- **8-Step Production Pipeline**: From research to final assembly
- **Smart Agent + Dumb Scripts**: AI handles orchestration, Python handles API calls
- **Breathing Photograph Approach**: 18 carefully composed scenes with subtle motion
- **Professional Quality**: Broadcast-ready 1920x1080 output
- **Cost-Effective**: $6-13 per documentary
- **Fast Generation**: 1.5-2.5 hours mostly automated

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Image Generation** | Google Gemini 2.5 Flash | Photorealistic seed images |
| **Video Generation** | KIE.ai Kling 2.5 Pro | Animation of static images |
| **Narration** | ElevenLabs v3 | David Attenborough-style voiceover |
| **Sound Effects** | ElevenLabs SFX API | Atmospheric environmental audio |
| **Video Assembly** | FFmpeg | Trimming, syncing, concatenation |
| **Image Hosting** | catbox.moe | Free public image URLs |
| **Orchestration** | Claude Code (Anthropic) | AI agent workflow automation |
| **Runtime** | Python 3.10+ | Script execution |
| **Package Manager** | uv | Fast dependency management |

## 📋 Prerequisites

### Required Software

- **Python 3.10+**: Core runtime
- **uv**: Python package manager ([installation](https://github.com/astral-sh/uv))
- **FFmpeg**: Video processing ([installation](https://ffmpeg.org/download.html))
- **Claude Code**: AI agent orchestration (optional but recommended)

### Required API Keys

1. **Anthropic Claude API** - For AI orchestration
2. **Google Gemini API** - For image generation
3. **KIE.ai API** - For video generation (Kling 2.5 Pro)
4. **ElevenLabs API** - For narration and sound effects

### API Key Setup

Sign up for each service:
- [Anthropic](https://console.anthropic.com/)
- [Google AI Studio](https://makersuite.google.com/app/apikey)
- [KIE.ai](https://kie.ai/) (for Kling access)
- [ElevenLabs](https://elevenlabs.io/)

## 🚀 Installation

### 1. Install System Dependencies

**macOS:**
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg
brew install ffmpeg

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Linux:**
```bash
# Install FFmpeg (Ubuntu/Debian)
sudo apt update && sudo apt install ffmpeg

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
# Install FFmpeg via Chocolatey
choco install ffmpeg

# Install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and Setup Project

```bash
# Navigate to project directory
cd pokemon-ai-video-generator

# Install Python dependencies
uv sync

# Configure API keys
cp scripts/.env.example scripts/.env

# Edit scripts/.env and add your API keys
nano scripts/.env  # or use your preferred editor
```

### 3. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.10+

# Check FFmpeg
ffmpeg -version

# Check uv
uv --version
```

## 📖 Usage

The production pipeline follows 8 Standard Operating Procedures (SOPs):

### SOP 1: Species Research

Research the Pokémon to create a biological profile.

**Prompt:** See `prompts/1_research.md`

**Output:** `[pokemon]/01_research.md`

**Example:**
```
Research Haunter, focusing on:
- Habitat: Abandoned buildings, caves
- Behavior: Nocturnal, spectral predator
- Abilities: Phase through matter, drain life energy
- Visual potential: Materialization, floating, glowing
```

### SOP 2: Story Development

Create 5 story options for the 90-second documentary.

**Prompt:** See `prompts/2_story_generator.md`

**Output:** `[pokemon]/02_story_script.md`

**Structure:**
- 18 segments, each 5-8 seconds
- Scene descriptions + narration
- Clear narrative arc (opening → development → climax → resolution)

### SOP 3: Asset Generation

Generate 20-25 photorealistic seed images.

**Prompt:** See `prompts/3.5_generate_assets_agent.md`

**Script:**
```bash
cd scripts

python generate_asset.py \
  --name "haunter_full_body_front" \
  --prompt "Photorealistic Haunter Pokemon, full body floating pose, purple gaseous spectral form with disembodied hands, menacing smile, glowing red eyes, translucent body, nature documentary style, 8k ultra detailed" \
  --output "../haunter/assets/haunter_full_body_front.jpg"
```

**Output:** `[pokemon]/assets/` (20-25 images)

### SOP 4: Composite & Video Generation

Create composites and generate animated videos.

**Prompt:** See `prompts/4.5_generate_videos_agent.md`

**Scripts:**
```bash
# Create composite (if needed)
python create_composite.py \
  --background "../haunter/assets/temple_ruins.jpg" \
  --foreground "../haunter/assets/haunter_full_body.png" \
  --position 960,800 \
  --scale 0.6 \
  --output "../haunter/composites/segment_01.jpg"

# Generate video
python generate_video.py \
  --image "../haunter/composites/segment_01.jpg" \
  --prompt "Purple spectral energy seeps through stone wall cracks and coalesces into Haunter's form, gaseous wisps swirl clockwise, translucent becoming semi-opaque over 10 seconds, ancient temple twilight atmosphere" \
  --output "../haunter/videos/segment_01.mp4" \
  --segment 1
```

**Output:** `[pokemon]/videos/` (18 × 10-second clips)

### SOP 5: Audio Generation

Generate narration for each segment.

**Prompt:** See `prompts/5.5_generate_audio_agent.md`

**Script:**
```bash
python generate_audio.py \
  --text "As darkness falls... the Haunter begins to stir. For creatures of the spectral realm... twilight is merely the beginning of their day." \
  --output "../haunter/audio/segment_01.mp3" \
  --segment 1
```

**Output:** `[pokemon]/audio/` (18 × 6-8 second clips)

### SOP 6: Sound Effects Generation

Generate atmospheric sound effects.

**Prompt:** See `prompts/6.5_generate_sound_effects_agent.md`

**Script:**
```bash
python generate_sound_effect.py \
  --prompt "Ancient temple ruins ambiance with gentle wind echoing through stone corridors, distant ghostly whispers, spectral energy materializing with ethereal resonance, mysterious twilight atmosphere" \
  --duration 7.2 \
  --output "../haunter/sfx/segment_01.mp3" \
  --segment 1
```

**Output:** `[pokemon]/sfx/` (18 clips matching audio duration)

### SOP 7: Final Assembly

Assemble all segments into final documentary.

**Prompt:** See `prompts/7_assemble_final_agent.md`

**Script:**
```bash
python assemble_video.py \
  --pokemon haunter \
  --project-dir .. \
  --output ../haunter/haunter_final.mp4
```

**Output:** `[pokemon]/[pokemon]_final.mp4` (90-second documentary)

## 📁 Project Structure

```
pokemon-ai-video-generator/
├── README.md
├── pyproject.toml                    # Python dependencies
├── prompts/                          # Agent instructions
│   ├── 1_research.md
│   ├── 2_story_generator.md
│   ├── 3.5_generate_assets_agent.md
│   ├── 4.5_generate_videos_agent.md
│   ├── 5.5_generate_audio_agent.md
│   ├── 6.5_generate_sound_effects_agent.md
│   └── 7_assemble_final_agent.md
├── scripts/                          # Python CLI tools
│   ├── .env.example
│   ├── generate_asset.py
│   ├── create_composite.py
│   ├── generate_video.py
│   ├── generate_audio.py
│   ├── generate_sound_effect.py
│   └── assemble_video.py
└── [pokemon_name]/                   # Per-Pokemon project
    ├── 01_research.md
    ├── 02_story_script.md
    ├── assets/                       # Generated images
    ├── composites/                   # Layered compositions
    ├── videos/                       # 10-second clips
    ├── audio/                        # Narration
    ├── sfx/                         # Sound effects
    ├── processed/                    # Synced segments
    └── [pokemon]_final.mp4          # Final output
```

## 💡 Key Concepts

### Breathing Photograph Approach

Instead of complex action sequences, each clip shows a carefully composed static scene with subtle motion:

- ✅ **Good**: Mist drifting, gentle breathing, eyes blinking
- ❌ **Avoid**: Running, fighting, complex interactions

This makes generation reliable and creates a contemplative documentary feel.

### Video Prompt Priority Hierarchy

When writing motion prompts, order matters:

1. **Core Action** - What's happening
2. **Specific Details** - What moves, how
3. **Logical Sequence** - Cause/effect, start/end
4. **Environmental Context** - Atmosphere, lighting
5. **Camera Movement** - Only if it enhances story

Example:
```
Purple gaseous form seeps through wall cracks and coalesces into Haunter,
hands forming first then head, mist swirls clockwise, translucent to opaque
over 10 seconds, twilight temple atmosphere, slight push-in
```

### Smart Agent + Dumb Scripts Philosophy

- **Agents** (Claude Code): Handle orchestration, decisions, file reading
- **Scripts** (Python): Single-purpose API calls, no complex logic

This separation makes debugging easier and keeps the pipeline maintainable.

## 💰 Cost & Timeline

### Per Documentary

**Cost:** ~$6-13
- Images: $0.50-2 (Gemini)
- Videos: $5-10 (Kling)
- Audio: $0.50-1 (ElevenLabs)

**Time:** ~1.5-2.5 hours
- Assets: 5-10 minutes
- Videos: 1-2 hours (longest step)
- Audio: 1-2 minutes
- SFX: 1-2 minutes
- Assembly: 1-2 minutes

### Optimization Tips

- Generate videos overnight
- Batch similar assets together
- Reuse environment assets across projects
- Use faster models for testing, premium for final

## 🎨 Example: Haunter Documentary

The `haunter/` directory contains a complete example:

**Story Arc:**
1. **Opening** - Temple at twilight, introduction
2. **Development** - Haunter materializes, explores ruins
3. **Climax** - Hunting scene, spectral powers displayed
4. **Resolution** - Return to dormancy as dawn approaches

**Key Scenes:**
- Materializing through stone walls
- Floating through ancient corridors
- Draining energy from prey
- Dissolving into mist

## 🐛 Troubleshooting

### Common Issues

**"API Key not found"**
- Ensure `.env` file exists in `scripts/` directory
- Verify API keys are correctly formatted
- No quotes around key values in `.env`

**"FFmpeg not found"**
- Install FFmpeg: `brew install ffmpeg` (macOS)
- Verify: `ffmpeg -version`

**"Video generation timeout"**
- Kling generation takes 5-8 minutes per clip
- Check KIE.ai API status
- Verify internet connection

**"Audio/video desync"**
- Ensure audio files are 6-8 seconds
- Verify SFX duration matches audio
- Check FFmpeg output for errors

**"Poor image quality"**
- Improve prompts with more detail
- Add "photorealistic", "8k", "ultra detailed"
- Reference "nature documentary photography"

### Getting Help

- Check agent prompts in `prompts/` for detailed instructions
- Review example Haunter project
- Verify all dependencies are installed
- Check API service status

## 🌟 Tips for Success

### Image Generation
- Lead with "Photorealistic"
- Be extremely specific about pose and features
- Include lighting direction
- Reference "nature documentary" style

### Video Prompts
- Follow priority hierarchy strictly
- Describe one primary action only
- Use temporal markers: "gradually", "over 10 seconds"
- Think simple: mist drifts > battles

### Narration
- 6-8 seconds per segment (15-26 words)
- Present tense for immediacy
- David Attenborough style: warm, authoritative
- Strategic pauses (ellipses)

### Sound Effects
- Match narration duration exactly
- Layer conceptually: background, mid, foreground
- Support, don't compete with narration
- Focus on atmosphere over action sounds

## 🔮 Advanced Usage

### Custom Voice
Replace default narrator:
```bash
python generate_audio.py \
  --voice-id "your_custom_voice_id" \
  --text "..." \
  --output "..."
```

### Adjust SFX Volume
```bash
python assemble_video.py \
  --sfx-volume 0.25  # Quieter SFX
```

### Add Fades
Manually add fade in/out to first/last segments using FFmpeg.

### Color Grading
Apply filters in assembly script for cinematic look.

## 📜 Credits

- **Concept**: Real Life Pokémon nature documentary series
- **Pipeline Design**: Brandon Hancock
- **AI Tools**: Google Gemini, KIE.ai Kling, ElevenLabs, Claude Code
- **Inspiration**: David Attenborough, BBC Earth, Planet Earth
- **Open Source**: This implementation

## 📄 License

This project is provided as-is for educational and creative purposes.

**Important Notes:**
- Pokémon is © Nintendo/Game Freak/The Pokémon Company
- Created documentaries are fan works
- Respect API terms of service
- Commercial use may require additional licensing

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Additional AI model integrations
- Web interface for easier pipeline management
- Batch processing multiple Pokémon
- Enhanced compositing features
- Auto-retry failed generations

## 🎯 Next Steps

1. Choose your Pokémon
2. Complete species research (SOP 1)
3. Develop story options (SOP 2)
4. Pick your favorite story direction
5. Generate assets (SOP 3)
6. Create videos (SOP 4)
7. Add audio (SOP 5-6)
8. Assemble final documentary (SOP 7)
9. Share your creation!

---

**Ready to create your first Pokémon nature documentary?**

Start with SOP 1: Research your chosen Pokémon using `prompts/1_research.md` as your guide.

Happy documenting! 🎬✨
