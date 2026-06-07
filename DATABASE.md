# Smart Test Database - Complete Guide

SQLAlchemy ORM with SQLite (dev) and PostgreSQL (prod) support.

---

## 🎯 Database Models

### Test
- URL tested
- Test objective  
- Pass rate
- Duration
- Mode (speed/balanced/quality)
- Model used
- Status
- Timestamps

### ModelPerformance
- Model name
- Total tests run
- Success count
- Average pass rate
- Average duration
- Min/Max pass rate

### Failure
- Test reference
- GitHub issue URL
- Notification status
- Resolution tracking
- Notes

### Domain
- Domain tracking
- Total tests per domain
- Average pass rate
- Last tested time

### Metric
- Custom metric tracking
- Metric value & unit
- Associated test

---

## 🚀 Quick Start

```python
from database import init_db, Database

# Initialize database
db = init_db()

# Add test
db.add_test(
    url="https://github.com",
    objective="Test repo",
    pass_rate=95.5,
    duration=42.3,
    mode="balanced",
    model="mistral"
)

# Get statistics
stats = db.get_statistics()
print(stats)

# Update model stats
db.update_model_stats("mistral")
```

---

## ⚙️ Configuration

**Development (SQLite):**
```bash
# Default, no configuration needed
python app.py
```

**Production (PostgreSQL):**
```bash
export DATABASE_URL="postgresql://user:password@localhost/smarttest"
python app.py
```

---

## 📊 Integration Points

Works seamlessly with:
- CLI enhancements (history persistence)
- Email reports (data export)
- GitHub issues (failure tracking)
- Slack notifications (stats aggregation)
- Dashboard analytics (metrics)

---

**Database: Production Ready**
