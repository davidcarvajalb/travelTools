# Environment Variables Configuration

This project supports loading environment variables from a `.env` file for secure configuration management.

## Quick Setup

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your API key**:
   ```bash
   # Open in your editor
   nano .env
   # OR
   vim .env
   ```

3. **Add your Gemini API key**:
   ```
   GEMINI_API_KEY=your-actual-api-key-here
   ```

## Getting a Gemini API Key

1. Visit https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key to your `.env` file

## Usage

Once your `.env` file is configured, you can run the summarization step without the `--api-key` flag:

```bash
./podman-run.sh shell << 'EOF'
python -m travel_tools.step2_5_summarize \
  --destination cancun \
  --source transat \
  --test-single-hotel
exit
EOF
```

## Podman + Make integration

If a `.env` file is present in the repo root, `make run`, `make shell`, and other `podman-run.sh` commands automatically load it via `--env-file`. You do not need to manually export `GEMINI_API_KEY`; the container will pick it up on every rebuild so long as `.env` exists next to the Makefile.
