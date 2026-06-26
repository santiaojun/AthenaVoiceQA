from openai import OpenAI
from rapidfuzz import fuzz
import os
import time
import random
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SCENARIOS = [
    ("scheduling", "Schedule an appointment for next Monday at 2pm"),
    ("refill", "Get a refill on a prescription for lisinopril"),
    ("hours", "Find out the office hours"),
    ("cancel", "Cancel an appointment scheduled for tomorrow"),
    ("insurance", "Check if the office accepts Blue Cross Blue Shield insurance"),
    ("reschedule", "Reschedule an appointment to sometime on Friday"),
    ("test_results", "Ask about recent test results"),
    ("weekend", "Ask if you can come in on Sunday at 10am"),
    ("urgent", "I'm not feeling well and need to speak with a nurse"),
    ("unclear", "You're not feeling well and unsure if you need an appointment"),
]

SCENARIO_RESPONSES = {
    "scheduling": "I'd like to book an appointment for next Monday at 2pm please.",
    "refill": "I need a refill on my lisinopril prescription.",
    "hours": "I was wondering what your office hours are.",
    "cancel": "I need to cancel my appointment scheduled for tomorrow.",
    "insurance": "I wanted to check if you accept Blue Cross Blue Shield insurance.",
    "reschedule": "I need to reschedule my appointment to sometime Friday.",
    "test_results": "I have a question about my recent test results.",
    "weekend": "I was hoping to come in on Sunday around 10am.",
    "urgent": "I'm not feeling well and I'd like to speak with a nurse please.",
    "unclear": "I'm not feeling well and I'm not sure what I need.",
}

PATIENT_INFO = {
    "name": ["Sarah Miller", "My name is Sarah Miller.", "It's Sarah Miller."],
    "first_name": ["Sarah"],
    "last_name": ["Miller"],
    "dob": ["July 4th, 1985", "My birthday is July fourth, nineteen eighty-five.", "It's July fourth, nineteen eighty-five.", "July fourth, nineteen eighty-five."],
    "phone": ["My number is 555-234-5678.", "It's 555-234-5678.", "555-234-5678.", "Sure, it's 555-234-5678."],
    "email": ["sarah.miller@email.com", "It's sarah.miller@email.com."],
    "address": ["123 Main Street, California", "It's 123 Main Street."],
    "state": ["California"],
    "insurance": ["Blue Cross Blue Shield PPO", "It's Blue Cross Blue Shield PPO.", "Blue Cross Blue Shield."],
    "member_id": ["BCB123456789", "It's BCB123456789."],
    "group_number": ["GRP001234", "The group number is GRP001234."],
    "pharmacy": ["CVS Pharmacy on Main Street", "It's CVS on Main Street.", "CVS on Main Street."],
}

VERIFY_RESPONSES = ["Yes.", "That's correct.", "Correct.", "Yes, that's right.", "That's right."]

GOAL_COMPLETED_SIGNALS = [
    "has been cancelled",
    "has been scheduled",
    "appointment is confirmed",
    "have been scheduled",
    "refill has been sent",
    "refill request",
    "we'll get that refill",
    "i've noted",
    "i have noted",
    "we have noted",
    "has been rescheduled",
    "have rescheduled",
    "office hours are",
    "we are open",
    "we're open",
    "clinic is open",
    "insurance is accepted",
    "we do accept",
    "yes we accept",
    "support team will review",
    "nurse will",
    "doctor will",
    "provider will",
    "someone will",
    "we will have",
    "we'll have",
    "sent the link",
    "send you a link",
    "text you a link",
    "sending you a link",
    "sent you a text",
    "upload your card",
    "uploading your card",
    "let me know when you finish",
    "let me know when you're done",
    "take your time",
    "i'm here if you need",
]

