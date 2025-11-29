import streamlit as st
import time
import pandas as pd
from simulator import VitalsSimulator
from monitor import VitalsMonitor
from agent import MedicalAgent
from notifier import WhatsAppNotifier
import os
from dotenv import load_dotenv

load_dotenv()

# Page Config
st.set_page_config(page_title="Vitalia - AI Health Monitor", page_icon="❤️", layout="wide")

# Initialize Session State
if 'simulator' not in st.session_state:
    st.session_state.simulator = VitalsSimulator()
if 'monitor' not in st.session_state:
    st.session_state.monitor = VitalsMonitor()
if 'agent' not in st.session_state:
    st.session_state.agent = MedicalAgent()
if 'notifier' not in st.session_state:
    st.session_state.notifier = WhatsAppNotifier()
if 'vitals_history' not in st.session_state:
    st.session_state.vitals_history = []
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False
if 'abnormal_detected' not in st.session_state:
    st.session_state.abnormal_detected = False
if 'abnormal_start_time' not in st.session_state:
    st.session_state.abnormal_start_time = None
if 'ai_result' not in st.session_state:
    st.session_state.ai_result = None

# Simulation State
if 'sim_hr' not in st.session_state:
    st.session_state.sim_hr = False
if 'sim_spo2' not in st.session_state:
    st.session_state.sim_spo2 = False
if 'sim_bp' not in st.session_state:
    st.session_state.sim_bp = False
if 'sim_temp' not in st.session_state:
    st.session_state.sim_temp = False

# Sidebar
st.sidebar.title("Vitalia Controls")
start_btn = st.sidebar.button("Start Monitoring")
stop_btn = st.sidebar.button("Stop Monitoring")

st.sidebar.divider()
st.sidebar.subheader("Doctor's Contact")
doctor_phone = os.getenv("DOCTOR_PHONE_NUMBER", "")
if doctor_phone:
    st.sidebar.success(f"Linked: {doctor_phone}")
else:
    st.sidebar.error("No Number Configured")

auto_send = st.sidebar.checkbox("Auto-send Reports", value=False,
                                help="Automatically send report to doctor when abnormality is detected")

if start_btn:
    st.session_state.monitoring = True
if stop_btn:
    st.session_state.monitoring = False

# Custom CSS for Vitals Cards
st.markdown("""
<style>
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .vital-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #4F4F4F;
        text-align: center;
        margin-bottom: 10px;
    }
    .vital-label {
        font-size: 16px;
        color: #FAFAFA;
        margin-bottom: 5px;
    }
    .vital-value {
        font-size: 36px; /* Increased size */
        font-weight: bold;
    }
    .vital-unit {
        font-size: 14px;
        color: #A0A0A0;
    }
    .vital-normal {
        color: #00FF00; /* Green */
    }
    .vital-abnormal {
        color: #FF0000; /* Red */
        animation: blink 1s infinite;
    }
</style>
""", unsafe_allow_html=True)

# Main Layout
st.title("Vitalia")

col1, col2 = st.columns([2, 1])


