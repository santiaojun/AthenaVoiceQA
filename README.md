# AthenaVoiceQA

> Healthcare voice agents are difficult to evaluate manually. AthenaVoiceQA automates quality assurance by acting as realistic patients over live phone calls.

An automated voice QA framework that stress-tests AI-powered medical office agents through realistic phone conversations. The system places outbound calls, simulates patient scenarios using GPT-4o-mini, records full transcripts, and identifies conversational failures such as:

- Premature call termination
- Incorrect intent recognition  
- Hallucinated or contradictory responses
- Failure to escalate to a nurse or staff member
- Appointment and medication workflow errors

See [architecture.md](architecture.md) for system design details.

---

## Features

- 📞 Automated outbound phone calls via Twilio
- 🤖 GPT-4o-mini powered patient simulator
- 🧠 Hybrid intent detection (RapidFuzz + LLM fallback)
- 💬 Dialogue state machine for natural conversation flow
- 📝 Automatic transcript logging after every call
- 🎙️ Call recording in MP3 format
- 🐞 Bug report with severity classification
- 🔄 10 randomized patient scenarios

---

## Tech Stack

- Python 3.11
- Flask
- Twilio Voice API + TwiML
- OpenAI GPT-4o-mini
- RapidFuzz
- ngrok

---

## Installation

```bash
git clone https://github.com/santiaojun/AthenaVoiceQA.git
cd AthenaVoiceQA
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
```

Fill in your credentials in `.env`:

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
OPENAI_API_KEY=sk-...
TARGET_PHONE_NUMBER=+18054398008
```

---

## Running

**Terminal 1 — Start Flask server:**
```bash
python app.py
```

**Terminal 2 — Start ngrok tunnel:**
```bash
./ngrok http 5000
```

**Terminal 3 — Place a call:**
```bash
python caller.py https://your-ngrok-url.ngrok-free.dev
```

Transcripts are automatically saved to `transcripts/` after each call ends.

---

## Test Scenarios

| Scenario | Description |
|----------|-------------|
| scheduling | Book an appointment for next Monday at 2pm |
| refill | Request a prescription refill for lisinopril |
| hours | Ask about office hours |
| cancel | Cancel tomorrow's appointment |
| insurance | Check if Blue Cross Blue Shield is accepted |
| reschedule | Move an appointment to Friday |
| test_results | Ask about recent lab results |
| weekend | Ask about Sunday availability |
| urgent | Request immediate nurse transfer |
| unclear | Describe vague symptoms, unsure what is needed |

---

## Example Output

```
Scenario: cancel - Cancel an appointment scheduled for tomorrow

Patient: Hi, I need to cancel my appointment that's scheduled for tomorrow.
Agent:   Thank you for calling Pivot Point Orthopedics. May I have your first and last name?
Patient: Sarah Miller.
Agent:   Your profile is set up. How may I help you today?
Patient: I need to cancel my appointment scheduled for tomorrow.
Agent:   I'm unable to cancel your appointment right now. I'll connect you to our patient support team.

Transcript saved: transcripts/call_cancel_20260625_154355.txt
```

---

## Project Structure

```
AthenaVoiceQA/
├── app.py              # Flask webhook server (Twilio callbacks)
├── bot.py              # Patient bot — intent detection + dialogue state
├── caller.py           # Outbound call trigger via Twilio
├── transcripts/        # Auto-saved call transcripts (.txt)
├── recordings/         # MP3 call recordings
├── bug_report.md       # Bugs found in Athena agent
├── architecture.md     # System design overview
├── .env.example        # Environment variable template
└── requirements.txt    # Python dependencies
```

---

## Limitations

- Supports English conversations only
- Designed specifically for Athena's call flow
- Requires active Twilio and OpenAI API credentials
- ngrok free tier generates a new URL on each restart

---

## Future Work

- Automatic bug classification by category
- Conversation quality scoring
- Multi-turn regression test suite
- Dashboard for QA reports across multiple calls
- Support for additional healthcare voice agents
