import os
os.environ["CREWAI_TELEMETRY_DISABLED"] = "true"
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew, LLM
import chromadb

def styled_section(title, content):
    st.markdown(
        f"""
        <div style="
            padding:16px;
            border-radius:10px;
            background-color:#f6f8fa;
            margin-bottom:15px;
        ">
        <h4>{title}</h4>
        <p>{content}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------
# Page Config
# -------------------------
st.set_page_config(
    page_title="AI Gym Planner",
    page_icon="💪",
    layout="centered"
)

st.title("💪 AI Gym, Diet & Lifestyle Planner")
st.caption("Personalized • Safe • Sustainable Fitness Plans")

# -------------------------
# LLM
# -------------------------
llm = LLM(model="gemini/gemini-2.5-flash")

# -------------------------
# ChromaDB
# -------------------------
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("gym_user_profiles")

# -------------------------
# UI – User Questions
# -------------------------
st.header("📋 Your Details")

with st.form("user_form"):
    age = st.text_input("Age")
    gender = st.selectbox("Gender (optional)", ["Prefer not to say", "Male", "Female", "Other"])
    height = st.text_input("Height (cm)")
    weight = st.text_input("Weight (kg)")

    st.subheader("🎯 Fitness Goals")
    goal = st.selectbox(
        "Main Goal",
        ["Fat Loss", "Muscle Gain", "Strength", "General Fitness"]
    )

    st.subheader("🥗 Diet Preferences")
    diet_type = st.selectbox(
        "Diet Type",
        ["No Preference", "Vegetarian", "Non-Vegetarian", "Vegan"]
    )
    allergies = st.text_input("Food allergies or dislikes (optional)")

    st.subheader("🌱 Lifestyle")
    activity = st.selectbox("Daily Activity Level", ["Low", "Moderate", "High"])
    sleep = st.slider("Average Sleep Hours", 4, 10, 7)

    submitted = st.form_submit_button("🚀 Generate My Plan")

# -------------------------
# On Submit
# -------------------------
if submitted:
    user_profile = {
        "Age": age,
        "Gender": gender,
        "Height": height,
        "Weight": weight,
        "Goal": goal,
        "Diet Type": diet_type,
        "Allergies": allergies,
        "Activity Level": activity,
        "Sleep Hours": sleep
    }

    profile_text = "\n".join([f"{k}: {v}" for k, v in user_profile.items()])

    # Save to ChromaDB
    collection.add(
        documents=[profile_text],
        ids=["current_user"]
    )

    st.success("✅ Profile saved. Generating your personalized plan...")

    # -------------------------
    # Agents
    # -------------------------
    workout_agent = Agent(
        role="Workout Coach",
        goal="Create a safe and effective workout plan",
        backstory="A certified gym coach focused on balanced training and injury prevention.",
        llm=llm
    )

    diet_agent = Agent(
        role="Diet Planner",
        goal="Design a healthy, balanced diet plan",
        backstory="A nutrition assistant focused on sustainable eating habits.",
        llm=llm
    )

    lifestyle_agent = Agent(
        role="Lifestyle Coach",
        goal="Improve recovery, sleep, and daily habits",
        backstory="A wellness coach for long-term fitness success.",
        llm=llm
    )

    # -------------------------
    # Tasks
    # -------------------------
    workout_task = Task(
    description=f"""
    Create a safe, beginner-to-intermediate workout plan.

    FORMAT STRICTLY AS:
    ### 🏋️ Workout Plan
    - Weekly split
    - Exercises
    - Sets & reps
    - Rest days

    USER PROFILE:
    {profile_text}
    """,
    agent=workout_agent,
    expected_output="A clearly formatted weekly workout plan."
)



    diet_task = Task(
    description=f"""
    Create a healthy, sustainable diet plan.

    FORMAT EXACTLY LIKE THIS:

    🥗 Daily Meal Plan
    - Breakfast:
    - Lunch:
    - Dinner:
    - Snacks:

    💧 Hydration
    - Water intake per day

    🧮 Nutrition Tips
    - Protein intake
    - Carb quality
    - Healthy fats

    ⚠️ Notes
    - Foods to limit
    - Allergy considerations

    USER PROFILE:
    {profile_text}
    """,
    agent=diet_agent,
    expected_output="A clearly structured daily diet plan with headings and bullet points."
)



    lifestyle_task = Task(
    description=f"""
    Suggest lifestyle improvements to support fitness progress.

    FORMAT EXACTLY LIKE THIS:

    🌙 Sleep
    - Ideal sleep duration
    - Bedtime routine tips

    🔄 Recovery
    - Rest days
    - Stretching or mobility

    🧠 Mental Wellness
    - Stress management
    - Motivation tips

    📅 Daily Habits
    - Simple habits to stay consistent

    USER PROFILE:
    {profile_text}
    """,
    agent=lifestyle_agent,
    expected_output="Clearly structured lifestyle recommendations."
)


    crew = Crew(
        agents=[workout_agent, diet_agent, lifestyle_agent],
        tasks=[workout_task, diet_task, lifestyle_task],
        verbose=False
    )

    with st.spinner("🧠 AI agents are working..."):
        result = crew.kickoff()

    # -------------------------
    # Output UI
    # -------------------------
    st.header("🏆 Your Personalized Fitness Plan")

    st.markdown("---")

    # Profile Summary
    st.subheader("📋 Your Profile")
    cols = st.columns(3)

    cols[0].metric("Age", age)
    cols[1].metric("Height (cm)", height)
    cols[2].metric("Weight (kg)", weight)

    cols2 = st.columns(3)
    cols2[0].metric("Goal", goal)
    cols2[1].metric("Diet", diet_type)
    cols2[2].metric("Activity", activity)

    st.markdown("---")

    # Tabs for plans
    tab1, tab2, tab3 = st.tabs(["🏋️ Workout", "🥗 Diet", "🌱 Lifestyle"])

    with tab1:
        st.subheader("🏋️ Workout Plan")

        styled_section("🗓️ Weekly Split", result)
        styled_section("🏋️ Exercises", result)
        styled_section("⏱️ Rest & Recovery", result)
        styled_section("⚠️ Safety Tips", result)


    with tab2:
        st.subheader("🥗 Diet Plan")

        styled_section("🍳 Breakfast", result)
        styled_section("🥗 Lunch", result)
        styled_section("🍲 Dinner", result)
        styled_section("🍎 Snacks", result)
        styled_section("⚠️ Diet Tips", result)

    with tab3:
        st.subheader("🌱 Lifestyle Plan")

        styled_section("🛌 Sleep & Recovery", result)
        styled_section("💧 Hydration", result)
        styled_section("📋 Daily Habits", result)
        styled_section("⚠️ Wellness Tips", result)

    st.success("✨ Consistency beats perfection. Progress comes with patience.")