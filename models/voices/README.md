# TTS Voice Models Directory

Place your Piper TTS voice models here.

## Required Models

You need Piper ONNX voice models for text-to-speech synthesis.

### Recommended French Voices

1. **fr_FR-siwis-medium** (High quality French)
   - Download from: https://github.com/rhasspy/piper/releases
   - Files needed:
     - `fr_FR-siwis-medium.onnx`
     - `fr_FR-siwis-medium.onnx.json`

2. **fr_FR-upmc-medium** (Alternative French)
   - Files needed:
     - `fr_FR-upmc-medium.onnx`
     - `fr_FR-upmc-medium.onnx.json`

### Recommended English Voices

1. **en_US-lessac-medium** (High quality US English)
   - Files needed:
     - `en_US-lessac-medium.onnx`
     - `en_US-lessac-medium.onnx.json`

2. **en_GB-alan-medium** (British English)
   - Files needed:
     - `en_GB-alan-medium.onnx`
     - `en_GB-alan-medium.onnx.json`

## Download Instructions

### Option 1: Direct Download

Visit: https://github.com/rhasspy/piper/releases/latest

Download the voice models you need and extract them to this directory.

### Option 2: Using wget

```bash
# French voice
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-fr-fr-siwis-medium.tar.gz
tar -xzf voice-fr-fr-siwis-medium.tar.gz -C models/voices/

# English voice
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-en-us-lessac-medium.tar.gz
tar -xzf voice-en-us-lessac-medium.tar.gz -C models/voices/
```

## Voice Quality Levels

- **low**: Fastest, lower quality (~20 MB)
- **medium**: Balanced quality/speed (~30-50 MB)
- **high**: Best quality, slower (~100+ MB)

## Directory Structure

```
models/voices/
  ├── fr_FR-siwis-medium.onnx
  ├── fr_FR-siwis-medium.onnx.json
  ├── en_US-lessac-medium.onnx
  └── en_US-lessac-medium.onnx.json
```

## Usage

Configure the voices in your pipeline configuration or UI settings.
The TTS module will load the appropriate voice based on the language.
