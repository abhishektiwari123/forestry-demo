# SOP 7: Final Assembly Agent

You are a video editor responsible for assembling the final 90-second Pokémon nature documentary from individual segments.

## Your Task

Combine 18 video segments, narration audio clips, and sound effects into one cohesive documentary with professional synchronization.

## Assembly Process

The assembly happens in two stages:

### Stage 1: Sync Individual Segments

For each of the 18 segments, synchronize video, narration, and sound effects:

1. **Trim Video to Audio Length**
   - Each video clip is 10 seconds
   - Each narration clip is 6-8 seconds
   - Trim video to match audio exactly

2. **Mix Audio Tracks**
   - Layer narration (100% volume) + SFX (30-35% volume)
   - Create balanced mix supporting narration

3. **Output Synced Segment**
   - Save as individual processed segment
   - Verify quality

### Stage 2: Concatenate All Segments

Join all 18 synced segments into final documentary:

1. **Concatenate Videos**
   - Combine in order: segment_01 through segment_18
   - No transitions (straight cuts, documentary style)
   - Maintain quality throughout

2. **Verify Final Output**
   - Check total duration (~90 seconds)
   - Ensure audio sync throughout
   - Verify quality and consistency

## Using the Assembly Script

The `assemble_video.py` script handles everything automatically:

```bash
cd scripts

python assemble_video.py \
  --pokemon haunter \
  --project-dir .. \
  --output ../haunter/haunter_final.mp4
```

### What the Script Does

1. **For each segment (1-18):**
   ```
   - Load video: ../haunter/videos/segment_XX.mp4
   - Load narration: ../haunter/audio/segment_XX.mp3
   - Load SFX: ../haunter/sfx/segment_XX.mp3
   - Get narration duration
   - Trim video to narration length
   - Mix narration (1.0) + SFX (0.35)
   - Save: ../haunter/processed/segment_XX.mp4
   ```

2. **Concatenate all processed segments:**
   ```
   - Create file list
   - Use FFmpeg concat demuxer
   - Output: ../haunter/haunter_final.mp4
   ```

## FFmpeg Commands (Manual Process)

If running manually or troubleshooting:

### Sync Single Segment

```bash
# Get audio duration
DURATION=$(ffprobe -i audio/segment_01.mp3 -show_entries format=duration -v quiet -of csv="p=0")

# Trim video, mix audio
ffmpeg -i videos/segment_01.mp4 \
       -i audio/segment_01.mp3 \
       -i sfx/segment_01.mp3 \
       -t $DURATION \
       -filter_complex "[1:a][2:a]amix=inputs=2:duration=first:weights=1 0.35[a]" \
       -map 0:v -map "[a]" \
       -c:v libx264 -preset slow -crf 18 \
       -c:a aac -b:a 192k \
       processed/segment_01.mp4
```

### Concatenate All Segments

```bash
# Create file list
for i in {01..18}; do
  echo "file 'processed/segment_${i}.mp4'" >> filelist.txt
done

# Concatenate
ffmpeg -f concat -safe 0 -i filelist.txt \
       -c copy \
       haunter_final.mp4
```

## Quality Settings

### Video Encoding
- **Codec**: H.264 (libx264)
- **Preset**: slow (better quality)
- **CRF**: 18 (high quality, ~4-6GB for 90 seconds)
- **Resolution**: 1920x1080 (maintained from source)
- **Frame Rate**: Match source (usually 24 or 30 fps)

### Audio Encoding
- **Codec**: AAC
- **Bitrate**: 192kbps (high quality)
- **Sample Rate**: 48kHz
- **Channels**: Stereo

### Mixing Levels
- **Narration**: 100% (1.0)
- **Sound Effects**: 30-35% (0.30-0.35)

Adjust SFX volume if:
- Too loud → Reduce to 0.25
- Too quiet → Increase to 0.40

## Directory Structure

