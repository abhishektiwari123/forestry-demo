# Background Music Guide for Pokemon Battle Documentary

## Where to Get Epic Battle Music (Royalty-Free)

### Best Sources:

1. **YouTube Audio Library** (FREE)
   - URL: https://studio.youtube.com/channel/UC.../music
   - Search for: "Epic", "Battle", "Cinematic", "Action"
   - Recommended tracks:
     - "Battle of Kings" by Per Kiilstofte
     - "Clash Defiant" by Audionautix
     - "Intro" by The Descent

2. **Pixabay Music** (FREE, No Attribution)
   - URL: https://pixabay.com/music/
   - Search: "Epic Battle Music"
   - Filter: 2-3 minutes duration (will loop for our 90s video)
   - Recommended: High-energy orchestral tracks

3. **Incompetech** (FREE with Attribution)
   - URL: https://incompetech.com/music/
   - Genre: "Cinematic" or "Action"
   - Look for: Fast-paced, dramatic orchestral

4. **Free Music Archive** (FREE)
   - URL: https://freemusicarchive.org/
   - Search: "Epic Orchestral"

## Recommended Music Style:

For a Pokemon battle documentary, look for:
- **Tempo**: 140-160 BPM (high energy)
- **Instruments**: Orchestral (strings, brass, percussion)
- **Mood**: Epic, dramatic, intense
- **Duration**: 2-3 minutes (will loop automatically)
- **Dynamic**: Building intensity for battle scenes

## How to Use:

1. **Download** your chosen battle music
2. **Save as**: `charizard/battle_assets/background_music.mp3`
3. **Run sync script**:
   ```bash
   # Test with one segment first
   python scripts/sync_audio_with_music.py --test 1

   # If good, process all segments
   python scripts/sync_audio_with_music.py --all
   ```

## Audio Mixing Details:

The script automatically:
- **Narration**: 100% volume (clear, prominent)
- **Background music**: 30% volume (subtle atmosphere)
- **Looping**: Music loops seamlessly across entire video
- **Quality**: 192kbps AAC audio (high quality)

## Example Searches:

- "Pokemon battle theme epic orchestral"
- "Anime fight scene background music"
- "Cinematic action trailer music"
- "Epic boss battle soundtrack"

## Pro Tips:

1. **Preview first**: Download 2-3 tracks, test with `--test 1`
2. **Check intensity**: Music should build during key moments
3. **Avoid lyrics**: Instrumental only (so narration is clear)
4. **Match energy**: High-energy for battle, slightly calmer for resolution

## Legal Note:

All music sources listed are:
- ✅ Royalty-free
- ✅ Commercial use allowed
- ✅ YouTube safe
- ℹ️  Some require attribution (check license)

When uploading final video, credit the composer in description!
