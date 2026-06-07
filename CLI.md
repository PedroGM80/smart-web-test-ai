# Smart Test CLI - Advanced Commands

Complete command-line interface for Smart Test with configuration, history, and analytics.

---

## 🎯 Available Commands

### CONFIG - Manage Configurations

**Save current configuration**
```bash
smart-test config save my-test-config
```
Saves all current settings to `~/.smarttest/my-test-config.json`

**Load saved configuration**
```bash
smart-test config load my-test-config
```
Loads settings from saved configuration

**List saved configurations**
```bash
smart-test config list
```
Shows all saved configurations with size and timestamp

### HISTORY - Test History

**View test history**
```bash
smart-test history list --last 10
```
Shows last 10 tests (default: 10)

**Options:**
- `--last N`: Show last N tests (default: 10)

**Example output:**
```
URL                      Pass Rate    Duration    Mode        Timestamp
─────────────────────────────────────────────────────────────────────
https://github.com       95.5%        42.3s       balanced    2026-06-07 14:32
https://api.github.com   87.0%        38.1s       speed       2026-06-07 14:15
```

**Clear history**
```bash
smart-test history clear
```
Delete all test history

### COMPARE - Compare Models

**Compare two models**
```bash
smart-test compare mistral vs neural-chat
```
Shows detailed comparison of two models

**Options:**
- `--last N`: Compare using last N tests (default: 10)

**Example output:**
```
Model Comparison: mistral vs neural-chat

Metric              mistral    neural-chat    Winner
────────────────────────────────────────────────────
Avg Pass Rate       93.5%      88.2%          mistral
Avg Duration        35.2s      41.5s          neural-chat
Tests Run           42         42             —
```

### EXPORT - Export Results

**Export to CSV**
```bash
smart-test export csv results.csv
```

**Export to JSON**
```bash
smart-test export json results.json
```

**Export last N tests**
```bash
smart-test export csv results.csv --last 100
```

**Supported formats:**
- `csv` - Comma-separated values
- `json` - JSON format

### STATS - Show Statistics

**Show all-time statistics**
```bash
smart-test stats
```

**Show weekly statistics**
```bash
smart-test stats --period week
```

**Show monthly statistics**
```bash
smart-test stats --period month
```

**Options:**
- `--period`: `all` (default), `week`, `month`

**Example output:**
```
╭─ Test Statistics ─╮
│ Total Tests: 42   │
│ Avg Pass Rate: 93.5% │
│ Avg Duration: 35.2s  │
│ Min Pass Rate: 45.0% │
│ Max Pass Rate: 98.0% │
│ Time Range: 2026-06-01 to 2026-06-07 │
╰──────────────────╯
```

### CACHE - Clear Cache

**Clear local cache**
```bash
smart-test clear-cache
```
Removes all cached data from `~/.smarttest/cache`

---

## 💾 Configuration Files

All data stored in `~/.smarttest/`:

```
~/.smarttest/
├── cache/                  # Local cache
├── history.json           # Test history
├── my-config.json         # Saved config 1
├── prod-config.json       # Saved config 2
└── ...
```

---

## 🔄 Workflow Examples

### Example 1: Compare Models on Specific Tests

```bash
# Run tests with model 1
smart-test "https://github.com" "Test repo" --model mistral

# Run same tests with model 2
smart-test "https://github.com" "Test repo" --model neural-chat

# Compare results
smart-test compare mistral vs neural-chat --last 1
```

### Example 2: Save and Load Test Configuration

```bash
# Create a test with specific settings
smart-test "https://api.example.com" "API tests" --mode quality

# Save this configuration
smart-test config save api-tests

# Later, use the same config
smart-test config load api-tests
```

### Example 3: Generate Reports

```bash
# Run multiple tests
smart-test "https://site1.com" "Test 1"
smart-test "https://site2.com" "Test 2"
smart-test "https://site3.com" "Test 3"

# View summary
smart-test stats --period week

# Export for sharing
smart-test export csv week-results.csv
smart-test export json week-results.json

# Share the CSV with team
# Send week-results.csv via email
```

### Example 4: Monitor Performance Over Time

```bash
# Daily tracking
smart-test "https://api.myapp.com" "Health check" --mode speed

# Weekly review
smart-test stats --period week
smart-test history list --last 7

# Monthly analysis
smart-test stats --period month
smart-test compare model1 vs model2 --last 30
```