INTENT_EXAMPLES = {
    "ASK_NAME": ["what's your name", "your full name", "first and last name", "name to get started", "tell me your name", "may i have your name"],
    "ASK_FIRST_NAME": ["first name", "your first name"],
    "ASK_LAST_NAME": ["last name", "your last name"],
    "ASK_DOB": ["date of birth", "birthday", "birth date", "dob", "when were you born", "verify birthday", "confirm birthday", "birth date on file"],
    "ASK_PHONE": ["phone number", "your phone", "contact number", "call you back", "your number"],
    "ASK_EMAIL": ["email address", "your email"],
    "ASK_ADDRESS": ["your address", "street address", "home address"],
    "ASK_STATE": ["what state", "state is your plan", "issued in", "plan issued in"],
    "ASK_INSURANCE": ["insurance plan", "insurance provider", "your insurance", "coverage", "insurer"],
    "ASK_MEMBER_ID": ["member id", "member number", "member i.d"],
    "ASK_GROUP": ["group number", "group id"],
    "VERIFY_INFO": ["is that correct", "is this correct", "that correct", "ending in", "on file", "confirm that", "verify that", "does that sound right"],
    "RECORDING_NOTICE": ["recorded for quality", "recorded for training", "espanol", "español"],
    "GOODBYE": ["goodbye", "have a great day", "great day", "take care", "have a good day"],
    "ASK_REASON": ["how can i help", "how may i help", "what can i do for you", "help you today", "assist you today", "what brings you", "reason for your call", "what would you like help with"],
    "WRAP_UP": ["is there anything else", "anything else i can help", "anything else for you", "anything else today", "anything else we can"],
    "ASK_CHOICE": ["would you like to", "would you prefer", "do you want", "morning or afternoon", "tuesday or", "which day", "what day works", "what time works", "or something else"],
}

STATE_OPENING = "OPENING"
STATE_VERIFYING = "VERIFYING"
STATE_HANDLING = "HANDLING"
STATE_CONFIRMING = "CONFIRMING"
STATE_WRAP_UP = "WRAP_UP"
STATE_ENDING = "ENDING"


def classify_intent_local(text: str) -> tuple:
    text_lower = text.lower()
    best_intent = "OTHER"
    best_score = 0

    for intent, examples in INTENT_EXAMPLES.items():
        for ex in examples:
            if ex in text_lower:
                return intent, 100
            score = max(
                fuzz.ratio(ex, text_lower),
                fuzz.partial_ratio(ex, text_lower),
                fuzz.token_set_ratio(ex, text_lower),
            )
            if score > best_score:
                best_score = score
                best_intent = intent

    if best_score >= 75:
        return best_intent, best_score
    return "OTHER", best_score


def classify_intent_openai(text: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            timeout=10,
            messages=[
                {"role": "system", "content": "You classify medical office agent utterances. Reply with ONLY one label."},
                {"role": "user", "content": f"""Labels: ASK_NAME, ASK_FIRST_NAME, ASK_LAST_NAME, ASK_DOB, ASK_PHONE, ASK_EMAIL, ASK_ADDRESS, ASK_STATE, ASK_INSURANCE, ASK_MEMBER_ID, ASK_GROUP, VERIFY_INFO, RECORDING_NOTICE, GOODBYE, ASK_REASON, WRAP_UP, ASK_CHOICE, OTHER

Agent: "{text}"

Label:"""}
            ],
            max_tokens=10,
            temperature=0.0,
        )
        intent = response.choices[0].message.content.strip().upper()
        return intent if intent in INTENT_EXAMPLES or intent == "OTHER" else "OTHER"
    except Exception as e:
        print(f"OpenAI classify error: {e}")
        return "OTHER"


def check_goal_completed(agent_text: str) -> bool:
    text_lower = agent_text.lower()
    for signal in GOAL_COMPLETED_SIGNALS:
        if signal in text_lower:
            return True
    return False


