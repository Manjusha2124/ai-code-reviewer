import streamlit as st
import textwrap
from datetime import datetime
import re

# =========================
# Page Configuration
# =========================
st.set_page_config(
    page_title="Code Reviewer AI",
    page_icon="💻",
    layout="wide"
)

# =========================
# Custom CSS
# =========================
st.markdown("""
<style>

body {
    background: radial-gradient(circle at top left, rgba(0, 255, 170, 0.18), transparent 25%),
                radial-gradient(circle at bottom right, rgba(255, 255, 255, 0.08), transparent 20%),
                linear-gradient(135deg, #07111d 0%, #0e1728 45%, #08111b 100%);
}

.stApp {
    background: transparent;
}

.main {
    background-color: rgba(14, 17, 23, 0.92);
    color: white;
}

.stTextArea textarea,
.stTextArea textarea:focus {
    background-color: #1E1E1E;
    color: white;
    font-size: 16px;
    border: 1px solid #2f4f4f;
}

h1, h2, h3 {
    color: #00FFAA;
}

.stButton>button {
    background-color: #00ff9d;
    color: #0f1720;
}

</style>
""", unsafe_allow_html=True)

# =========================
# App Title
# =========================
st.title("💻 AI Code Reviewer")
st.caption("Analyze, detect errors, and optimize your code instantly")

# =========================
# Sample Code Library
# =========================
sample_code = {
    "Python": {
        "Simple Function": """def greet(name):
    return f"Hello, {name}!"

print(greet('World'))"""
    },

    "Java": {
        "Simple Function": """public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}"""
    },

    "C++": {
        "Simple Function": """#include <iostream>

using namespace std;

int main() {
    cout << "Hello";
    return 0;
}"""
    },

    "JavaScript": {
        "Simple Function": """function greet(name) {
    return "Hello " + name;
}

console.log(greet("World"));"""
    }
}

language_map = {
    "Java": "java",
    "Python": "python",
    "C++": "cpp",
    "JavaScript": "javascript"
}

# =========================
# Error Detection
# =========================
def find_errors(code, language):

    errors = []

    lines = code.splitlines()

    # Java / C++ / JavaScript Errors
    if language in ["Java", "C++", "JavaScript"]:

        for i, line in enumerate(lines):

            stripped = line.strip()

            # Missing semicolon
            if (
                stripped
                and not stripped.endswith(";")
                and not stripped.endswith("{")
                and not stripped.endswith("}")
                and "if" not in stripped
                and "for" not in stripped
                and "while" not in stripped
                and "class " not in stripped
                and not stripped.startswith("//")
            ):
                errors.append(
                    f"Possible missing semicolon at line {i+1}"
                )

        # Bracket count
        if code.count("{") != code.count("}"):
            errors.append("Mismatched curly braces detected")

        if code.count("(") != code.count(")"):
            errors.append("Mismatched parentheses detected")

    # Python Errors
    elif language == "Python":

        try:
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            errors.append(f"Syntax Error at line {e.lineno}: {e.msg}")

    return errors

# =========================
# Complexity Analyzer
# =========================
def analyze_complexity(code: str, language: str) -> dict:

    lines = code.splitlines()

    loop_count = 0
    nested_loop = False
    recursion = False

    for line in lines:

        stripped = line.strip().lower()

        # Detect loops
        if (
            stripped.startswith("for ")
            or stripped.startswith("while ")
            or " for(" in stripped
            or " while(" in stripped
        ):
            loop_count += 1

        # Detect recursion
        if language == "Python":

            if "def " in stripped:

                func_name = stripped.split("def ")[1].split("(")[0]

                if func_name + "(" in code and code.count(func_name + "(") > 1:
                    recursion = True

        elif language in ["Java", "C++", "JavaScript"]:

            if "(" in stripped and ")" in stripped and "class " not in stripped:

                parts = stripped.split("(")[0].split()

                if len(parts) > 0:

                    func_name = parts[-1]

                    if code.count(func_name + "(") > 1:
                        recursion = True

    # Nested loops
    if loop_count >= 2:
        nested_loop = True

    # Time Complexity
    if recursion:
        time_complexity = "O(2^n)"
    elif nested_loop:
        time_complexity = "O(n²)"
    elif loop_count == 1:
        time_complexity = "O(n)"
    else:
        time_complexity = "O(1)"

    # Space Complexity
    if recursion:
        space_complexity = "O(n)"
    elif (
        "[]" in code
        or "ArrayList" in code
        or "vector" in code
        or "HashMap" in code
    ):
        space_complexity = "O(n)"
    else:
        space_complexity = "O(1)"

    return {
        "time": time_complexity,
        "space": space_complexity
    }

