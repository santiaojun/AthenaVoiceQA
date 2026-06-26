from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from bot import PatientBot
import os
import time
import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
bot = PatientBot()
silence_count = 0

@app.route("/answer", methods=["GET", "POST"])
def answer():
    global silence_count
    silence_count = 0
    opening = bot.get_opening()
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action="/respond",
        timeout=20,
        speech_timeout=3,
        action_on_empty_result=True,
    )
    gather.say(opening, voice="Polly.Joanna-Neural")
    response.append(gather)
    return Response(str(response), mimetype="text/xml")

@app.route("/respond", methods=["GET", "POST"])
def respond():
    global silence_count
    start = time.time()
    speech_input = request.form.get("SpeechResult", "")

    print("=" * 50)
    print(f"Speech Input: {speech_input}")

    # 沉默处理
    if not speech_input.strip():
        silence_count += 1
        print(f"Silence detected ({silence_count})")
        response = VoiceResponse()
        if silence_count == 1:
            gather = Gather(
                input="speech",
                action="/respond",
                timeout=20,
                speech_timeout=3,
                action_on_empty_result=True,
            )
            gather.say("Hello? Are you still there?", voice="Polly.Joanna-Neural")
            response.append(gather)
        else:
            response.say("It seems the line has gone quiet. Thank you for calling, goodbye!", voice="Polly.Joanna-Neural")
            response.hangup()
            _save_transcript()
        return Response(str(response), mimetype="text/xml")

    silence_count = 0
    bot_reply = bot.respond(speech_input)

    print(f"Bot Reply: {bot_reply}")
    print(f"Elapsed: {time.time() - start:.2f}s")

    response = VoiceResponse()
    if bot.should_end() or bot.should_hangup:
        response.say(bot_reply, voice="Polly.Joanna-Neural")
        response.hangup()
    else:
        gather = Gather(
            input="speech",
            action="/respond",
            timeout=20,
            speech_timeout=3,
            action_on_empty_result=True,
        )
        gather.say(bot_reply, voice="Polly.Joanna-Neural")
        response.append(gather)

    return Response(str(response), mimetype="text/xml")

@app.route("/hangup", methods=["GET", "POST"])
def hangup():
    _save_transcript()
    return Response("", mimetype="text/xml")

def _save_transcript():
    try:
        if not bot.conversation_history:
            print("No conversation to save.")
            return
        os.makedirs("transcripts", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcripts/call_{bot.scenario_key}_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Scenario: {bot.scenario_key}\n")
            f.write(f"Goal: {bot.current_scenario}\n")
            f.write(f"Time: {timestamp}\n")
            f.write("=" * 50 + "\n")
            f.write(bot.get_transcript())
        print(f"Transcript saved: {filename}")
    except Exception as e:
        print(f"Failed to save transcript: {e}")

if __name__ == "__main__":
    app.run(port=5000, debug=True)