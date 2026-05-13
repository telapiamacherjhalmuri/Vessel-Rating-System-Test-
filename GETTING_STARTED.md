# GETTING STARTED - Vessel Rating System

## 🎯 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
cd e:\Vessel_Rating_System
pip install -r requirements.txt
```

### Step 2: Initialize System
```bash
python quickstart.py --init
```

### Step 3: Launch Application
```bash
python quickstart.py
```

✅ **Done!** Application opens automatically at `http://localhost:8501`

---

## 📖 First-Time User Guide

### What This System Does

The Vessel Rating System automatically analyzes maritime vessels by:

1. **Accepting just 2 inputs:**
   - Vessel Name (e.g., "Meghna Pearl")
   - IMO Number (e.g., "9894765")

2. **Automatically fetching:**
   - Real-time AIS tracking data
   - Vessel specifications and history
   - Ownership and management information
   - Compliance and certification records
   - International sanctions status
   - Weather and route information

3. **Scoring across 6 modules:**
   - General Information (10% weight)
   - Ownership Information (20% weight)
   - AIS Information (15% weight)
   - Risk & Compliance (30% weight)
   - Environmental & Voyage Data (15% weight)
   - Legal & Documentation (10% weight)

4. **Generating:**
   - Final risk score (0-100)
   - Band rating (0-9 scale)
   - Risk classification and level
   - Detailed alerts and anomalies
   - Module-by-module breakdown

### Example Usage

#### Input
```
Vessel Name: Meghna Pearl
IMO: 9894765
```

#### Output
```
Band: 6.9 / 9.0
Classification: GOOD
Risk Level: Moderate Risk 🟡

Alerts:
- Moderate AIS gaps detected
- High-risk port history
```

---

## 🖥️ User Interface Tour

### Home Screen
- **Simple input form** with vessel name and IMO number
- **"Analyze Vessel" button** to start analysis
- **Recent analyses** display for quick reference

### Results Screen
- **Overall rating** with band score and risk level
- **Risk alerts** highlighting any concerning factors
- **Module breakdown** showing individual scores
- **Export options** for JSON and CSV reports

### Navigation
- **About** - System overview and features
- **FAQ** - Common questions and troubleshooting

---

## 📊 Understanding Your Report

### Band Rating Scale

| Band | Meaning | Risk | Emoji |
|------|---------|------|-------|
| 8-9 | Excellent | Very Low | 🟢 |
| 7-7.9 | Strong | Low-Moderate | 🟡 |
| 6-6.9 | Good | Moderate | 🟡 |
| 5-5.9 | Acceptable | Medium | 🟠 |
| 4-4.9 | Weak | Elevated | 🟠 |
| 3-3.9 | Poor | High | 🔴 |
| 0-2.9 | Very Poor | Critical | 🔴 |

### What Each Module Assesses

**Module 1: General Information**
- How old is the vessel?
- Is it well-maintained?
- What type of fuel does it use?
- Who certifies it?

**Module 2: Ownership**
- Has ownership changed frequently?
- Has the name changed suspiciously?
- Who are the current owners/managers?
- Are they reputable?

**Module 3: AIS Information**
- Is the vessel's AIS signal continuous?
- Are there gaps in tracking?
- Signs of spoofing or deception?

**Module 4: Risk & Compliance** (Most Important)
- Is the vessel sanctioned?
- What's the flag state?
- What ports does it visit?
- Any STS (Ship-to-Ship) transfers?

**Module 5: Environmental & Voyage**
- Current weather conditions?
- In piracy or war zones?
- Historical incident patterns?

**Module 6: Documentation**
- Are certificates valid?
- Insurance in force?
- Recent inspections passed?

---

## 🚨 Alert Types

### Critical Alerts (Red 🔴)
**Immediate action required**
- Sanctioned vessel
- AIS spoofing detected
- Dark activity patterns
- Expired certificates

### High Alerts (Orange 🟠)
**Close monitoring needed**
- Extended AIS gaps
- High-risk port calls
- War/piracy zones
- Frequent STS transfers

### Medium Alerts (Yellow 🟡)
**Attention required**
- Moderate AIS gaps
- Unusual movement patterns
- Historical incidents

---

## 💾 Exporting Reports

### JSON Export
Complete report with all scoring details
- Use for: Integration with other systems, detailed archiving
- File format: Standard JSON with all data

### CSV Export
Module scores summary in spreadsheet format
- Use for: Comparison, charting, reporting
- File format: Comma-separated values

### Manual Save
Copy important information from the dashboard

---

## ⚙️ Configuration (Advanced)