---

## 📊 Data Storage

### History Format

Each test is stored with:
```json
{
  "timestamp": "2026-06-07T14:32:45.123456",
  "url": "https://github.com",
  "objective": "Test repository",
  "pass_rate": 95.5,
  "duration": 42.3,
  "mode": "balanced",
  "model": "mistral",
  "status": "success"
}
```

### CSV Export Format

```
timestamp,url,objective,pass_rate,duration,mode,model,status
2026-06-07T14:32:45.123456,https://github.com,Test repo,95.5,42.3,balanced,mistral,success
2026-06-07T14:15:30.456789,https://api.github.com,API test,87.0,38.1,speed,neural-chat,success
```

---

## ⚙️ Configuration Format

Saved configurations include:
```json
{
  "mode": "balanced",
  "model": "mistral",
  "vision_model": "llava",
  "headed": false,
  "timeout": 30,
  "retries": 2
}
```

---

## 🎯 Pro Tips

### Tip 1: Alias Common Commands
```bash
# Add to ~/.bash_profile or ~/.zshrc
alias stest='smart-test'
alias stest-compare='smart-test compare'
alias stest-export='smart-test export csv'
```

### Tip 2: Automated Reports
```bash
# Create a script for weekly reports
#!/bin/bash
smart-test stats --period week
smart-test export csv "report-$(date +%Y-%m-%d).csv"
echo "Report generated"
```

### Tip 3: Model Testing
```bash
# Test all models systematically
for model in mistral neural-chat dolphin-mixtral; do
  smart-test "https://example.com" "Test" --model $model
done

# Compare them all
smart-test compare mistral vs neural-chat
smart-test compare mistral vs dolphin-mixtral
```

### Tip 4: Performance Baselines
```bash
# Create performance baseline
smart-test config save baseline
smart-test "https://myapp.com" "Load test" --mode quality
smart-test stats > baseline-stats.txt

# Later, compare against baseline
smart-test config load baseline
smart-test stats --period week
# Check if performance improved
```

---

## 🐛 Troubleshooting

### History Not Found
```
Question: History shows no data
Solution: 
- Ensure tests were run with smart-test
- Check ~/.smarttest/history.json exists
- Run: smart-test stats to verify data
```

### Export Fails
```
Question: Export command fails
Solution:
- Check file permissions
- Ensure output directory exists
- Try: smart-test export json /tmp/results.json
```

### Config Not Loading
```
Question: Config load fails
Solution:
- List configs: smart-test config list
- Check spelling of config name
- Verify config file in ~/.smarttest/
```

---

## 📈 Metrics Tracked

Per test, we track:
- ✅ URL tested
- ✅ Test objective
- ✅ Pass rate (%)
- ✅ Duration (seconds)
- ✅ Test mode (speed/balanced/quality)
- ✅ Model used
- ✅ Success/failure status
- ✅ Exact timestamp

---

## 🔐 Privacy

All CLI data stored locally:
- No cloud storage
- No external APIs
- All data on your machine
- Delete anytime: `smart-test clear-cache`

---

## 📚 Integration with Other Tools

### With Email Reports
```bash
# Export results to JSON
smart-test export json results.json

# Include in email (from email_reports.py)
python -c "
from email_reports import EmailReporter
import json

with open('results.json') as f:
    results = json.load(f)

reporter = EmailReporter()
reporter.send_daily_report(['team@company.com'], results)
"
```

### With Slack Notifications
```bash
# Get stats for Slack message
stats=$(smart-test stats)
# Send to Slack (from slack_integration.py)
python -c "from slack_integration import SlackNotifier; ..."
```

### With GitHub Issues
```bash
# Export results and process with GitHub integration
smart-test export json latest-results.json

python -c "
from github_integration import GitHubIssueCreator
import json

with open('latest-results.json') as f:
    results = json.load(f)

creator = GitHubIssueCreator()
for result in results:
    creator.create_or_update_issue(result)
"
```

---

## 🚀 Future Enhancements

Planned CLI improvements:
- [ ] Batch test execution
- [ ] Scheduled cron integration
- [ ] Real-time streaming output
- [ ] Interactive dashboard mode
- [ ] Custom metric definitions
- [ ] Advanced filtering/search
- [ ] Performance alerts
- [ ] Cost estimation

---

**CLI Version: 1.0 | Date: June 2026**