@st.fragment(run_every=1)
def run_vitals_monitor():
    if st.session_state.monitoring:
        # Generate Vitals
        abnormal_flags = {
            'hr': st.session_state.sim_hr,
            'spo2': st.session_state.sim_spo2,
            'bp': st.session_state.sim_bp,
            'temp': st.session_state.sim_temp
        }
        vitals = st.session_state.simulator.generate_vitals(abnormal_flags=abnormal_flags)
        st.session_state.vitals_history.append(vitals)

        # Keep history manageable
        if len(st.session_state.vitals_history) > 50:
            st.session_state.vitals_history.pop(0)

        # Monitor Check
        analysis = st.session_state.monitor.check_vitals(vitals)
        details = analysis.get("details", {})  # Get per-vital status

        if analysis["status"] == "ABNORMAL":
            st.error(f"⚠️ ABNORMAL DETECTED: {', '.join(analysis['abnormalities'])}")
            st.session_state.abnormal_detected = True

            # Auto-Analysis Logic
            if st.session_state.abnormal_start_time is None:
                st.session_state.abnormal_start_time = time.time()
                # Initialize last run time to start time so we wait 10s first
                st.session_state.last_auto_analysis_time = st.session_state.abnormal_start_time

            # Check if 10 seconds have passed since the last analysis (or start)
            if time.time() - st.session_state.last_auto_analysis_time > 10:
                patient_advice, doctor_report, emergency = st.session_state.agent.analyze(vitals,
                                                                                          "Auto-detected abnormality. Patient has not provided symptoms yet.")
                st.session_state.ai_result = {
                    "patient": patient_advice,
                    "doctor": doctor_report,
                    "emergency": emergency
                }

                # Auto-send logic
                if auto_send and doctor_phone:
                    msg_body = f"{doctor_report}\n\nNo-reply: This is from vAItal"
                    st.session_state.notifier.send_whatsapp_message(msg_body, doctor_phone)

                # Update last run time to NOW to reset the 10s timer
                st.session_state.last_auto_analysis_time = time.time()

        else:
            st.success("Status: Normal")
            st.session_state.abnormal_detected = False
            st.session_state.abnormal_start_time = None
            st.session_state.auto_analysis_done = False

        # Display Vitals with Custom Cards and Graphs
        df = pd.DataFrame(st.session_state.vitals_history)

        # Helper to get class based on status
        def get_status_class(vital_key):
            return "vital-abnormal" if details.get(vital_key) == "ABNORMAL" else "vital-normal"

        # Row 1
        r1_c1, r1_c2 = st.columns(2)

        with r1_c1:
            with st.container(border=True):
                st.markdown(f"""
                <div class="vital-card">
                    <div class="vital-label">Heart Rate</div>
                    <div class="vital-value {get_status_class('heart_rate')}">{vitals['heart_rate']}</div>
                    <div class="vital-unit">bpm</div>
                </div>
                """, unsafe_allow_html=True)
                st.line_chart(df["heart_rate"], height=150, color="#FF4B4B")
                st.session_state.sim_hr = st.checkbox("Simulate", key="chk_hr", value=st.session_state.sim_hr, label_visibility="collapsed")

        with r1_c2:
            with st.container(border=True):
                st.markdown(f"""
                <div class="vital-card">
                    <div class="vital-label">SpO2</div>
                    <div class="vital-value {get_status_class('spo2')}">{vitals['spo2']}</div>
                    <div class="vital-unit">%</div>
                </div>
                """, unsafe_allow_html=True)
                st.line_chart(df["spo2"], height=150, color="#00CC96")
                st.session_state.sim_spo2 = st.checkbox("Simulate", key="chk_spo2", value=st.session_state.sim_spo2, label_visibility="collapsed")

        # Row 2
        r2_c1, r2_c2 = st.columns(2)

        with r2_c1:
            with st.container(border=True):
                st.markdown(f"""
                <div class="vital-card">
                    <div class="vital-label">Blood Pressure</div>
                    <div class="vital-value {get_status_class('bp')}">{vitals['sys_bp']}/{vitals['dia_bp']}</div>
                    <div class="vital-unit">mmHg</div>
                </div>
                """, unsafe_allow_html=True)
                st.line_chart(df[["sys_bp", "dia_bp"]], height=150)
                st.session_state.sim_bp = st.checkbox("Simulate", key="chk_bp", value=st.session_state.sim_bp, label_visibility="collapsed")

        with r2_c2:
            with st.container(border=True):
                st.markdown(f"""
                <div class="vital-card">
                    <div class="vital-label">Temperature</div>
                    <div class="vital-value {get_status_class('temperature')}">{vitals['temperature']}</div>
                    <div class="vital-unit">°C</div>
                </div>
                """, unsafe_allow_html=True)
                st.line_chart(df["temperature"], height=150, color="#FFA15A")
                st.session_state.sim_temp = st.checkbox("Simulate", key="chk_temp", value=st.session_state.sim_temp, label_visibility="collapsed")
    else:
        st.info("Monitoring Stopped. Press 'Start Monitoring' to begin.")


@st.fragment(run_every=1)
def display_ai_results():
    if st.session_state.ai_result:
        res = st.session_state.ai_result

        st.markdown("## Advising Patient")
        st.info(res["patient"])

        st.markdown("## Reporting Doctor")
        st.warning(res["doctor"])

        if res["emergency"]:
            st.error("🚨 EMERGENCY ALERT SENT TO HOSPITAL 🚨")
        else:
            st.success("Situation Is Stable. Follow advice.")

        if st.button("Send Report to Doctor via WhatsApp"):
            if doctor_phone:
                with st.spinner("Sending WhatsApp message..."):
                    msg_body = f"{res['doctor']}\n\nNo-reply: This is from vAItal"
                    success, msg = st.session_state.notifier.send_whatsapp_message(msg_body, doctor_phone)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
            else:
                st.warning("Please enter a Doctor's WhatsApp number in the sidebar.")


with col1:
    st.subheader("Monitoring Live Vitals")
    run_vitals_monitor()

with col2:
    st.subheader("Vitalia Support")

    with st.form("symptom_form"):
        symptoms = st.text_input("How are you feeling? (Describe symptoms)", key="symptoms_input")
        submit_symptoms = st.form_submit_button("Analyze")

        if submit_symptoms:
            if not st.session_state.monitoring:
                st.warning("Please start monitoring first.")
            elif not st.session_state.vitals_history:
                st.warning("No vitals data yet.")
            else:
                # Use the latest vitals
                latest_vitals = st.session_state.vitals_history[-1]

                with st.spinner("Vitalia is analyzing..."):
                    patient_advice, doctor_report, emergency = st.session_state.agent.analyze(latest_vitals, symptoms)

                    st.session_state.ai_result = {
                        "patient": patient_advice,
                        "doctor": doctor_report,
                        "emergency": emergency
                    }
                    st.session_state.auto_analysis_done = True  # Mark as done so auto doesn't overwrite immediately
                    st.rerun()

    display_ai_results()
