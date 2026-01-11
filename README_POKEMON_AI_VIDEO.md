# Pokémon AI Video Generator

A production pipeline for creating 90-second photorealistic Pokémon nature documentaries in the style of David Attenborough's *Planet Earth*.

## Overview

This project uses an **8-step automated pipeline** combining multiple AI services to create stunning nature documentary-style videos featuring Pokémon in their natural habitats.

### Core Components

- **Image Generation**: Google Gemini 2.5 Flash creates photorealistic seed images
- **Video Animation**: KIE.ai Kling 2.5 Pro adds subtle motion to static scenes
- **Narration**: ElevenLabs v3 delivers Attenborough-style voiceovers
- **Sound Design**: ElevenLabs SFX API provides atmospheric audio
- **Assembly**: FFmpeg synchronizes all elements into final output

## The "Breathing Photograph" Approach

This system emphasizes subtle movement within carefully composed scenes rather than complex action sequences. Each clip shows a carefully composed static scene with subtle motion focusing on elements like:

- Mist drifting through ancient forests
- Gentle breathing and natural body movements
- Environmental particles and atmospheric effects
- Slow, deliberate creature behaviors

## Requirements

### Software
- Python 3.10+
- FFmpeg (with ffprobe)
- uv package manager

### API Keys
You'll need API keys from:
- **Anthropic** - For Claude (orchestration)
- **Google AI** - For Gemini 2.5 Flash (image generation)
- **KIE.ai** - For Kling 2.5 Pro (video animation)
- **ElevenLabs** - For TTS and sound effects

## Installation

### macOS/Linux

```bash
# Clone the repository
git clone https://github.com/abhishektiwari123/forestry-demo.git
cd forestry-demo

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Copy environment template
cp scripts/.env.example scripts/.env

# Edit .env with your API keys
nano scripts/.env
```

### Windows

```powershell
# Clone the repository
git clone https://github.com/abhishektiwari123/forestry-demo.git
cd forestry-demo

# Install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Create virtual environment and install dependencies
uv sync

# Copy environment template
copy scripts\.env.example scripts\.env

# Edit .env with your API keys
notepad scripts\.env
```

## Project Structure

```
pokemon-ai-video-generator/
├── prompts/                    # AI agent instructions
│   ├── 1_research.md          # Species research SOP
│   ├── 2_story_generator.md   # Story development SOP
│   ├── 3.5_generate_assets_agent.md
│   ├── 4.5_generate_videos_agent.md
│   ├── 5.5_generate_audio_agent.md
│   ├── 6.5_generate_sound_effects_agent.md
│   └── 7_assemble_final_agent.md
├── scripts/                    # Python CLI tools
│   ├── generate_asset.py      # Image generation
│   ├── create_composite.py    # Image compositing
│   ├── generate_video.py      # Video animation
│   ├── generate_audio.py      # Narration TTS
│   ├── generate_sound_effect.py
│   ├── assemble_video.py      # Final assembly
│   └── .env.example           # API key template
├── [pokemon_name]/            # Per-project folders
│   ├── 01_research.md         # Species research
│   ├── 02_story_script.md     # 18-segment story
│   ├── assets/                # Generated images
│   ├── composites/            # Scene composites
│   ├── videos/                # Animated clips
│   ├── audio/                 # Narration files
│   ├── sfx/                   # Sound effects
│   ├── processed/             # Synced segments
│   └── [pokemon]_final.mp4    # Final output
└── docs/                       # Additional documentation
```

## Workflow

### Standard Operating Procedures

1. **SOP 1: Research** - Create comprehensive species profile
2. **SOP 2: Story Development** - Write 18-segment documentary script
3. **SOP 3.5: Asset Generation** - Create 20-25 photorealistic images
4. **SOP 4.5: Video Generation** - Animate scenes with subtle motion
5. **SOP 5.5: Audio Generation** - Generate Attenborough-style narration
6. **SOP 6.5: Sound Effects** - Create atmospheric background audio
7. **SOP 7: Final Assembly** - Synchronize and concatenate everything

### Quick Start

```bash
# 1. Create a new Pokemon project
mkdir haunter && cd haunter

# 2. Generate an asset
python ../scripts/generate_asset.py \
  --name "haunter_forest" \
  --prompt "Photorealistic Haunter ghost Pokemon floating in misty ancient forest, purple ethereal glow, volumetric fog, BBC Earth wildlife photography style" \
  --output assets/haunter_forest_01.png

# 3. Generate video from image
python ../scripts/generate_video.py \
  --image assets/haunter_forest_01.png \
  --prompt "Haunter slowly materializes from the mist, its gaseous form rippling as spectral particles drift around it" \
  --output videos/segment_01.mp4 \
  --segment 1

# 4. Generate narration
python ../scripts/generate_audio.py \
  --text "In the depths of an ancient forest, where sunlight rarely penetrates, a presence stirs." \
  --output audio/narration_01.mp3 \
  --segment 1

# 5. Generate sound effect
python ../scripts/generate_sound_effect.py \
  --prompt "Ancient misty forest ambiance, hollow wind through twisted trees, faint ethereal whispers" \
  --duration 8.0 \
  --output sfx/ambiance_01.mp3 \
  --segment 1

# 6. Assemble final documentary
python ../scripts/assemble_video.py \
  --pokemon haunter \
  --project-dir . \
  --output haunter_final.mp4
```

## Estimated Costs & Time

| Component | Cost per Documentary | Time |
|-----------|---------------------|------|
| Image Generation | $1-2 | 10-15 min |
| Video Animation | $3-6 | 60-90 min |
| Narration | $0.50-1 | 5 min |
| Sound Effects | $0.50-1 | 5 min |
| **Total** | **$6-13** | **1.5-2.5 hours** |

*Most time is automated waiting for API responses*

## Quality Standards

### Video Requirements
- Resolution: 1920x1080 (Full HD)
- Frame Rate: 24-30 fps
- Codec: H.264 with CRF 18
- Total Duration: 85-95 seconds

### Audio Requirements
- Format: MP3/WAV
- Bitrate: 128kbps minimum (192kbps preferred)
- Narration: 6-8 seconds per segment
- SFX Volume: 30-35% of narration

## Tips for Best Results

1. **Front-load critical motion** in video prompts
2. **Use temporal markers** ("begins to", "gradually", "slowly")
3. **Describe start and end states** for smooth animations
4. **Keep motion subtle** - think "breathing photograph"
5. **Verify timing** at each step to hit 90-second target

## Troubleshooting

### Common Issues

**Video generation timeout**
- Retry with simpler motion prompt
- Check API status at kie.ai

**Audio too long/short**
- Adjust word count (15-20 words per 6 seconds)
- Use ElevenLabs voice settings to adjust pace

**FFmpeg errors**
- Ensure all segments exist before assembly
- Check file paths and naming conventions

## License

This project is for educational and demonstration purposes.

## Contributing

Contributions welcome! Please read the documentation files for detailed guidelines on each component.
