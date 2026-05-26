import streamlit as st
import textwrap
from datetime import datetime

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
st.caption("Analyze and review your code instantly")

# =========================
# Sample Code Library
# =========================
sample_code = {
    "Python": {
        "Simple Function": """def greet(name):
    return f\"Hello, {name}!\"\n
print(greet('World'))""",
        "Loop Example": """numbers = [1, 2, 3, 4, 5]
squared = [n**2 for n in numbers]
print(squared)""",
        "Class Template": """class Calculator:
    def __init__(self):
        self.total = 0

    def add(self, value):
        self.total += value
        return self.total

calc = Calculator()
print(calc.add(10))"""
    },
    "Java": {
        "Simple Function": """public class HelloWorld {
    public static void main(String[] args) {
        System.out.println(\"Hello, World!\");
    }
}""",
        "Loop Example": """for (int i = 0; i < 5; i++) {
    System.out.println(i);
}""",
        "Class Template": """public class Calculator {
    private int total = 0;

    public int add(int value) {
        total += value;
        return total;
    }
}"""
    },
    "C++": {
        "Simple Function": """#include <iostream>

int main() {
    std::cout << \"Hello, C++!\" << std::endl;
    return 0;
}""",
        "Loop Example": """for (int i = 0; i < 5; i++) {
    std::cout << i << std::endl;
}""",
        "Class Template": """#include <iostream>

class Calculator {
public:
    int total = 0;

    int add(int value) {
        total += value;
        return total;
    }
};"""
    },
    "JavaScript": {
        "Simple Function": """function greet(name) {
    return `Hello, ${name}!`;
}

console.log(greet('World'));""",
        "Loop Example": """const numbers = [1, 2, 3, 4, 5];
const squared = numbers.map(n => n * n);
console.log(squared);""",
        "Class Template": """class Calculator {
    constructor() {
        this.total = 0;
    }

    add(value) {
        this.total += value;
        return this.total;
    }
}

const calc = new Calculator();
console.log(calc.add(10));"""
    }
}

language_map = {
    "Java": "java",
    "Python": "python",
    "C++": "cpp",
    "JavaScript": "javascript"
}

dangerous_patterns = {
    "Python": ["eval(", "exec(", "pickle.loads", "subprocess.Popen"],
    "Java": ["Runtime.getRuntime", "exec(", "System.exit"],
    "C++": ["strcpy(", "sprintf(", "gets(", "system("],
    "JavaScript": ["eval(", "document.write(", "innerHTML", "setTimeout("]
}

comment_tokens = {
    "Python": ["#"],
    "Java": ["//", "/*"],
    "C++": ["//", "/*"],
    "JavaScript": ["//", "/*"]
}

# =========================
# Helpers
# =========================
def count_comments(code: str, language: str) -> int:
    tokens = comment_tokens.get(language, ["#"])
    comments = 0
    for line in code.splitlines():
        if any(token in line.strip() for token in tokens):
            comments += 1
    return comments


def detect_issues(code: str, language: str) -> tuple[list[str], dict]:
    lines = code.splitlines()
    metrics = {
        "lines": len(lines),
        "characters": len(code),
        "comments": count_comments(code, language),
        "long_lines": sum(1 for line in lines if len(line) > 100),
        "todo_count": sum(line.lower().count("todo") + line.lower().count("fixme") for line in lines),
        "tabs": "\t" in code,
        "dangerous": any(pattern in code for pattern in dangerous_patterns.get(language, []))
    }

    issues = []
    if metrics["todo_count"]:
        issues.append(f"Found {metrics['todo_count']} TODO/FIXME comment(s).")
    if metrics["long_lines"]:
        issues.append(f"{metrics['long_lines']} line(s) exceed 100 characters.")
    if metrics["tabs"]:
        issues.append("Tab characters are used; prefer spaces for consistent indentation.")
    if metrics["dangerous"]:
        issues.append("Potentially unsafe function or pattern detected.")
    if metrics["comments"] == 0 and metrics["lines"] > 10:
        issues.append("No comments detected; add documentation for readability.")

    if language == "JavaScript" and "var " in code:
        issues.append("Use let/const instead of var for modern JavaScript.")
    if language == "Python" and "print(" in code and "def " in code and metrics["lines"] > 20:
        issues.append("Consider using logging instead of print for larger Python projects.")
    if language == "C++" and "using namespace std" in code:
        issues.append("Avoid 'using namespace std' in headers or shared code.")

    return issues, metrics


