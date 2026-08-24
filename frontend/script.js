const chatInput = document.getElementById("chatInput");
const summarizeBtn = document.getElementById("summarizeBtn");
const clearBtn = document.getElementById("clearBtn");
const copyBtn = document.getElementById("copyBtn");
const downloadBtn = document.getElementById("downloadBtn");
const summaryBox = document.getElementById("summaryBox");

const wordCount = document.getElementById("wordCount");
const charCount = document.getElementById("charCount");
const messageCount = document.getElementById("messageCount");

const fileInput = document.getElementById("fileInput");
const fileName = document.getElementById("fileName");

const themeToggle = document.getElementById("themeToggle");

const historyList = document.getElementById("historyList");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");

const summaryTitle = document.getElementById("summaryTitle");

const originalWords = document.getElementById("originalWords");
const summaryWords = document.getElementById("summaryWords");
const reductionPercent = document.getElementById("reductionPercent");
const analyticsMessages = document.getElementById("analyticsMessages");


let currentSummary = "";
let currentTitle = "";


/* ==========================================
   WORD COUNT
========================================== */

function countWords(text) {

    if (!text || !text.trim()) {
        return 0;
    }

    return text.trim().split(/\s+/).length;
}


/* ==========================================
   MESSAGE COUNT
========================================== */

function countMessages(text) {

    if (!text || !text.trim()) {
        return 0;
    }

    return text
        .split(/\n+/)
        .filter(line => line.trim().length > 0)
        .length;
}


/* ==========================================
   UPDATE INPUT STATISTICS
========================================== */

function updateStatistics() {

    const text = chatInput.value;

    wordCount.textContent = countWords(text);

    charCount.textContent = text.length;

    messageCount.textContent = countMessages(text);
}


chatInput.addEventListener(
    "input",
    updateStatistics
);


/* ==========================================
   CREATE TITLE
========================================== */

function createTitle(text) {

    const cleaned = text
        .replace(/\s+/g, " ")
        .trim();

    if (!cleaned) {
        return "Conversation Summary";
    }

    let title = cleaned.split(/[.!?]/)[0];

    if (title.length > 50) {
        title = title.substring(0, 50).trim() + "...";
    }

    return title || "Conversation Summary";
}


/* ==========================================
   FILE UPLOAD
========================================== */

fileInput.addEventListener(
    "change",
    function () {

        const file = fileInput.files[0];

        if (!file) {
            return;
        }

        if (
            !file.name
                .toLowerCase()
                .endsWith(".txt")
        ) {

            alert(
                "Please select a TXT file."
            );

            fileInput.value = "";

            fileName.textContent =
                "No file selected";

            return;
        }


        fileName.textContent = file.name;


        const reader = new FileReader();


        reader.onload = function (event) {

            chatInput.value =
                event.target.result;

            updateStatistics();

            resetSummary();

        };


        reader.readAsText(file);

    }
);


/* ==========================================
   RESET SUMMARY
========================================== */

function resetSummary() {

    currentSummary = "";

    currentTitle = "";


    summaryTitle.textContent =
        "No summary generated yet";


    summaryBox.innerHTML = `
        <p class="placeholder">
            Your AI-generated summary
            will appear here...
        </p>
    `;


    copyBtn.disabled = true;

    downloadBtn.disabled = true;


    originalWords.textContent = "0";

    summaryWords.textContent = "0";

    reductionPercent.textContent = "0%";

    analyticsMessages.textContent = "0";
}


/* ==========================================
   SUMMARIZE
========================================== */

