import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(override=True)


class MedicalAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in .env")
            self.model = None
        else:
            print(f"Agent loaded API Key: {api_key[:5]}... (Length: {len(api_key)})")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.chat = self.model.start_chat(history=[])
            self._initialize_persona()

    def _initialize_persona(self):
        if self.model:
            system_prompt = """
            You are vAItal, a calm and professional medical AI assistant. 
            Your goal is to analyze user vitals and symptoms to provide:
            1. Calming advice to the user.
            2. An assessment of whether an emergency alert is needed.
            3. If emergency alert is needed, summarize the user's condition concisely, suggest what could be happening to patient, include all vital signs and reported symptoms. Recommend the urgency of the situation (e.g., "Immediate attention recommended"), be professional and to the point.

            Keep your responses concise and reassuring. 
            Always prioritize patient safety. 
            If vitals are severely abnormal, recommend immediate medical attention.
            """
            self.chat.send_message(system_prompt)

    def analyze(self, vitals_data, symptoms):
        if not self.model:
            return "AI Module not initialized (Missing API Key).", "", False

        prompt = f"""
        Current Vitals: {vitals_data}
        User Symptoms: {symptoms}

        Please provide three distinct sections separated by "---":

        SECTION 1 (Patient Advice):
        Directly address the patient. Be calming and concise. Give specific advice on what to do immediately.

        ---

        SECTION 2 (Doctor Report):
        For medical professionals. Structured summary including:
        - Patient Condition Summary
        - Vitals Analysis
        - Reported Symptoms
        - Recommended Urgency Level

        ---

        SECTION 3 (Emergency Status):
        Just "YES" or "NO"
        """

        try:
            response = self.chat.send_message(prompt)
            text = response.text

            parts = text.split("---")

            # Default values in case parsing fails
            patient_advice = text
            doctor_report = "Could not parse doctor report."
            emergency = False

            if len(parts) >= 3:
                patient_advice = parts[0].replace("SECTION 1 (Patient Advice):", "").strip()
                doctor_report = parts[1].replace("SECTION 2 (Doctor Report):", "").strip()
                emergency_status = parts[2].replace("SECTION 3 (Emergency Status):", "").strip()
                emergency = "YES" in emergency_status.upper()

            return patient_advice, doctor_report, emergency
        except Exception as e:
            return f"Error communicating with AI: {e}", "", False
