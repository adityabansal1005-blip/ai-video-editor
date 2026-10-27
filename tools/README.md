# tools/

Not stored in git. Each machine fills this folder itself.

**Windows laptop** (downloaded by hand from a browser, because GitHub downloads are very slow on this ISP):
- `yt-dlp.exe`: github.com/yt-dlp/yt-dlp/releases/latest
- `whisper/Release/whisper-cli.exe`: unzip `whisper-bin-x64.zip` from github.com/ggml-org/whisper.cpp/releases/tag/b5454 (the newer v1.9.x tags have no Windows files)
- `ggml-base.bin`, `ggml-small.bin`: huggingface.co/ggerganov/whisper.cpp

**Cloud / Linux:** run `bash setup-cloud.sh --small` from the repo root. It builds `tools/whisper-cli` and downloads the models.
