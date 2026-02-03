# Integration Test Guide - All 9 Agents

## Overview

This integration test validates the complete NexSidi pipeline from user conversation to deployed application, testing all 9 agents:

1. **Tilotma** - Orchestrator/Chat Agent
2. **Saanvi** - Requirements Analyst/Architect  
3. **Shubham** - Backend Developer
4. **Aanya** - Frontend Developer
5. **Navya** - Adversarial Logic Reviewer
6. **Karan** - Adversarial Security Reviewer
7. **Deepika** - Adversarial Performance Reviewer
8. **Aarav** - Browser Testing Agent
9. **Pranav** - DevOps/Deployment Agent

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip install pytest pytest-asyncio

# Ensure environment variables are set
export ANTHROPIC_API_KEY="your-key"
export GOOGLE_CLOUD_PROJECT="your-project"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
```

### Run All Tests

```bash
# From backend directory
python tests/run_integration_test.py
```

### Run Specific Test Suites

```bash
# Individual agent tests only
python tests/run_integration_test.py --test individual

# Full pipeline test only
python tests/run_integration_test.py --test pipeline

# Error handling tests
python tests/run_integration_test.py --test errors

# Performance tests
python tests/run_integration_test.py --test performance
```

### Verbose Output

```bash
python tests/run_integration_test.py --verbose
```

## Test Structure

### 1. Individual Agent Tests (`TestIndividualAgents`)

Tests each agent in isolation:

- `test_tilotma_conversation` - Validates conversation handling
- `test_saanvi_requirements_analysis` - Validates requirements analysis
- `test_shubham_backend_generation` - Validates backend code generation
- `test_aanya_frontend_generation` - Validates frontend code generation
- `test_navya_logic_review` - Validates logic error detection
- `test_karan_security_review` - Validates security vulnerability detection
- `test_deepika_performance_review` - Validates performance issue detection
- `test_aarav_browser_testing` - Validates browser testing
- `test_pranav_deployment` - Validates deployment

### 2. Full Pipeline Test (`TestFullPipeline`)

Tests the complete end-to-end flow:

```
User Conversation (Tilotma)
    ↓
Requirements Analysis (Saanvi)
    ↓
Backend Generation (Shubham)
    ↓
Frontend Generation (Aanya)
    ↓
Adversarial Review (Navya, Karan, Deepika)
    ↓
Browser Testing (Aarav)
    ↓
Deployment (Pranav)
    ↓
Live Application
```

### 3. Error Handling Tests (`TestErrorHandling`)

Tests error recovery mechanisms:

- Agent failure recovery
- Retry mechanisms
- Graceful degradation

### 4. Performance Tests (`TestPerformance`)

Tests performance and cost optimization:

- Cost tracking accuracy
- Response time monitoring
- Resource usage

## Expected Output

### Successful Run

```
==================================================
NEXSIDI INTEGRATION TEST - ALL 9 AGENTS
==================================================
Test Class: all
Verbose: False
==================================================

tests/integration/test_full_pipeline.py::TestIndividualAgents::test_tilotma_conversation PASSED
✅ Tilotma: 10 messages, ₹0.15

tests/integration/test_full_pipeline.py::TestIndividualAgents::test_saanvi_requirements_analysis PASSED
✅ Saanvi: Complexity 5/10, ₹250.00

tests/integration/test_full_pipeline.py::TestIndividualAgents::test_shubham_backend_generation PASSED
✅ Shubham: 8 files, ₹1.25

tests/integration/test_full_pipeline.py::TestIndividualAgents::test_aanya_frontend_generation PASSED
✅ Aanya: 12 files, ₹1.50

tests/integration/test_full_pipeline.py::TestIndividualAgents::test_navya_logic_review PASSED
✅ Navya: 2 logic issues found

tests/integration/test_full_pipeline.py::TestIndividualAgents::test_karan_security_review PASSED
✅ Karan: 1 security issues found

tests/integration/test_full_pipeline.py::TestIndividualAgents::test_deepika_performance_review PASSED
✅ Deepika: 0 performance issues found

tests/integration/test_full_pipeline.py::TestIndividualAgents::test_aarav_browser_testing PASSED
✅ Aarav: 3 tests passed