# =========================
# Detect Issues
# =========================
def detect_issues(code, language):

    lines = code.splitlines()

    metrics = {
        "lines": len(lines),
        "characters": len(code),
        "comments": sum(
            1 for line in lines
            if line.strip().startswith("#")
            or line.strip().startswith("//")
        )
    }

    issues = []

    if metrics["comments"] == 0:
        issues.append("No comments found.")

    if len(code) > 1000:
        issues.append("Large code block detected.")

    return issues, metrics

# =========================
# Score Calculation
# =========================
def calculate_score(metrics):

    score = 10

    if metrics["comments"] == 0:
        score -= 1

    return max(score, 1)

# =========================
# Build Review
# =========================
def build_review(language, difficulty, review_mode, metrics, issues):

    score = calculate_score(metrics)

    issue_text = "\n".join([f"- {i}" for i in issues])

    return f"""
## ✅ Review Summary

- Language: {language}
- Difficulty: {difficulty}
- Review Focus: {review_mode}

### 📊 Metrics
- Total Lines: {metrics['lines']}
- Characters: {metrics['characters']}
- Comments: {metrics['comments']}

### ⭐ Score
{score}/10

### 🔎 Issues
{issue_text if issue_text else "No issues detected"}

### 🚀 Overall Feedback
Your code review completed successfully.
"""

# =========================
# Sidebar
# =========================
st.sidebar.title("⚙ Settings")

language = st.sidebar.selectbox(
    "Programming Language",
    ["Java", "Python", "C++", "JavaScript"]
)

difficulty = st.sidebar.selectbox(
    "Code Level",
    ["Beginner", "Intermediate", "Advanced"]
)

review_mode = st.sidebar.selectbox(
    "Review Focus",
    ["Best Practices", "Style & Readability", "Performance", "Security"]
)

sample_options = ["None"] + list(sample_code[language].keys())

sample_choice = st.sidebar.selectbox(
    "Use Sample Code",
    sample_options
)

uploaded_file = st.sidebar.file_uploader(
    "Upload Code File",
    type=["py", "java", "cpp", "js", "txt"]
)

# =========================
# Main Input
# =========================
st.subheader("📌 Paste Your Code")

code = ""

if uploaded_file is not None:

    raw = uploaded_file.read()

    try:
        code = raw.decode("utf-8")
    except:
        code = str(raw)

elif sample_choice != "None":

    code = sample_code[language][sample_choice]

else:

    code = st.text_area(
        "Code",
        height=350,
        placeholder="Paste your code here..."
    )

# =========================
# Analyze Button
# =========================
if st.button("🔍 Review Code"):

    if not code.strip():

        st.warning("Please paste some code.")

    else:

        # Error Detection
        errors = find_errors(code, language)

        if errors:

            st.subheader("❌ Syntax Errors")

            for error in errors:
                st.error(error)

        # Review
        issues, metrics = detect_issues(code, language)

        review = build_review(
            language,
            difficulty,
            review_mode,
            metrics,
            issues
        )

        col1, col2 = st.columns((2, 3))

        # =========================
        # LEFT SIDE
        # =========================
        with col1:

            st.subheader("🧾 Original Code")

            st.code(
                code,
                language=language_map[language]
            )

            st.markdown("---")

            st.subheader("📊 Metrics")

            st.metric("Lines", metrics["lines"])
            st.metric("Characters", metrics["characters"])
            st.metric("Comments", metrics["comments"])

            # Complexity Analysis
            complexity = analyze_complexity(code, language)

            st.markdown("---")

            st.subheader("📊 Complexity Analysis")

            st.metric(
                "Time Complexity",
                complexity["time"]
            )

            st.metric(
                "Space Complexity",
                complexity["space"]
            )

        # =========================
        # RIGHT SIDE
        # =========================
        with col2:

            st.markdown(review)

            st.download_button(
                label="⬇ Download Report",
                data=review,
                file_name=f"review_{datetime.now():%Y%m%d_%H%M%S}.txt",
                mime="text/plain"
            )

            st.download_button(
                label="⬇ Download Code",
                data=code,
                file_name=f"code_{datetime.now():%Y%m%d_%H%M%S}.txt",
                mime="text/plain"
            )

# =========================
# Footer
# =========================
st.markdown("---")

st.caption(
    "Built with Streamlit 🚀 | AI Code Reviewer"
)
