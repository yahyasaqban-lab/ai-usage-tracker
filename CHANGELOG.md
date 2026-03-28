# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-03-28

### Added
- 🎉 **Initial release** of AI Usage Tracker
- 💰 **Credit Management System**
  - Monthly subscriptions with auto-renewal tracking
  - One-time credit purchases
  - Real-time balance monitoring
  - Expense tracking and budgets

- 📊 **Job Tracking System**
  - Automatic token counting for all major AI models
  - Multi-provider cost calculation (6 providers, 14+ models)
  - Job categorization with metadata
  - Usage analytics by model, time, and cost

- 🔌 **OpenClaw Integration**
  - Automatic session tracking from OpenClaw logs
  - Real-time usage monitoring
  - Background auto-tracking daemon
  - OpenClaw skill creation

- 🌐 **REST API (FastAPI)**
  - Credit management endpoints
  - Job tracking endpoints
  - Usage analytics endpoints
  - Cost estimation endpoints
  - Interactive documentation at `/docs`

- 💻 **Web Dashboard**
  - Beautiful responsive UI
  - Real-time data updates
  - Credit balance visualization
  - Job management interface
  - Quick actions for credits/subscriptions

- 🛠️ **CLI Interface**
  - Complete command-line interface
  - JSON output support
  - Batch operations
  - Scriptable automation

### Supported AI Providers
- **OpenAI**: GPT-4o, GPT-4o Mini, o1, o3-mini
- **Anthropic**: Claude 3 Opus/Sonnet/Haiku, Claude Sonnet 4.0
- **Google**: Gemini Pro/Flash/Ultra
- **Mistral**: Small/Medium/Large
- **DeepSeek**: Chat/Coder
- **Groq**: Llama 3.3 70B, Mixtral 8x7B

### Technical Features
- SQLite database with full schema
- Token counting approximation engine
- Auto-tracking background daemon
- CORS-enabled API
- Mobile-responsive dashboard
- Error handling and validation
- Comprehensive logging

### Documentation
- Complete README with examples
- API documentation
- CLI help system
- Example usage scripts
- Development setup guide