summarizeBtn.addEventListener(
    "click",
    async function () {

        const text =
            chatInput.value.trim();


        if (!text) {

            alert(
                "Please enter a conversation first."
            );

            return;
        }


        summarizeBtn.disabled = true;

        summarizeBtn.textContent =
            "⏳ Summarizing...";


        summaryBox.innerHTML = `
            <p class="placeholder">
                🧠 AI is analyzing
                your conversation...
            </p>
        `;


        try {

            const response =
                await fetch(
                    "http://127.0.0.1:8000/summarize",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                text: text
                            })
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "Server error: " +
                    response.status
                );
            }


            const data =
                await response.json();


            currentSummary =
                data.summary || "";


            currentTitle =
                createTitle(text);


            /* Show AI summary */

            summaryTitle.textContent =
                currentTitle;


            summaryBox.innerHTML = `
                <p>
                    ${escapeHTML(
                        currentSummary
                    )}
                </p>
            `;


            /* Enable buttons */

            copyBtn.disabled = false;

            downloadBtn.disabled = false;


            /* Analytics */

            updateAnalytics(
                text,
                currentSummary
            );


            /* Save history */

            saveToHistory(
                text,
                currentSummary,
                currentTitle
            );


            /* Refresh history */

            displayHistory();


        } catch (error) {

            console.error(error);


            summaryBox.innerHTML = `
                <p class="placeholder">

                    ❌ Unable to connect
                    to the AI backend.

                    <br><br>

                    Please make sure
                    FastAPI is running.

                </p>
            `;


        } finally {

            summarizeBtn.disabled = false;

            summarizeBtn.textContent =
                "✨ Summarize Chat";

        }

    }
);


/* ==========================================
   ANALYTICS
========================================== */

function updateAnalytics(
    originalText,
    summaryText
) {

    const original =
        countWords(originalText);

    const summary =
        countWords(summaryText);


    let reduction = 0;


    if (original > 0) {

        reduction =
            ((original - summary)
                / original) * 100;
    }


    reduction =
        Math.max(0, reduction);


    originalWords.textContent =
        original;

    summaryWords.textContent =
        summary;

    reductionPercent.textContent =
        Math.round(reduction) + "%";

    analyticsMessages.textContent =
        countMessages(originalText);
}


/* ==========================================
   COPY BUTTON
========================================== */

copyBtn.addEventListener(
    "click",
    async function () {

        if (!currentSummary) {

            return;
        }


        try {

            await navigator.clipboard.writeText(
                currentSummary
            );


            copyBtn.textContent =
                "✅ Copied!";


            setTimeout(
                function () {

                    copyBtn.textContent =
                        "📋 Copy";

                },
                2000
            );


        } catch (error) {

            console.error(
                "Copy failed:",
                error
            );


            /*
               Backup copy method
            */

            const temp =
                document.createElement(
                    "textarea"
                );

            temp.value =
                currentSummary;

            document.body.appendChild(
                temp
            );

            temp.select();

            document.execCommand(
                "copy"
            );

            document.body.removeChild(
                temp
            );


            copyBtn.textContent =
                "✅ Copied!";


            setTimeout(
                function () {

                    copyBtn.textContent =
                        "📋 Copy";

                },
                2000
            );

        }

    }
);


/* ==========================================
   DOWNLOAD BUTTON
========================================== */

downloadBtn.addEventListener(
    "click",
    function () {

        if (!currentSummary) {

            return;
        }


        const content =
            currentTitle +
            "\n\n" +
            currentSummary;


        const blob =
            new Blob(
                [content],
                {
                    type:
                        "text/plain"
                }
            );


        const url =
            URL.createObjectURL(blob);


        const link =
            document.createElement("a");


        link.href = url;

        link.download =
            "SynaptiChat_Summary.txt";


        document.body.appendChild(
            link
        );


        link.click();


        document.body.removeChild(
            link
        );


        URL.revokeObjectURL(url);


        downloadBtn.textContent =
            "✅ Downloaded!";


        setTimeout(
            function () {

                downloadBtn.textContent =
                    "💾 Download";

            },
            2000
        );

    }
);


/* ==========================================
   CLEAR CURRENT CHAT
========================================== */

clearBtn.addEventListener(
    "click",
    function () {

        chatInput.value = "";

        fileInput.value = "";

        fileName.textContent =
            "No file selected";


        updateStatistics();

        resetSummary();

    }
);


