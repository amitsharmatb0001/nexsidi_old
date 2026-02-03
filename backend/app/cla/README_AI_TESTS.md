# AI Provider Connection Tests

## Test Scripts Created

I've created two test scripts to verify your AI provider connections:

### 1. Comprehensive Test: [test_ai_providers.py](file:///e:/nexsidi/backend/app/tests/test_ai_providers.py)

**Features:**
- Tests all three providers (Vertex AI, Claude AI, Gemini AI Studio)
- Checks configuration status
- Makes actual API calls to verify connectivity
- Provides detailed error messages
- Shows summary of working/failed providers

**Run with:**
```bash
python app/tests/test_ai_providers.py
```

### 2. Simple Test: [test_ai_connection.py](file:///e:/nexsidi/backend/app/tests/test_ai_connection.py)

**Features:**
- Simpler, faster test
- Shows configuration status
- Tests each configured provider
- Displays response and token usage

**Run with:**
```bash
python app/tests/test_ai_connection.py
```

## What the Tests Check

### Vertex AI (GCP)
- ✅ Checks if `GOOGLE_CLOUD_PROJECT` is set
- ✅ Checks if `GOOGLE_CLOUD_LOCATION` is set
- ✅ Checks if `GOOGLE_APPLICATION_CREDENTIALS` is set
- ✅ Verifies credentials file exists
- ✅ Makes test API call to verify connection
- ✅ Shows project, location, and credentials path

### Claude AI (Anthropic)
- ✅ Checks if `ANTHROPIC_API_KEY` is set
- ✅ Makes test API call to verify connection
- ✅ Shows API key (masked)

### Gemini AI Studio
- ✅ Checks if `GOOGLE_API_KEY` is set
- ✅ Makes test API call to verify connection
- ✅ Shows API key (masked)
- ⚠️ May fail if quota exhausted (20 requests/day on free tier)

## Expected Output

```
======================================================================
  TESTING AI PROVIDER CONNECTIONS
======================================================================

📋 Configuration Status:
   Vertex AI: ✅ Configured
   Claude AI: ✅ Configured
   Gemini AI Studio: ✅ Configured

   Vertex AI Details:
   - Project: your-gcp-project
   - Location: us-central1
   - Credentials: /path/to/credentials.json

----------------------------------------------------------------------
Testing Vertex AI...
----------------------------------------------------------------------
✅ SUCCESS!
   Model: gemini-1.5-flash
   Response: Vertex AI works!
   Tokens: 15

----------------------------------------------------------------------
Testing Claude AI...
----------------------------------------------------------------------
✅ SUCCESS!
   Model: claude-haiku-4-5-20251001
   Response: Claude works!
   Tokens: 12

----------------------------------------------------------------------
Testing Gemini AI Studio...
----------------------------------------------------------------------
❌ FAILED: Quota exhausted (or) ✅ SUCCESS!

======================================================================
  TEST COMPLETE
======================================================================
```

## Troubleshooting

### Vertex AI Not Configured
If you see `❌ Not configured`, check your `.env` file:
```env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

### Claude AI Not Configured
Check your `.env` file:
```env
ANTHROPIC_API_KEY=sk-ant-...
```

### API Call Fails
Common issues:
1. **Vertex AI**: Invalid credentials, wrong project ID, API not enabled in GCP
2. **Claude AI**: Invalid API key, quota exceeded, billing not set up
3. **Gemini AI Studio**: Quota exhausted (free tier limit: 20 requests/day)

## Next Steps

Run the test to see which providers are working, then we can troubleshoot any issues.
