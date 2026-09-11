import json
import os
import re
import tempfile
from datetime import date

from groq import Groq
from gtts import gTTS
import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS — PROFESSIONAL UI
# ============================================================

st.markdown(
    """
<style>

.stApp {
    background: linear-gradient(135deg, #eef4ff 0%, #f8f5ff 100%);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #172554 0%, #312e81 100%);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.hero {
    background: linear-gradient(
        135deg,
        #312e81,
        #4f46e5,
        #2563eb
    );
    padding: 38px;
    border-radius: 25px;
    color: white;
    box-shadow: 0 10px 30px rgba(37, 99, 235, 0.25);
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 46px;
    margin-bottom: 8px;
    font-weight: 800;
}

.hero p {
    font-size: 19px;
    margin-top: 5px;
}

.visual-box {
    background: white;
    padding: 25px;
    border-radius: 22px;
    text-align: center;
    border: 1px solid #dbeafe;
    box-shadow: 0 8px 25px rgba(30, 64, 175, 0.10);
}

.visual-icon {
    font-size: 85px;
}

.feature-card {
    background: white;
    padding: 23px;
    border-radius: 20px;
    min-height: 180px;
    border: 1px solid #e0e7ff;
    box-shadow: 0 6px 18px rgba(30, 64, 175, 0.08);
    transition: 0.2s;
}

.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 25px rgba(30, 64, 175, 0.15);
}

.feature-icon {
    font-size: 38px;
}

.feature-title {
    font-size: 21px;
    font-weight: 700;
    color: #1e1b4b;
}

.feature-text {
    color: #475569;
}

.config-connected {
    background: #ecfdf5;
    border: 2px solid #10b981;
    padding: 16px;
    border-radius: 15px;
    color: #065f46;
    font-weight: 700;
}

.config-error {
    background: #fff1f2;
    border: 2px solid #f43f5e;
    padding: 16px;
    border-radius: 15px;
    color: #9f1239;
    font-weight: 700;
}

.agent-box {
    background: linear-gradient(
        135deg,
        #eef2ff,
        #f5f3ff
    );
    padding: 25px;
    border-radius: 20px;
    border-left: 6px solid #4f46e5;
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    text-align: center;
    border: 1px solid #e0e7ff;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# GROQ CONFIGURATION
# ============================================================


def get_api_key():
  try:
    if "GROQ_API_KEY" in st.secrets:
      return st.secrets["GROQ_API_KEY"]
  except Exception:
    pass

  return os.getenv("GROQ_API_KEY")


API_KEY = get_api_key()

if API_KEY:
  client = Groq(api_key=API_KEY)
else:
  client = None

# UPDATED TO ACTIVE GROQ MODEL
MODEL = "openai/gpt-oss-20b"

# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "quiz_data": [],
    "quiz_topic": "",
    "quiz_submitted": False,
    "last_score": None,
    "last_topic": "",
    "weak_topics": [],
    "progress": [],
    "summary": "",
    "mcqs": [],
    "recommendation": "",
}

for key, value in defaults.items():
  if key not in st.session_state:
    st.session_state[key] = value


# ============================================================
# AI FUNCTION
# ============================================================


def ask_ai(prompt, system_prompt=None):
  if not client:
    return "ERROR_API_KEY"

  if system_prompt is None:
    system_prompt = """
You are StudyMate AI, an intelligent educational assistant for students of all levels.

Give accurate, simple, and highly adaptive answers tailored to the user's specific query level.

Use:
- clear headings
- easy language
- examples where useful
- step-by-step explanations when needed

Do not use unnecessarily difficult vocabulary.
"""

  try:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=2500,
    )

    return response.choices[0].message.content

  except Exception as e:
    return f"ERROR: {str(e)}"


# ============================================================
# JSON PARSER
# ============================================================


def extract_json(text):
  try:
    return json.loads(text)
  except:
    pass

  cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE)

  cleaned = cleaned.replace("```", "").strip()

  try:
    return json.loads(cleaned)
  except:
    pass

  start = cleaned.find("[")
  end = cleaned.rfind("]")

  if start != -1 and end != -1:
    try:
      return json.loads(cleaned[start : end + 1])
    except:
      pass

  start = cleaned.find("{")
  end = cleaned.rfind("}")

  if start != -1 and end != -1:
    try:
      return json.loads(cleaned[start : end + 1])
    except:
      pass

  return None


# ============================================================
# TEXT TO SPEECH
# ============================================================


def create_audio(text):
  try:
    path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name

    tts = gTTS(text=text, lang="en", slow=False)

    tts.save(path)
    return path
  except:
    return None


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    """
    <div style="text-align:center; padding:10px;">
        <div style="font-size:55px;">📚</div>
        <h2>StudyMate AI</h2>
        <p>Your AI Study Partner</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.divider()

page = st.sidebar.radio(
    "📌 Navigation",
    [
        "🏠 Home",
        "📚 Study Tools",
        "🎯 Quiz",
        "🤖 AI Study Coach",
        "📅 Study Planner",
        "📈 Progress Tracker",
        "🧠 Adaptive Learning",
    ],
)

st.sidebar.divider()

# ============================================================
# GROQ STATUS
# ============================================================

st.sidebar.markdown("### 🔑 Groq Configuration")

if API_KEY:
  st.sidebar.markdown(
      """
        <div class="config-connected">
        🟢 Groq API Connected<br>
        AI system is ready!
        </div>
        """,
      unsafe_allow_html=True,
  )
else:
  st.sidebar.markdown(
      """
        <div class="config-error">
        🔴 Groq API Not Connected
        </div>
        """,
      unsafe_allow_html=True,
  )

  st.sidebar.caption("Add GROQ_API_KEY to " ".streamlit/secrets.toml")

st.sidebar.divider()

st.sidebar.caption("Generative AI + Agentic AI")


# ============================================================
# HOME
# ============================================================

if page == "🏠 Home":

  st.markdown(
      """
        <div class="hero">

        <h1>📚 StudyMate AI</h1>

        <p>
        Your Universal AI Study Partner — Learn Smarter, Not Harder.
        </p>

        <p>
        Personalized learning powered by
        Generative AI + Agentic AI 🤖
        </p>

        </div>
        """,
      unsafe_allow_html=True,
  )

  col1, col2 = st.columns([1.5, 1])

  with col1:
    st.markdown(
        """
            ### 🎓 Smarter Learning Starts Here

            StudyMate AI helps students of all levels:

            ✅ Understand difficult topics  
            ✅ Summarize long notes  
            ✅ Generate MCQs  
            ✅ Take interactive quizzes  
            ✅ Analyze performance  
            ✅ Find weak areas  
            ✅ Create personalized study plans  
            ✅ Adapt future practice to performance
            """
    )

    if API_KEY:
      st.success("🟢 Groq AI is connected and ready!")
    else:
      st.warning("🔴 Connect Groq API to use AI features.")

  with col2:
    st.markdown(
        """
            <div class="visual-box">

            <div class="visual-icon">
            👩‍🎓🤖📚
            </div>

            <h2>AI Learning Assistant</h2>

            <p>
            Learn • Practice • Improve
            </p>

            <h3>
            🧠 Personalized<br>
            🎯 Interactive<br>
            🚀 Adaptive
            </h3>

            </div>
            """,
        unsafe_allow_html=True,
    )

  st.write("")
  st.subheader("✨ Everything You Need to Study Better")

  features = [
      (
          "📝",
          "AI Notes Summarizer",
          "Convert long notes into short and easy study material.",
      ),
      ("🎯", "MCQ Generator", "Generate exam-style MCQs from any topic."),
      ("🏆", "Interactive Quiz", "Take quizzes and get automatic scores."),
      ("❓", "Doubt Solver", "Ask questions and get simple explanations."),
      (
          "🤖",
          "AI Study Coach",
          "Get recommendations based on your performance.",
      ),
      (
          "📅",
          "Study Planner",
          "Create a personalized plan for your exam.",
      ),
      ("📈", "Progress Tracker", "Track scores and learning improvement."),
      (
          "🧠",
          "Adaptive Learning",
          "Future practice changes according to your performance.",
      ),
  ]

  cols = st.columns(4)

  for i, feature in enumerate(features):
    with cols[i % 4]:
      st.markdown(
          f"""
                <div class="feature-card">
                <div class="feature-icon">{feature[0]}</div>
                <div class="feature-title">{feature[1]}</div>
                <p class="feature-text">{feature[2]}</p>
                </div>
                """,
          unsafe_allow_html=True,
      )
      st.write("")

  st.subheader("🤖 How Our Agentic AI Works")

  st.markdown(
      """
        <div class="agent-box">

        <h3>🔄 Personalized Learning Loop</h3>

        <p>
        Student Input
        ➜ AI Analysis
        ➜ Content Generation
        ➜ Quiz
        ➜ Performance Analysis
        ➜ Weak Topic Detection
        ➜ AI Decision
        ➜ Next Learning Task
        </p>

        <strong>
        StudyMate AI doesn't only generate content —
        it decides what the student should do next.
        </strong>

        </div>
        """,
      unsafe_allow_html=True,
  )

  st.write("")
  st.info(
      "💡 Hackathon Highlight: StudyMate AI combines "
      "Generative AI for content creation with Agentic AI "
      "for personalized learning decisions."
  )


# ============================================================
# STUDY TOOLS
# ============================================================

elif page == "📚 Study Tools":

  st.title("📚 AI Study Tools")

  tool = st.selectbox(
      "Choose your tool",
      ["📝 Notes Summarizer", "🎯 MCQ Generator", "❓ Doubt Solver"],
  )

  # --------------------------------------------------------
  # SUMMARIZER
  # --------------------------------------------------------

  if tool == "📝 Notes Summarizer":

    st.subheader("📝 AI Notes Summarizer")

    notes = st.text_area(
        "Paste your notes",
        height=250,
        placeholder="Paste your chapter notes here...",
    )

    style = st.selectbox(
        "Summary style",
        ["Simple English", "Very Easy English", "English + Roman Urdu"],
    )

    if st.button("✨ Generate Summary", use_container_width=True):
      if not notes.strip():
        st.error("Please enter your notes.")
      else:
        with st.spinner("🤖 AI is summarizing your notes..."):
          prompt = f"""
Summarize the following study notes.

Style:
{style}

Include:
1. Short Summary
2. Important Points
3. Key Terms
4. Easy Explanation
5. Example if useful

Notes:
{notes}
"""
          result = ask_ai(prompt)

        if result.startswith("ERROR"):
          st.error(result)
        else:
          st.success("✅ Summary generated!")
          st.markdown(result)

          audio = create_audio(result)
          if audio:
            st.audio(audio, format="audio/mp3")

  # --------------------------------------------------------
  # MCQ GENERATOR
  # --------------------------------------------------------

  elif tool == "🎯 MCQ Generator":

    st.subheader("🎯 AI MCQ Generator")

    topic = st.text_input(
        "Enter topic",
        placeholder="Example: Vectors, Photosynthesis, Financial Accounting...",
    )
    number = st.slider("Number of MCQs", 3, 10, 5)

    if st.button("🎯 Generate MCQs", use_container_width=True):
      if not topic.strip():
        st.error("Please enter a topic.")
      else:
        with st.spinner("🤖 Creating MCQs..."):
          prompt = f"""
Create exactly {number} MCQs suitable for a student studying this topic.

Topic:
{topic}

Return ONLY valid JSON.

Format:
[
 {{
  "question": "Question",
  "options": [
   "Option A",
   "Option B",
   "Option C",
   "Option D"
  ],
  "answer": "Correct option",
  "explanation": "Short explanation"
 }}
]
"""
          result = ask_ai(prompt)

        data = extract_json(result)

        if data:
          st.session_state.mcqs = data
          for i, q in enumerate(data):
            st.markdown(f"### Q{i+1}. {q['question']}")
            for option in q["options"]:
              st.write(f"◯ {option}")
            with st.expander("💡 Show Answer"):
              st.success(f"Correct: {q['answer']}")
              st.write(q["explanation"])
        else:
          st.error("Could not read the AI response. Please try again.")

  # --------------------------------------------------------
  # DOUBT SOLVER
  # --------------------------------------------------------

  else:

    st.subheader("❓ AI Doubt Solver")

    subject = st.text_input(
        "Subject", placeholder="Example: Physics, History, Programming..."
    )
    question = st.text_area(
        "Ask your question",
        height=180,
        placeholder="What do you want to understand?",
    )
    level = st.selectbox(
        "Explanation level",
        ["Beginner / Basic", "Intermediate", "Detailed / Advanced"],
    )

    if st.button("🤖 Solve My Doubt", use_container_width=True):
      if not question.strip():
        st.error("Please enter your question.")
      else:
        with st.spinner("🤖 StudyMate is thinking..."):
          prompt = f"""
Subject:
{subject}

Student level:
{level}

Question:
{question}

Explain the answer clearly and step-by-step.
Use simple student-friendly language.
"""
          result = ask_ai(prompt)

        if result.startswith("ERROR"):
          st.error(result)
        else:
          st.success("💡 Here's your explanation:")
          st.markdown(result)

          audio = create_audio(result)
          if audio:
            st.audio(audio, format="audio/mp3")


# ============================================================
# QUIZ
# ============================================================

elif page == "🎯 Quiz":

  st.title("🎯 Interactive AI Quiz")

  st.markdown(
      "Test your knowledge and let StudyMate AI analyze your performance."
  )

  topic = st.text_input(
      "Quiz Topic",
      placeholder="Example: Newton's Laws, Organic Chemistry, World War II...",
  )
  number = st.slider("Number of Questions", 3, 10, 5)

  if st.button("🚀 Generate Quiz", use_container_width=True):
    if not topic.strip():
      st.error("Please enter a topic.")
    else:
      with st.spinner("🤖 Creating your personalized quiz..."):
        prompt = f"""
Create exactly {number} MCQs for a student.

Topic:
{topic}

Return ONLY JSON:
[
 {{
  "question": "...",
  "options": ["A", "B", "C", "D"],
  "answer": "exact correct option",
  "explanation": "short explanation"
 }}
]
"""
        result = ask_ai(prompt)

      quiz = extract_json(result)

      if quiz:
        st.session_state.quiz_data = quiz
        st.session_state.quiz_topic = topic
        st.session_state.last_topic = topic
        st.session_state.quiz_submitted = False
        st.rerun()
      else:
        st.error("Quiz generation failed. Try again.")

  if st.session_state.quiz_data:
    st.divider()
    st.subheader(f"📝 {st.session_state.quiz_topic} Quiz")

    answers = {}
    for i, q in enumerate(st.session_state.quiz_data):
      st.markdown(f"### Question {i+1}")
      st.write(q["question"])
      answers[i] = st.radio("Select answer:", q["options"], key=f"answer_{i}")

    if st.button("📊 Submit Quiz", use_container_width=True):
      score = 0
      for i, q in enumerate(st.session_state.quiz_data):
        if answers[i] == q["answer"]:
          score += 1

      total = len(st.session_state.quiz_data)
      percentage = (score / total) * 100

      st.session_state.last_score = percentage
      st.session_state.progress.append({
          "topic": st.session_state.quiz_topic,
          "score": score,
          "total": total,
          "percentage": percentage,
      })

      st.divider()
      st.subheader("🏆 Your Result")

      c1, c2, c3 = st.columns(3)
      c1.metric("Score", f"{score}/{total}")
      c2.metric("Percentage", f"{percentage:.0f}%")

      if percentage >= 80:
        performance = "Excellent 🎉"
      elif percentage >= 60:
        performance = "Good 👍"
      else:
        performance = "Needs Practice 📚"

      c3.metric("Performance", performance)

      # Agentic decision
      if percentage < 60:
        recommendation = (
            "Revise this topic and take an easier targeted quiz."
        )
      elif percentage < 80:
        recommendation = (
            "Review your mistakes and take another practice quiz."
        )
      else:
        recommendation = (
            "Try advanced questions or move to the next topic."
        )

      st.session_state.recommendation = recommendation

      st.markdown(
          f"""
                <div class="agent-box">
                <h3>🤖 AI Learning Decision</h3>
                <p>{recommendation}</p>
                </div>
                """,
          unsafe_allow_html=True,
      )


# ============================================================
# AI STUDY COACH
# ============================================================

elif page == "🤖 AI Study Coach":

  st.title("🤖 AI Study Coach")

  if st.session_state.last_score is None:
    st.info("🎯 Take a quiz first to activate your AI Study Coach.")
  else:
    score = st.session_state.last_score
    topic = st.session_state.last_topic

    st.subheader(f"📚 Topic: {topic}")
    st.metric("Latest Performance", f"{score:.0f}%")

    if score < 60:
      st.error("⚠️ Weak area detected")
      recommendation = """
            1. Revise the topic.
            2. Review important concepts.
            3. Practice basic questions.
            4. Take another targeted quiz.
            """
    elif score < 80:
      st.warning("📚 More practice recommended")
      recommendation = """
            1. Review mistakes.
            2. Practice medium-level questions.
            3. Take another quiz.
            """
    else:
      st.success("🎉 Strong performance!")
      recommendation = """
            1. Try advanced questions.
            2. Move to the next topic.
            3. Take an adaptive quiz.
            """

    st.subheader("🎯 Personalized Recommendation")
    st.markdown(recommendation)

    st.markdown(
        """
            <div class="agent-box">

            <h3>🧠 Agentic AI Decision Process</h3>

            <p>
            Quiz Result
            ➜ Analyze Performance
            ➜ Detect Learning Level
            ➜ Select Next Task
            ➜ Recommend Action
            </p>

            </div>
            """,
        unsafe_allow_html=True,
    )


# ============================================================
# STUDY PLANNER
# ============================================================

elif page == "📅 Study Planner":

  st.title("📅 AI Study Planner")

  subject = st.text_input(
      "Subject", placeholder="Example: Mathematics, Computer Science..."
  )
  topics = st.text_area(
      "Topics", placeholder="Vectors\nComplex Numbers\nMatrices"
  )
  exam_date = st.date_input("Exam Date", min_value=date.today())
  hours = st.slider("Study Hours Per Day", 1, 10, 2)

  if st.button("📅 Create Study Plan", use_container_width=True):
    if not subject or not topics:
      st.error("Please enter subject and topics.")
    else:
      days = (exam_date - date.today()).days

      with st.spinner("🤖 Creating your personalized plan..."):
        prompt = f"""
Create a personalized study plan for a student.

Subject:
{subject}

Topics:
{topics}

Days remaining:
{days}

Study hours per day:
{hours}

Include:
- Day
- Topic
- Study activity
- Practice
- Revision

Keep it realistic and well-structured.
"""
        result = ask_ai(prompt)

      if result.startswith("ERROR"):
        st.error(result)
      else:
        st.success("✅ Your study plan is ready!")
        st.markdown(result)


# ============================================================
# PROGRESS TRACKER
# ============================================================

elif page == "📈 Progress Tracker":

  st.title("📈 Progress Tracker")

  if not st.session_state.progress:
    st.info("No quiz data yet. Take your first quiz!")
  else:
    total = len(st.session_state.progress)
    average = (
        sum(item["percentage"] for item in st.session_state.progress) / total
    )
    best = max(item["percentage"] for item in st.session_state.progress)

    c1, c2, c3 = st.columns(3)
    c1.metric("🎯 Quizzes", total)
    c2.metric("📊 Average", f"{average:.0f}%")
    c3.metric("🏆 Best", f"{best:.0f}%")

    st.divider()
    st.subheader("📚 Quiz History")

    for i, item in enumerate(st.session_state.progress):
      st.write(
          f"**{i+1}. {item['topic']}** — "
          f"{item['score']}/{item['total']} "
          f"({item['percentage']:.0f}%)"
      )

    st.divider()

    if average >= 80:
      st.success("🎉 Excellent progress!")
    elif average >= 60:
      st.info("👍 Good progress! Keep practicing.")
    else:
      st.warning("📚 More revision is recommended.")


# ============================================================
# ADAPTIVE LEARNING
# ============================================================

elif page == "🧠 Adaptive Learning":

  st.title("🧠 Adaptive Learning")

  st.write(
      "StudyMate AI adjusts the next activity according to your performance."
  )

  if st.session_state.last_score is None:
    st.info("Take a quiz first to activate adaptive learning.")
  else:
    score = st.session_state.last_score
    topic = st.session_state.last_topic

    st.metric("Current Score", f"{score:.0f}%")

    if score < 50:
      level = "🔴 Needs Revision"
      action = "Easy revision + basic questions"
    elif score < 70:
      level = "🟠 Needs Practice"
      action = "Medium-level practice quiz"
    elif score < 85:
      level = "🟡 Good Understanding"
      action = "Mixed practice questions"
    else:
      level = "🟢 Strong Understanding"
      action = "Advanced quiz / next topic"

    st.subheader(f"{topic}: {level}")

    st.markdown(
        f"""
            <div class="agent-box">

            <h3>🤖 AI Selected Next Activity</h3>

            <h2>{action}</h2>

            <p>
            This recommendation was selected
            according to the student's quiz performance.
            </p>

            </div>
            """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.subheader("🔄 Adaptive Learning Loop")

    st.markdown(
        """
            ### 1️⃣ Take Quiz
            ↓
            ### 2️⃣ Analyze Performance
            ↓
            ### 3️⃣ Detect Learning Level
            ↓
            ### 4️⃣ Choose Next Activity
            ↓
            ### 5️⃣ Practice Again
            """
    )

    st.success(
        "🧠 This demonstrates the Agentic AI "
        "decision-making component of StudyMate AI."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; padding:15px;">

    <h3>📚 StudyMate AI</h3>

    <p>
    Your AI Study Partner — Learn Smarter, Not Harder.
    </p>

    <p>
    🚀 Generative AI + Agentic AI
    </p>

    </div>
    """,
    unsafe_allow_html=True,
)