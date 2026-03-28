# AI Usage Tracker 🤖💰

**Complete AI usage tracking system with credit management, job tracking, API, and OpenClaw integration.**

Track your AI costs, manage credits, and monitor usage across all your AI projects.

## ✨ Features

### 🏦 **Credit Management**
- **Subscriptions** with automatic renewal tracking
- **One-time credit purchases** 
- **Real-time balance monitoring**
- **Expense tracking** and budgets

### 📊 **Job Tracking**
- **Automatic token counting** for all major AI models
- **Multi-provider cost calculation** (OpenAI, Anthropic, Google, Mistral, DeepSeek, Groq)
- **Job categorization** with metadata
- **Usage analytics** by model, time, and cost

### 🔌 **Integrations**
- **OpenClaw auto-tracking** from session logs
- **REST API** for external integrations
- **Web dashboard** for visual monitoring
- **Standalone CLI** for scripting

### 📈 **Analytics**
- **Usage trends** (daily/monthly)
- **Cost breakdown** by model
- **Token usage patterns**
- **Budget alerts** and monitoring

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/yahyasaqban-lab/ai-usage-tracker.git
cd ai-usage-tracker
pip install -r requirements-usage-tracker.txt
```

### 2. Start the API Server

```bash
python ai-tracker-api.py
# API running at http://localhost:8001
```

### 3. Open Web Dashboard

```bash
# Serve the dashboard
python -m http.server 8002
# Open http://localhost:8002/usage-dashboard.html
```

### 4. Set Up Credits

```bash
# Add a monthly subscription
python ai-usage-tracker.py add-subscription "OpenAI Pro" 20.00 --days 30

# Or purchase credits once
python ai-usage-tracker.py add-credits 10.00 --notes "Initial credits"
```

### 5. Start Tracking (OpenClaw Users)

```bash
python openclaw-usage-integration.py --auto-track
```

## 💻 CLI Usage

### Credit Management
```bash
# Add subscription
python ai-usage-tracker.py add-subscription "OpenAI Pro" 20.00 --days 30

# Purchase credits
python ai-usage-tracker.py add-credits 10.00 --notes "One-time purchase"

# Check balance
python ai-usage-tracker.py balance
```

### Job Tracking
```bash
# Log a manual job
python ai-usage-tracker.py log-job "Code review" gpt-4o \
  --input "Review this code" \
  --output "Code looks good" \
  --description "Manual code review task"

# List recent jobs
python ai-usage-tracker.py jobs --limit 10

# Get job details
python ai-usage-tracker.py job-details <job-id>
```

### Analytics
```bash
# Usage stats (last 30 days)
python ai-usage-tracker.py stats --days 30

# Export as JSON
python ai-usage-tracker.py stats --days 7 --json
```

## 🌐 API Endpoints

### Credit Management
- `POST /subscriptions` - Create subscription
- `POST /credits` - Purchase credits
- `GET /balance` - Get credit balance

### Job Tracking
- `POST /jobs` - Log AI job
- `GET /jobs` - List recent jobs
- `GET /jobs/{id}` - Get job details

### Analytics
- `GET /stats?days=30` - Usage statistics
- `GET /models` - List supported models
- `POST /estimate` - Estimate job cost

### Example API Calls

```bash
# Get balance
curl http://localhost:8001/balance

# Log job
curl -X POST http://localhost:8001/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test job",
    "model": "gpt-4o",
    "input_text": "Hello world",
    "output_text": "Hi there!"
  }'

# Get usage stats
curl http://localhost:8001/stats?days=30
```

## 🎯 Supported AI Models

### OpenAI
- GPT-4o ($0.0025/$0.01 per 1K tokens)
- GPT-4o Mini ($0.00015/$0.0006 per 1K)
- o1 ($0.015/$0.06 per 1K)
- o3-mini ($0.002/$0.008 per 1K)

### Anthropic
- Claude 3 Opus ($0.015/$0.075 per 1K)
- Claude 3 Sonnet ($0.003/$0.015 per 1K)
- Claude 3 Haiku ($0.00025/$0.00125 per 1K)
- Claude Sonnet 4.0 ($0.003/$0.015 per 1K)

### Google
- Gemini Pro ($0.00125/$0.005 per 1K)
- Gemini Flash ($0.000125/$0.0005 per 1K)
- Gemini Ultra ($0.0125/$0.05 per 1K)

### Mistral
- Small ($0.002/$0.006 per 1K)
- Medium ($0.0027/$0.0081 per 1K)
- Large ($0.008/$0.024 per 1K)

### DeepSeek
- Chat ($0.00014/$0.00028 per 1K)
- Coder ($0.00014/$0.00028 per 1K)

### Groq (Fast Inference)
- Llama 3.3 70B ($0.00059/$0.00079 per 1K)
- Mixtral 8x7B ($0.00027/$0.00027 per 1K)

## 🔧 OpenClaw Integration

For OpenClaw users, the system can automatically track all AI interactions:

### Create OpenClaw Skill
```bash
python openclaw-usage-integration.py --create-skill
```

### Auto-Track Sessions
```bash
# Start background tracking
python openclaw-usage-integration.py --auto-track --interval 300
```

### Manual Session Tracking
```bash
# Track specific session
python openclaw-usage-integration.py --track-session "agent:main:main"
```

## 📱 Web Dashboard

The web dashboard provides:

- **Real-time credit balance** and usage
- **Visual analytics** and charts
- **Job management** interface
- **Quick actions** for credits and subscriptions
- **Responsive design** for mobile/desktop

Access at: `http://localhost:8002/usage-dashboard.html`

## 📊 Database Schema

The system uses SQLite with these tables:

- **subscriptions** - Monthly/annual subscriptions
- **credit_purchases** - One-time credit purchases
- **jobs** - AI job logs with costs
- **usage_summary** - Daily usage aggregates

## 🛠️ Development

### Project Structure
```
ai-usage-tracker/
├── ai-usage-tracker.py      # Core tracker + CLI
├── ai-tracker-api.py        # FastAPI server
├── openclaw-usage-integration.py  # OpenClaw integration
├── usage-dashboard.html     # Web dashboard
├── requirements-usage-tracker.txt  # Dependencies
└── README.md               # This file
```

### Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yahyasaqban-lab/ai-usage-tracker/issues)
- **Documentation**: This README + code comments
- **API Docs**: Visit `http://localhost:8001/docs` when API is running

## 🎯 Use Cases

### Personal AI Budget Tracking
- Track spending across ChatGPT, Claude, etc.
- Set monthly budgets and alerts
- Analyze usage patterns

### Business AI Cost Management
- Monitor team AI usage
- Allocate costs by project/department
- Generate expense reports

### AI Development Projects
- Track costs during development
- Optimize model selection for budget
- Monitor production usage

### OpenClaw Power Users
- Automatic session tracking
- No manual logging required
- Full integration with OpenClaw workflows

---

**Built for the AI-powered future.** 🚀

Track every token, manage every dollar, optimize every model.