### Adjusting Scoring Weights

Edit `config.py`:

```python
SCORING_WEIGHTS = {
    "general_info": 10,        # Make less important
    "ownership": 20,
    "ais": 15,
    "risk_compliance": 40,     # Make more important (from 30%)
    "environmental": 10,       # From 15%
    "documentation": 5,        # From 10%
}
```

Total must equal 100.

### Changing Risk Thresholds

```python
RISK_THRESHOLDS = {
    "AIS_GAP_HOURS": 12,          # Flag gaps > 12 hours (from 24)
    "FREQUENT_NAME_CHANGES": 2,   # From 3
    "FREQUENT_STS": 3,            # From 5
}
```

### Adding High-Risk Flags

```python
HIGH_RISK_FLAGS = [
    "DPRK", "IRN", "SYR",  # Existing
    "CUSTOM_FLAG",         # Add your own
]
```

---

## 🧪 Running Examples

### Try Example Analyses

```bash
# Run all examples
python examples.py

# Run specific example
python examples.py 1    # Simple analysis
python examples.py 2    # Batch analysis
python examples.py 3    # Export reports
python examples.py 4    # Risk analysis
python examples.py 5    # Compare vessels
python examples.py 6    # JSON output
```

### Programmatic Usage

```python
from api_integration import get_api_integration
from scoring_engine import get_scoring_engine
from utils import print_console_report

# Initialize
api = get_api_integration()
engine = get_scoring_engine()

# Fetch data
data = api.fetch_all_vessel_data("Meghna Pearl", "9894765")

# Generate report
report = engine.generate_report("Meghna Pearl", "9894765", data)

# Display
print_console_report(report)
```

---

## 🔧 Troubleshooting

### Application Won't Start
```bash
# Check Python version
python --version    # Should be 3.9+

# Check dependencies
pip list | findstr streamlit

# Reinstall
pip install -r requirements.txt --force-reinstall
```

### Database Issues
```bash
# Reinitialize database
python quickstart.py --init

# Check database file
dir db/
```

### Port Already in Use
```bash
# Use different port
streamlit run app/main.py --server.port 8502
```

### API Connection Error
- System currently uses demo data
- Real API integration requires keys
- See DEPLOYMENT.md for API setup

---

## 📚 Common Questions

**Q: Do I need to input all vessel data?**
A: No! Just input name and IMO - system fetches everything automatically.

**Q: How accurate is the rating?**
A: Very accurate for demo data. Real accuracy depends on actual API data quality.

**Q: Can I use this commercially?**
A: Yes, but you'll need real API access (see DEPLOYMENT.md).

**Q: How often should I re-analyze a vessel?**
A: Recommended every 30-90 days for monitoring.

**Q: Can I export reports?**
A: Yes! JSON and CSV export available on results screen.

**Q: What if the band changes?**
A: Download the new report and compare with previous analysis.

---

## 🎓 Learning Resources

### Understanding the Scoring

1. **Module Weights**: Different factors have different importance
   - Risk & Compliance = 30% (most important)
   - Ownership = 20% (second most important)
   - Others = 50% combined

2. **Score Calculation**:
   ```
   Final Score = Σ(Module Score × Module Weight)
   Band = (Final Score / 100) × 9
   ```

3. **Critical Overrides**:
   - Certain conditions force lower bands automatically
   - Examples: sanctions, AIS spoofing, expired documents

### Interpreting Results

- **Band 8-9**: Excellent vessels, low risk
- **Band 6-7.9**: Good/strong vessels, normal monitoring
- **Band 4-5.9**: Below average, needs attention
- **Band 0-3.9**: Serious issues, possible intervention

### Next Steps

1. Try analyzing several vessels
2. Compare results between vessels
3. Review detailed module breakdowns
4. Explore export functionality
5. Check DEPLOYMENT.md for real API integration

---

## 📞 Getting Help

### Check These Resources

1. **FAQ** - See "FAQ" page in app
2. **README.md** - Comprehensive documentation
3. **DEPLOYMENT.md** - Configuration and deployment
4. **examples.py** - Running example analyses
5. **config.py** - All configuration options

### Debug Mode

```bash
streamlit run app/main.py --logger.level=debug
```

This shows detailed logging information in console.

---

## 🎉 You're Ready!

1. ✅ System installed
2. ✅ Database initialized
3. ✅ Application running
4. ✅ Ready to analyze vessels!

**Start by entering a vessel name and IMO number.**

**Happy analyzing! 🚢**

---

**Version**: 1.0.0
**Last Updated**: April 2024