/* ==========================================
   HISTORY STORAGE
========================================== */

function getHistory() {

    const saved =
        localStorage.getItem(
            "synaptichat-history"
        );


    if (!saved) {

        return [];
    }


    try {

        return JSON.parse(saved);

    } catch {

        return [];
    }
}


/* ==========================================
   SAVE HISTORY
========================================== */

function saveToHistory(
    originalText,
    summary,
    title
) {

    const history =
        getHistory();


    const item = {

        id: Date.now(),

        title: title,

        original: originalText,

        summary: summary,

        date:
            new Date().toLocaleString()

    };


    history.unshift(item);


    localStorage.setItem(
        "synaptichat-history",
        JSON.stringify(
            history.slice(0, 20)
        )
    );
}


/* ==========================================
   DISPLAY HISTORY
========================================== */

function displayHistory() {

    const history =
        getHistory();


    if (!history.length) {

        historyList.innerHTML = `
            <p class="history-empty">

                No summaries yet.

                <br><br>

                Your summaries will
                appear here.

            </p>
        `;

        return;
    }


    historyList.innerHTML = "";


    history.forEach(
        function (item) {

            const historyItem =
                document.createElement("div");


            historyItem.className =
                "history-item";


            historyItem.innerHTML = `
                <div
                    class="history-item-title"
                >
                    📝
                    ${escapeHTML(item.title)}
                </div>

                <div
                    class="history-item-date"
                >
                    ${escapeHTML(item.date)}
                </div>
            `;


            historyItem.addEventListener(
                "click",
                function () {

                    loadHistoryItem(item);

                }
            );


            historyList.appendChild(
                historyItem
            );

        }
    );
}


/* ==========================================
   LOAD HISTORY
========================================== */

function loadHistoryItem(item) {

    /*
       Original conversation goes
       ONLY into the input box.
    */

    chatInput.value =
        item.original;


    /*
       Saved AI summary goes
       ONLY into summary box.
    */

    currentSummary =
        item.summary;


    currentTitle =
        item.title;


    summaryTitle.textContent =
        item.title;


    summaryBox.innerHTML = `
        <p>
            ${escapeHTML(
                item.summary
            )}
        </p>
    `;


    copyBtn.disabled = false;

    downloadBtn.disabled = false;


    updateStatistics();


    updateAnalytics(
        item.original,
        item.summary
    );

}


/* ==========================================
   CLEAR ALL HISTORY
========================================== */

clearHistoryBtn.addEventListener(
    "click",
    function () {

        const history =
            getHistory();


        if (!history.length) {

            alert(
                "There is no history to clear."
            );

            return;
        }


        const confirmed =
            confirm(
                "Delete all saved summaries?"
            );


        if (!confirmed) {

            return;
        }


        localStorage.removeItem(
            "synaptichat-history"
        );


        displayHistory();


        resetSummary();

    }
);


/* ==========================================
   ESCAPE HTML
========================================== */

function escapeHTML(text) {

    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/* ==========================================
   DARK MODE
========================================== */

const savedTheme =
    localStorage.getItem(
        "smartchat-theme"
    );


if (savedTheme === "dark") {

    document.body.classList.add(
        "dark-mode"
    );

    themeToggle.textContent = "☀️";
}


themeToggle.addEventListener(
    "click",
    function () {

        document.body.classList.toggle(
            "dark-mode"
        );


        const isDark =
            document.body.classList.contains(
                "dark-mode"
            );


        if (isDark) {

            themeToggle.textContent =
                "☀️";

            localStorage.setItem(
                "smartchat-theme",
                "dark"
            );

        } else {

            themeToggle.textContent =
                "🌙";

            localStorage.setItem(
                "smartchat-theme",
                "light"
            );
        }

    }
);


/* ==========================================
   START
========================================== */

updateStatistics();

displayHistory();