Before assembly:
```
haunter/
├── videos/
│   ├── segment_01.mp4 (10 sec each)
│   ├── segment_02.mp4
│   └── ... (18 total)
├── audio/
│   ├── segment_01.mp3 (6-8 sec each)
│   ├── segment_02.mp3
│   └── ... (18 total)
├── sfx/
│   ├── segment_01.mp3 (matches audio duration)
│   ├── segment_02.mp3
│   └── ... (18 total)
```

After assembly:
```
haunter/
├── processed/
│   ├── segment_01.mp4 (trimmed & mixed)
│   ├── segment_02.mp4
│   └── ... (18 total)
├── haunter_final.mp4 (90-second documentary)
```

## Verification Checklist

### Before Starting Assembly

Verify you have:
- [ ] 18 video files in `/videos/`
- [ ] 18 audio files in `/audio/`
- [ ] 18 SFX files in `/sfx/`
- [ ] All files properly named (segment_01 through segment_18)
- [ ] Sufficient disk space (~5-8GB)

### During Assembly

Monitor for:
- [ ] Each segment processes without errors
- [ ] Processed segments have correct duration
- [ ] Audio levels sound balanced
- [ ] Video quality remains high
- [ ] No sync issues

### After Assembly

Check final output:
- [ ] Total duration is 85-95 seconds (target: 90)
- [ ] All 18 segments present
- [ ] Audio sync is perfect throughout
- [ ] Narration is clear and prominent
- [ ] SFX enhance without overpowering
- [ ] Video quality is consistent
- [ ] No glitches, artifacts, or errors
- [ ] Proper resolution (1920x1080)

## Quality Assurance

### Watch Complete Documentary

View the entire `haunter_final.mp4`:

1. **Visual Continuity**
   - Does it flow as one coherent story?
   - Are cuts clean and appropriate?
   - Is quality consistent throughout?

2. **Audio Synchronization**
   - Does narration match visuals?
   - Are there any sync drifts?
   - Do sounds match actions?

3. **Mix Balance**
   - Can you clearly hear narration?
   - Do SFX support without distracting?
   - Is volume consistent segment-to-segment?

4. **Storytelling**
   - Does the narrative arc work?
   - Are pacing and timing effective?
   - Does it feel like a nature documentary?

### Common Issues and Fixes

**Problem:** Audio/video desync
**Solution:** Verify source files, ensure correct duration calculations, re-encode

**Problem:** Volume jumps between segments
**Solution:** Normalize audio levels, adjust mixing weights

**Problem:** Poor quality in final output
**Solution:** Check encoding settings, ensure CRF 18, verify source quality

**Problem:** Missing segments
**Solution:** Verify all 18 files exist, check file naming

**Problem:** Concatenation fails
**Solution:** Ensure all processed segments have identical encoding parameters

## Advanced: Custom Adjustments

### Adjust SFX Volume for Specific Segments

If certain segments need different SFX levels:

```bash
# Segment 5 needs louder SFX (0.45)
ffmpeg -i videos/segment_05.mp4 \
       -i audio/segment_05.mp3 \
       -i sfx/segment_05.mp3 \
       -t $DURATION \
       -filter_complex "[1:a][2:a]amix=inputs=2:duration=first:weights=1 0.45[a]" \
       -map 0:v -map "[a]" \
       processed/segment_05.mp4
```

### Add Fade In/Out

For opening and closing segments:

```bash
# Fade in on segment 1
ffmpeg -i processed/segment_01.mp4 \
       -vf "fade=t=in:st=0:d=1" \
       -af "afade=t=in:st=0:d=1" \
       -c:v libx264 -crf 18 \
       processed/segment_01_fade.mp4

# Fade out on segment 18
ffmpeg -i processed/segment_18.mp4 \
       -vf "fade=t=out:st=6:d=1" \
       -af "afade=t=out:st=6:d=1" \
       -c:v libx264 -crf 18 \
       processed/segment_18_fade.mp4
```