class PatientBot:
    def __init__(self):
        self.conversation_history = []
        self.turn_count = 0
        self.max_turns = 20
        self.state = STATE_OPENING
        self.goal_stated = False
        self.goal_completed = False
        self.should_hangup = False
        self.repeat_count = 0
        self.last_agent_snippet = ""
        self.last_reply = ""
        self.recent_replies = []
        self.scenario_key, self.current_scenario = self._select_scenario()

    def _select_scenario(self):
        return random.choice(SCENARIOS)

    def get_opening(self):
        self.scenario_key, self.current_scenario = self._select_scenario()
        self.conversation_history = []
        self.turn_count = 0
        self.state = STATE_OPENING
        self.goal_stated = False
        self.goal_completed = False
        self.should_hangup = False
        self.repeat_count = 0
        self.last_agent_snippet = ""
        self.last_reply = ""
        self.recent_replies = []
        openings = {
            "scheduling": "Hi, I'd like to schedule an appointment for next Monday at 2pm.",
            "refill": "Hi, I need to get a refill on my prescription for lisinopril.",
            "hours": "Hi, I was wondering what your office hours are?",
            "cancel": "Hi, I need to cancel my appointment that's scheduled for tomorrow.",
            "insurance": "Hi, I wanted to check if you accept Blue Cross Blue Shield insurance.",
            "reschedule": "Hi, I need to reschedule my upcoming appointment to sometime on Friday.",
            "test_results": "Hi, I recently had some tests done and I have a question about my results.",
            "weekend": "Hi, I was hoping to come in on Sunday around 10am, is that possible?",
            "urgent": "Hi, I'm not feeling well and I'd like to speak with a nurse please.",
            "unclear": "Hi, um, I'm not feeling well and I'm not sure if I need an appointment or what.",
        }
        opening = openings.get(self.scenario_key, "Hi, I need some help please.")
        self.conversation_history.append(f"Patient: {opening}")
        print(f"\nScenario: {self.scenario_key} - {self.current_scenario}")
        return opening

    def _get_info(self, key: str) -> str:
        return random.choice(PATIENT_INFO.get(key, [""]))

    def _check_repeat(self, agent_response: str) -> bool:
        snippet = agent_response[:50].lower()
        if snippet == self.last_agent_snippet:
            self.repeat_count += 1
        else:
            self.repeat_count = 0
            self.last_agent_snippet = snippet
        return self.repeat_count >= 2

    def _check_semantic_loop(self, reply: str) -> bool:
        if len(self.recent_replies) < 2:
            return False
        for prev_reply in self.recent_replies[-2:]:
            similarity = fuzz.token_set_ratio(reply.lower(), prev_reply.lower())
            if similarity > 70:
                print(f"Semantic loop detected (similarity: {similarity})")
                return True
        return False

    def _openai_respond(self, intent: str = "OTHER") -> str:
        last_turns = self.conversation_history[-4:]
        history_text = "\n".join(last_turns)
        for attempt in range(3):
            try:
                start = time.time()
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    timeout=10,
                    messages=[
                        {"role": "system", "content": f"""You are Sarah, a patient calling a medical office.
Goal: {self.current_scenario}
Current state: {self.state}
Goal completed: {self.goal_completed}
Patient info: name Sarah Miller, DOB July 4 1985, phone 555-234-5678, email sarah.miller@email.com, address 123 Main Street California, insurance Blue Cross Blue Shield PPO, member ID BCB123456789, group GRP001234, pharmacy CVS on Main Street.
Reply naturally in under 15 words. Do not say you are an AI. Do not repeat what you just said.
If the conversation seems stuck or goal is done, politely end the call."""},
                        {"role": "user", "content": f"Recent conversation:\n{history_text}\n\nYour reply:"}
                    ],
                    max_tokens=40,
                    temperature=0.1,
                )
                elapsed = time.time() - start
                print(f"OpenAI time: {elapsed:.2f}s")
                reply = response.choices[0].message.content.strip()
                if reply:
                    return reply
            except Exception as e:
                print(f"OpenAI attempt {attempt+1} error: {e}")
                if attempt < 2:
                    time.sleep(0.5 * (attempt + 1))
        return "I'm sorry, could you repeat that?"

    def respond(self, agent_response: str) -> str:
        total_start = time.time()
        self.turn_count += 1
        self.conversation_history.append(f"Agent: {agent_response}")

        print(f"\n{'='*50}")
        print(f"Agent: {agent_response}")
        print(f"State: {self.state} | Goal stated: {self.goal_stated} | Goal completed: {self.goal_completed}")

        if self.turn_count >= self.max_turns:
            self.should_hangup = True
            reply = "Thank you so much for your help. Goodbye."
            self.conversation_history.append(f"Patient: {reply}")
            return reply

        # Detect goal completion
        if not self.goal_completed and self.goal_stated:
            if check_goal_completed(agent_response):
                self.goal_completed = True
                self.state = STATE_CONFIRMING
                print("Goal completed detected!")

        # Repeat detection
        if self._check_repeat(agent_response):
            if self.repeat_count == 2:
                reply = "I'm sorry, I didn't quite catch that."
            elif self.repeat_count == 3:
                reply = "Could you please repeat that?"
            else:
                self.should_hangup = True
                reply = "Thank you for your help. Goodbye!"
            self.conversation_history.append(f"Patient: {reply}")
            print(f"Reply (repeat): {reply}")
            print(f"Total latency: {time.time()-total_start:.2f}s")
            return reply

        # Local intent classification
        intent, score = classify_intent_local(agent_response)
        source = "local"
        if intent == "OTHER":
            intent = classify_intent_openai(agent_response)
            source = "openai"
        print(f"Intent: {intent} (score: {score}, source: {source})")

        reply = self._decide_reply(intent, agent_response)

        # Check for semantic loop
        if self._check_semantic_loop(reply):
            print("Breaking semantic loop with OpenAI...")
            reply = self._openai_respond("BREAK_LOOP")

        # Track recent replies
        self.recent_replies.append(reply)
        if len(self.recent_replies) > 4:
            self.recent_replies.pop(0)

        self.last_reply = reply
        print(f"Reply: {reply}")
        print(f"Total latency: {time.time()-total_start:.2f}s")
        self.conversation_history.append(f"Patient: {reply}")
        return reply

    def _decide_reply(self, intent: str, agent_response: str) -> str:

        if intent == "RECORDING_NOTICE":
            self.state = STATE_OPENING
            return "Yes, that's fine."

        if intent == "GOODBYE":
            self.should_hangup = True
            self.state = STATE_ENDING
            return "Thank you, goodbye!"

        if intent == "WRAP_UP":
            if self.goal_completed:
                self.should_hangup = True
                self.state = STATE_ENDING
                return "No, that's all. Thank you so much. Goodbye!"
            elif self.goal_stated:
                return self._openai_respond(intent)
            else:
                self.goal_stated = True
                self.state = STATE_HANDLING
                return SCENARIO_RESPONSES.get(self.scenario_key, "I need some assistance please.")

        if intent == "ASK_REASON":
            if not self.goal_stated:
                self.goal_stated = True
                self.state = STATE_HANDLING
                return SCENARIO_RESPONSES.get(self.scenario_key, "I need some assistance please.")
            elif self.goal_completed:
                self.should_hangup = True
                self.state = STATE_ENDING
                return "No, that's everything. Thank you so much. Goodbye!"
            else:
                return self._openai_respond(intent)

        if intent == "ASK_CHOICE":
            if not self.goal_stated:
                self.goal_stated = True
                self.state = STATE_HANDLING
                return SCENARIO_RESPONSES.get(self.scenario_key, "I need some assistance please.")
            else:
                return self._openai_respond(intent)

        if intent == "VERIFY_INFO":
            self.state = STATE_VERIFYING
            return random.choice(VERIFY_RESPONSES)

        info_map = {
            "ASK_NAME": "name",
            "ASK_FIRST_NAME": "first_name",
            "ASK_LAST_NAME": "last_name",
            "ASK_DOB": "dob",
            "ASK_PHONE": "phone",
            "ASK_EMAIL": "email",
            "ASK_ADDRESS": "address",
            "ASK_STATE": "state",
            "ASK_INSURANCE": "insurance",
            "ASK_MEMBER_ID": "member_id",
            "ASK_GROUP": "group_number",
        }

        if intent in info_map:
            self.state = STATE_VERIFYING

            if intent == "ASK_DOB":
                text_lower = agent_response.lower()
                if "i have your" in text_lower or "date of birth is" in text_lower or "birthday is" in text_lower or "birth is" in text_lower:
                    return random.choice(VERIFY_RESPONSES)

            if intent == "ASK_PHONE":
                text_lower = agent_response.lower()
                if "pharmacy" in text_lower or "location" in text_lower or "street" in text_lower or "city" in text_lower:
                    return self._openai_respond(intent)

            reply = self._get_info(info_map[intent])

            if self.last_reply and (reply.lower() in self.last_reply.lower() or self.last_reply.lower() in reply.lower()):
                print("Duplicate reply detected, using OpenAI instead")
                return self._openai_respond(intent)

            return reply

        # OTHER
        if not self.goal_stated:
            self.goal_stated = True
            self.state = STATE_HANDLING
            return SCENARIO_RESPONSES.get(self.scenario_key, "I need some assistance please.")
        else:
            self.state = STATE_HANDLING
            return self._openai_respond(intent)

    def should_end(self):
        return self.turn_count >= self.max_turns

    def get_transcript(self):
        return "\n".join(self.conversation_history)