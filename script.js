document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript Loaded");
});

function generateQuestion() {
    let company = document.getElementById("company").value;
    let role = document.getElementById("role").value;
    fetch("/ask_question", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ company: company, role: role })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("question").innerText = "Q: " + data.question;
        document.getElementById("question").classList.remove("hidden");
        speakText(data.question);
    })
    .catch(error => console.error("Error fetching question:", error));
}

function submitAnswer() {
    let userAnswer = document.getElementById("user-answer").value;
    let questionText = document.getElementById("question").innerText;
    fetch("/evaluate_answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: questionText, answer: userAnswer })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("correct-answer").innerText = "✅ Correct Answer: " + data.correct_answer;
        document.getElementById("correct-answer").classList.remove("hidden");
        document.getElementById("feedback").innerText = "📝 Feedback: " + data.feedback;
        document.getElementById("feedback").classList.remove("hidden");
    })
    .catch(error => console.error("Error evaluating answer:", error));
}

function speakText(text) {
    let speech = new SpeechSynthesisUtterance();
    speech.text = text;
    speech.volume = 1;
    speech.rate = 1;
    speech.pitch = 1;
    window.speechSynthesis.speak(speech);
}