tests/integration/test_full_pipeline.py::TestIndividualAgents::test_pranav_deployment PASSED
✅ Pranav: Backend=https://nexsidi-abc123.railway.app, Frontend=https://nexsidi-abc123.vercel.app

tests/integration/test_full_pipeline.py::TestFullPipeline::test_complete_pipeline PASSED

==================================================
FULL PIPELINE TEST - ALL 9 AGENTS
==================================================

[1/9] 💬 Tilotma - Handling conversation...
  Message 1/5: 45 chars
  Message 2/5: 38 chars
  Message 3/5: 52 chars
  Message 4/5: 61 chars
  Message 5/5: 35 chars

[2/9] 📋 Saanvi - Analyzing requirements...
  Complexity: 5/10
  Price: ₹250.00

[3/9] 💻 Shubham - Generating backend...
  Files generated: 8

[4/9] 🌐 Aanya - Generating frontend...
  Files generated: 12

[5-7/9] ✅ Adversarial Review - Navya, Karan, Deepika...
  Total issues found: 3
  Navya (logic): 2
  Karan (security): 1
  Deepika (performance): 0

[8/9] 🧪 Aarav - Browser testing...
  Status: Deferred (requires deployed app)

[9/9] 🚀 Pranav - Deploying to production...
  Backend URL: https://nexsidi-abc123.railway.app
  Platform: Railway

==================================================
PIPELINE COMPLETE - SUMMARY
==================================================
Total Messages: 10
Total Cost: ₹253.90
Complexity: 5/10
Last Agent: pranav

✅ ALL AGENTS TESTED SUCCESSFULLY!
==================================================

========== 10 passed in 45.23s ==========
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```
ModuleNotFoundError: No module named 'app'
```

**Solution**: Run from backend directory:
```bash
cd backend
python tests/run_integration_test.py
```

#### 2. API Key Errors

```
Exception: Claude API not configured
```

**Solution**: Set environment variables:
```bash
export ANTHROPIC_API_KEY="your-key"
export GOOGLE_CLOUD_PROJECT="your-project"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/key.json"
```

#### 3. Agent Not Found

```
ModuleNotFoundError: No module named 'app.agents.navya_adversarial'
```

**Solution**: Ensure all agent files exist:
- `app/agents/tilotma.py`
- `app/agents/saanvi.py`
- `app/agents/shubham.py`
- `app/agents/aanya.py`
- `app/agents/navya_adversarial.py`
- `app/agents/karan_adversarial.py`
- `app/agents/deepika_adversarial.py`
- `app/agents/aarav_testing.py`
- `app/agents/pranav.py`

#### 4. Timeout Errors

```
asyncio.TimeoutError
```

**Solution**: Increase timeout in AI Router or use faster models for testing.

## Cost Estimation

Approximate costs for full pipeline test:

| Agent | Model | Estimated Cost |
|-------|-------|----------------|
| Tilotma | Gemini 2.5 Flash | ₹0.10 - ₹0.20 |
| Saanvi | Claude Opus 4.5 | ₹0.50 - ₹1.00 |
| Shubham | Gemini 3 Pro | ₹1.00 - ₹2.00 |
| Aanya | Gemini 3 Pro | ₹1.00 - ₹2.00 |
| Navya | Claude Sonnet 4.5 | ₹0.30 - ₹0.60 |
| Karan | Claude Sonnet 4.5 | ₹0.30 - ₹0.60 |
| Deepika | Claude Sonnet 4.5 | ₹0.30 - ₹0.60 |
| Aarav | Gemini 3 Flash | ₹0.05 - ₹0.10 |
| Pranav | Gemini 3 Flash | ₹0.05 - ₹0.10 |
| **TOTAL** | | **₹3.60 - ₹7.20** |

## Next Steps

After successful test run:

1. **Review Logs**: Check agent outputs for quality
2. **Verify Costs**: Ensure costs are within budget
3. **Test Edge Cases**: Add tests for complex scenarios
4. **Performance Tuning**: Optimize slow agents
5. **Production Deploy**: Deploy tested pipeline to production

## Support

For issues or questions:
- Check logs in `backend/logs/`
- Review agent documentation in `backend/app/agents/`
- Contact: dev@nexsidi.com