def calculate_score(metrics: dict, difficulty: str) -> int:
    score = 10
    score -= min(3, metrics["todo_count"])
    score -= min(2, metrics["long_lines"] / 5)
    score -= 1 if metrics["tabs"] else 0
    score -= 2 if metrics["dangerous"] else 0

    comment_ratio = metrics["comments"] / max(metrics["lines"], 1)
    if metrics["lines"] > 15 and comment_ratio < 0.08:
        score -= 1

    score = max(3, min(10, round(score)))
    return score


def get_quality_label(score: int) -> str:
    if score >= 9:
        return "Excellent"
    if score >= 7:
        return "Good"
    if score >= 5:
        return "Average"
    return "Needs Improvement"


def build_review(language: str, difficulty: str, review_mode: str, metrics: dict, issues: list[str]) -> str:
    score = calculate_score(metrics, difficulty)
    label = get_quality_label(score)

    improvements = [
        "Use meaningful variable and function names",
        "Keep functions small and focused",
        "Add comments or docstrings where helpful",
        "Refactor repeated code into reusable helpers",
    ]

    if review_mode == "Performance":
        improvements.append("Check for expensive loops and repeated calculations.")
    elif review_mode == "Security":
        improvements.append("Validate user input and sanitize external data.")
    elif review_mode == "Style & Readability":
        improvements.append("Use consistent spacing and naming conventions.")

    suggestions = "\n".join(f"- {item}" for item in improvements)
    issue_section = "\n".join(f"- {issue}" for issue in issues) if issues else "No major issues detected."

    return f"""
### ✅ AI Code Review Report

- Language Selected: {language}
- Difficulty Level: {difficulty}
- Review Focus: {review_mode}
- Quality Label: **{label}**

### 📊 Metrics
- Total Lines: {metrics['lines']}
- Total Characters: {metrics['characters']}
- Commented Lines: {metrics['comments']}
- Long Lines: {metrics['long_lines']}
- TODO/FIXME Count: {metrics['todo_count']}

### ⭐ Code Quality Score
{score}/10

### 🔎 Detected Issues
{issue_section}

### 🛠 Recommendations
{suggestions}

### 🚀 Overall Feedback
This review gives you a quick snapshot of maintainability, readability, and style. Use the detailed issues above to improve your code before the next review.
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
sample_choice = st.sidebar.selectbox("Use Sample Code", sample_options)

uploaded_file = st.sidebar.file_uploader(
    "Upload Code File",
    type=["py", "java", "cpp", "js", "txt"]
)

verbose = st.sidebar.checkbox("Verbose Analysis", value=False)

# =========================
# Main Input
# =========================
st.subheader("📌 Paste Your Code")

code = ""
source_note = ""

if uploaded_file is not None:
    raw = uploaded_file.read()
    try:
        code = raw.decode("utf-8")
    except AttributeError:
        code = raw
    except UnicodeDecodeError:
        code = raw.decode("utf-8", errors="replace")
    source_note = f"Analyzing uploaded file: **{uploaded_file.name}**"
elif sample_choice != "None":
    code = sample_code[language][sample_choice]
    source_note = f"Loaded sample: **{sample_choice}**"
else:
    code = st.text_area(
        "Enter Code Here",
        height=320,
        placeholder="Paste your code here..."
    )

if source_note:
    st.write(source_note)

# =========================
# Analyze Button
# =========================
if st.button("🔍 Review Code"):
    if not code or not code.strip():
        st.warning("Please paste some code or upload a file first.")
    else:
        issues, metrics = detect_issues(code, language)
        review = build_review(language, difficulty, review_mode, metrics, issues)

        col1, col2 = st.columns((2, 3))

        with col1:
            st.subheader("🧾 Code Preview")
            st.code(code, language=language_map[language])
            st.markdown("---")
            st.subheader("📌 Quick Metrics")
            st.metric("Lines", metrics["lines"])
            st.metric("Characters", metrics["characters"])
            st.metric("Comments", metrics["comments"])

        with col2:
            st.subheader("✅ Review Summary")
            st.markdown(review)

            if verbose and issues:
                with st.expander("Detailed Issues"):
                    for issue in issues:
                        st.write(f"- {issue}")

            st.download_button(
                label="⬇ Download Full Report",
                data=review,
                file_name=f"code_review_report_{datetime.now():%Y%m%d_%H%M%S}.md",
                mime="text/markdown"
            )

            st.download_button(
                label="⬇ Download Code",
                data=code,
                file_name=f"code_snippet_{datetime.now():%Y%m%d_%H%M%S}.{uploaded_file.name.split('.')[-1] if uploaded_file is not None else language_map[language]}",
                mime="text/plain"
            )

        if verbose:
            with st.expander("⚙️ Analysis Details"):
                st.json(metrics)

# =========================
# Footer
# =========================
st.markdown("---")
st.caption("Built with Streamlit 🚀 | Enhanced with sample code, file upload, and richer analysis.")