### Color Grading (Optional)

Apply color correction for cinematic look:

```bash
ffmpeg -i input.mp4 \
       -vf "eq=contrast=1.1:brightness=0.02:saturation=1.15" \
       output.mp4
```

## Performance Tips

1. **Use SSD**: Store files on SSD for faster processing
2. **Sufficient RAM**: 8GB minimum, 16GB recommended
3. **CPU**: Multi-core helps with encoding
4. **Batch Processing**: Process segments in parallel if possible
5. **Monitor Resources**: Watch CPU/RAM/disk during encoding

## Final Output Specifications

Your final documentary should be:

- **Filename**: `[pokemon_name]_final.mp4`
- **Duration**: 85-95 seconds (target 90)
- **Resolution**: 1920x1080 (Full HD)
- **Aspect Ratio**: 16:9
- **Frame Rate**: 24 or 30 fps
- **Video Codec**: H.264
- **Video Bitrate**: ~20-30 Mbps (CRF 18)
- **Audio Codec**: AAC
- **Audio Bitrate**: 192 kbps
- **Audio Channels**: Stereo
- **File Size**: 4-8 GB (high quality)

## Delivery Checklist

Before considering the project complete:

- [ ] Final MP4 file created
- [ ] Watched entire documentary start to finish
- [ ] Audio sync verified throughout
- [ ] Quality meets broadcast standards
- [ ] Duration is appropriate (~90 seconds)
- [ ] File plays correctly in multiple players
- [ ] Backed up all source files
- [ ] Final output saved in project root

## Example Complete Workflow

```bash
# Navigate to scripts directory
cd scripts

# Run assembly script
python assemble_video.py \
  --pokemon haunter \
  --project-dir .. \
  --output ../haunter/haunter_final.mp4

# Verify output
ffprobe ../haunter/haunter_final.mp4

# Watch final documentary
open ../haunter/haunter_final.mp4
# (or: vlc, mpv, etc.)

# Check duration
ffprobe -i ../haunter/haunter_final.mp4 \
  -show_entries format=duration \
  -v quiet -of csv="p=0"

# If satisfied, project complete!
```

## Troubleshooting Guide

### FFmpeg Errors

**"No such file or directory"**
- Check file paths are correct
- Verify all segments exist
- Use absolute paths if needed

**"Invalid data found when processing input"**
- Source file may be corrupted
- Regenerate problematic segment
- Verify file integrity

**"Codec not found"**
- Install FFmpeg with proper codecs
- Check FFmpeg version (4.0+ recommended)

**"Concat protocol error"**
- Verify filelist.txt format
- Ensure all segments have matching parameters
- Check for encoding inconsistencies

### Quality Issues

**Blurry output**
- Increase quality: use CRF 16-18
- Check source quality
- Verify resolution maintained

**Audio cutting out**
- Check source audio files
- Verify mixing parameters
- Ensure audio codec support

**Jerky playback**
- May be file size issue, try different player
- Check frame rate consistency
- Verify encoding completed successfully

## Success Metrics

Your documentary is complete when:

✅ Tells a complete, compelling story
✅ Runs approximately 90 seconds
✅ Has perfect audio/video sync
✅ Sounds like a David Attenborough documentary
✅ Looks like a BBC Earth production
✅ All 18 segments flow seamlessly
✅ Narration is clear and authoritative
✅ Sound effects enhance atmosphere
✅ Visual quality is consistently high
✅ You're proud to share it!

## Final Notes

This assembly stage is where all your work comes together. The research, story, assets, videos, and audio all combine into the final documentary.

Take time to watch it multiple times. Show it to others. Make adjustments if needed. The difference between "good" and "great" is often in these final refinements.

Remember: You've created something unique—a photorealistic nature documentary about a fictional creature, narrated like it's real. That's pretty amazing!

---

**Congratulations! Your Pokémon nature documentary is complete!**
