# Bug Report — Pretty Good AI Athena Voice Agent

**Tester:** AthenaVoiceQA Automated Patient Simulator  
**Test Phone:** +17373872003  
**Target:** +18054398008  
**Date:** June 2026  

---

## Bug #1 — Agent Sent Refill to Unconfirmed Pharmacy Address

**Severity:** Critical  
**Scenario:** Refill  
**Call:** call_refill_20260626_120552.txt  
**Timestamp:** Final portion of call  

**Description:**  
The patient clearly and repeatedly stated their pharmacy as "CVS at 456 Oak Avenue, Los Angeles, CA 90001." The agent could not verify this address and substituted a completely different CVS location at "5837 South Central Avenue" without asking the patient to confirm the change.

**Expected behavior:**  
Agent should not substitute a different pharmacy address without explicit patient confirmation. If the address cannot be verified, agent should ask the patient to confirm the alternative, escalate to a staff member, or ask the patient to contact the pharmacy directly.

**Actual behavior:**  
Agent unilaterally switched the pharmacy to a different address and confirmed processing the refill to that location without patient approval.

**Why this matters:**  
Patient medication sent to the wrong pharmacy is a patient safety issue. The patient may not receive critical medication in time.

---

## Bug #2 — Agent Loops Without Escalating When Patient Cannot Provide Information

**Severity:** High  
**Scenario:** Refill, Insurance  
**Call:** call_refill_20260626_120552.txt  
**Timestamp:** Pharmacy address portion  

**Description:**  
When the patient was unable to provide a verifiable pharmacy address, the agent repeatedly asked for more details (cross streets, zip code, landmarks) for over 10 turns without offering to escalate to a human agent or suggesting an alternative path forward.

**Expected behavior:**  
After 2–3 failed attempts to collect required information, the agent should offer to transfer to a staff member or suggest the patient call back with the correct information.

**Actual behavior:**  
Agent looped the same question repeatedly without escalation, causing the conversation to stall indefinitely and forcing the patient to abandon the call.

---

## Bug #3 — Agent Did Not Acknowledge Potential Specialty Mismatch for Medication Refill

**Severity:** High  
**Scenario:** Refill  
**Call:** call_refill_20260626_120552.txt  
**Timestamp:** After patient states reason for call  

**Description:**  
The patient requested a refill for lisinopril, a cardiovascular medication (ACE inhibitor) used to treat high blood pressure. The clinic is Pivot Point Orthopedics, an orthopedic practice. The agent did not acknowledge that the medication appeared unrelated to the clinic's specialty, nor did it clarify whether this type of refill could be handled by the practice.

**Expected behavior:**  
Agent should flag the potential mismatch and ask whether the patient intended to contact a different provider, or confirm whether the clinic handles this type of medication.

**Actual behavior:**  
Agent accepted the refill request and proceeded to process it without any acknowledgment of the specialty mismatch.

---

## Bug #4 — Demo Date of Birth Assigned Without Patient Confirmation

**Severity:** Medium  
**Scenario:** All scenarios  
**Call:** Multiple calls  
**Timestamp:** Profile creation step  

**Description:**  
During demo profile creation, the agent automatically assigned a date of birth of "July 4th, 2000" without asking the patient to confirm or provide their real date of birth. A patient unfamiliar with the demo flow could mistake this for their actual medical record.

**Expected behavior:**  
Agent should clearly communicate that the date of birth is a demo placeholder and does not reflect the patient's real information, or ask the patient to provide their actual date of birth.

**Actual behavior:**  
Agent stated "your date of birth is July 4th 2000 for demo purposes" and moved on without any confirmation step.

---

## Bug #5 — Appointment Cancellation Always Transferred to Human Support

**Severity:** Medium  
**Scenario:** Cancel  
**Call:** call_cancel transcripts  
**Timestamp:** After patient states reason for call  

**Description:**  
When a patient requested to cancel an appointment, the agent responded "I'm unable to cancel your appointment right now" and immediately transferred to patient support rather than attempting to handle the request.

**Note:** It is possible this reflects an intentional product decision to route cancellations to human staff. However, if self-service cancellation is a supported use case, this behavior significantly limits the usefulness of the automated voice channel for one of the most common patient requests.

**Expected behavior (if self-service is supported):**  
Agent should be able to process a cancellation directly, or at minimum confirm the request and inform the patient it will be handled.

**Actual behavior:**  
Agent transferred immediately without attempting to process the request or explaining why self-service cancellation is unavailable.

---

## Bug #6 — Demo Profile Creation Uses Wrong Specialty Label

**Severity:** Low  
**Scenario:** All scenarios  
**Call:** Multiple calls  
**Timestamp:** Beginning of each call  

**Description:**  
When creating the demo patient profile, the agent stated "your dental patient profile is set up" — incorrect for an orthopedic clinic.

**Expected behavior:**  
Agent should say "orthopedic patient profile" or simply "patient profile."

**Actual behavior:**  
Agent said "dental patient profile."

---

## Summary

| # | Bug | Severity | Scenario |
|---|-----|----------|----------|
| 1 | Refill sent to unconfirmed pharmacy address | Critical | Refill |
| 2 | No escalation after repeated failed info collection | High | Refill, Insurance |
| 3 | Specialty mismatch not acknowledged for medication refill | High | Refill |
| 4 | Demo DOB assigned without patient confirmation | Medium | All |
| 5 | Appointment cancellation always transferred to human | Medium | Cancel |
| 6 | Wrong specialty label in demo profile creation | Low | All |
