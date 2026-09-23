/* ============================================================
   SYNAPTICHAT - AI CHAT SUMMARIZER
   ============================================================ */


/* ============================================================
   AUTHENTICATION PROTECTION
   ============================================================ */

const loggedIn =
    localStorage.getItem("synaptichat_logged_in");

if (loggedIn !== "true") {
    window.location.href = "login.html";
}


/* ============================================================
   DOM ELEMENTS
   ============================================================ */

const chatInput =
    document.getElementById("chatInput");

const summarizeBtn =
    document.getElementById("summarizeBtn");

const clearBtn =
    document.getElementById("clearBtn");

const copyBtn =
    document.getElementById("copyBtn");

const downloadBtn =
    document.getElementById("downloadBtn");

const summaryBox =
    document.getElementById("summaryBox");

const wordCount =
    document.getElementById("wordCount");

const charCount =
    document.getElementById("charCount");

const messageCount =
    document.getElementById("messageCount");

const fileInput =
    document.getElementById("fileInput");

const fileName =
    document.getElementById("fileName");

const themeToggle =
    document.getElementById("themeToggle");

const historyList =
    document.getElementById("historyList");

const clearHistoryBtn =
    document.getElementById("clearHistoryBtn");

const summaryTitle =
    document.getElementById("summaryTitle");

const originalWords =
    document.getElementById("originalWords");

const summaryWords =
    document.getElementById("summaryWords");

const reductionPercent =
    document.getElementById("reductionPercent");

const analyticsMessages =
    document.getElementById("analyticsMessages");


/* ============================================================
   GLOBAL STATE
   ============================================================ */

let currentSummary = "";
let currentTitle = "";


/* ============================================================
   WORD COUNT
   ============================================================ */

function countWords(text) {

    if (!text || !text.trim()) {
        return 0;
    }

    return text
        .trim()
        .split(/\s+/)
        .length;
}


/* ============================================================
   MESSAGE COUNT
   ============================================================ */

function countMessages(text) {

    if (!text || !text.trim()) {
        return 0;
    }

    return text
        .split(/\n+/)
        .filter(line => line.trim().length > 0)
        .length;
}


/* ============================================================
   UPDATE STATISTICS
   ============================================================ */

function updateStatistics() {

    const text =
        chatInput.value;

    wordCount.textContent =
        countWords(text);

    charCount.textContent =
        text.length;

    messageCount.textContent =
        countMessages(text);
}


chatInput.addEventListener(
    "input",
    updateStatistics
);


/* ============================================================
   CREATE SUMMARY TITLE
   ============================================================ */

function createTitle(text) {

    const cleaned =
        text
            .replace(/\s+/g, " ")
            .trim();

    if (!cleaned) {
        return "Conversation Summary";
    }

    let title =
        cleaned.split(/[.!?]/)[0];

    if (title.length > 55) {

        title =
            title.substring(0, 55).trim()
            + "...";
    }

    return title ||
        "Conversation Summary";
}


/* ============================================================
   FILE UPLOAD
   ============================================================ */

fileInput.addEventListener(
    "change",
    function () {

        const file =
            fileInput.files[0];

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

        fileName.textContent =
            file.name;

        const reader =
            new FileReader();

        reader.onload =
            function (event) {

                chatInput.value =
                    event.target.result;

                updateStatistics();

                resetSummary();
            };

        reader.readAsText(file);
    }
);


/* ============================================================
   RESET SUMMARY
   ============================================================ */

function resetSummary() {

    currentSummary = "";
    currentTitle = "";

    summaryTitle.textContent =
        "No summary generated yet";

    summaryBox.innerHTML = `
        <div class="placeholder">

            <div class="placeholder-icon">
                🧠
            </div>

            <h3>
                Your AI summary will appear here
            </h3>

            <p>
                Enter a conversation and let
                SynaptiChat analyze the important
                information for you.
            </p>

        </div>
    `;

    copyBtn.disabled = true;
    downloadBtn.disabled = true;

    originalWords.textContent = "0";
    summaryWords.textContent = "0";
    reductionPercent.textContent = "0%";
    analyticsMessages.textContent = "0";
}


/* ============================================================
   SUMMARIZE CHAT
   ============================================================ */

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


        /* ----------------------------------------
           Loading state
           ---------------------------------------- */

        summarizeBtn.disabled = true;

        summarizeBtn.innerHTML =
            "⏳ Analyzing conversation...";

        summaryBox.innerHTML = `
            <div class="ai-loading">

                <div class="loading-spinner"></div>

                <h3>
                    SynaptiChat AI is working
                </h3>

                <p>
                    Analyzing messages and extracting
                    the most important information...
                </p>

            </div>
        `;


        try {

            /* ----------------------------------------
               SEND CHAT TO BACKEND
               ---------------------------------------- */

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


            /* ----------------------------------------
               SERVER ERROR
               ---------------------------------------- */

            if (!response.ok) {

                throw new Error(
                    "Backend returned HTTP " +
                    response.status
                );
            }


            /* ----------------------------------------
               READ AI RESPONSE
               ---------------------------------------- */

            const data =
                await response.json();


            if (
                !data.summary ||
                !data.summary.trim()
            ) {

                throw new Error(
                    "AI returned an empty summary."
                );
            }


            /* ----------------------------------------
               SAVE MAIN SUMMARY
               ---------------------------------------- */

            currentSummary =
                data.summary.trim();

            currentTitle =
                createTitle(text);


            /* ----------------------------------------
               GET STRUCTURED RESULTS
               ---------------------------------------- */

            const actions =
                Array.isArray(data.actions)
                    ? data.actions
                    : [];

            const deadlines =
                Array.isArray(data.deadlines)
                    ? data.deadlines
                    : [];


            /* ----------------------------------------
               DISPLAY TITLE
               ---------------------------------------- */

            summaryTitle.textContent =
                currentTitle;


            /* ----------------------------------------
               BUILD RESULT UI
               ---------------------------------------- */

            let resultHTML = `

                <div class="ai-result">


                    <!-- SUMMARY -->

                    <section class="result-section">

                        <h3 class="result-heading">
                            📝 SUMMARY
                        </h3>

                        <p class="generated-summary">
                            ${escapeHTML(
                                currentSummary
                            )}
                        </p>

                    </section>

            `;


            /* ----------------------------------------
               KEY ACTIONS
               ---------------------------------------- */

            if (actions.length > 0) {

                resultHTML += `

                    <section class="result-section">

                        <h3 class="result-heading">
                            🎯 KEY ACTIONS
                        </h3>

                        <ul class="result-list">

                `;


                actions.forEach(
                    function (item) {

                        const person =
                            item.person ||
                            "Team";

                        const task =
                            item.task ||
                            "";


                        resultHTML += `

                            <li>

                                <strong>
                                    ${escapeHTML(
                                        person
                                    )}
                                </strong>

                                —
                                
                                ${escapeHTML(
                                    task
                                )}

                            </li>

                        `;
                    }
                );


                resultHTML += `

                        </ul>

                    </section>

                `;
            }


            /* ----------------------------------------
               DEADLINES
               ---------------------------------------- */

            if (deadlines.length > 0) {

                resultHTML += `

                    <section class="result-section">

                        <h3 class="result-heading">
                            ⏰ DEADLINES
                        </h3>

                        <ul class="result-list">

                `;


                deadlines.forEach(
                    function (item) {

                        const date =
                            item.date ||
                            "Deadline";

                        const description =
                            item.description ||
                            "";


                        resultHTML += `

                            <li>

                                <strong>
                                    ${escapeHTML(
                                        date
                                    )}
                                </strong>

                                —

                                ${escapeHTML(
                                    description
                                )}

                            </li>

                        `;
                    }
                );


                resultHTML += `

                        </ul>

                    </section>

                `;
            }


            /* ----------------------------------------
               CLOSE RESULT CONTAINER
               ---------------------------------------- */

            resultHTML += `

                </div>

            `;


            summaryBox.innerHTML =
                resultHTML;


            /* ----------------------------------------
               ENABLE ACTION BUTTONS
               ---------------------------------------- */

            copyBtn.disabled = false;
            downloadBtn.disabled = false;


            /* ----------------------------------------
               ANALYTICS
               ---------------------------------------- */

            updateAnalytics(
                text,
                currentSummary
            );


            /* ----------------------------------------
               SAVE HISTORY
               ---------------------------------------- */

            saveToHistory(
                text,
                currentSummary,
                currentTitle
            );

            displayHistory();


        } catch (error) {

            console.error(
                "SynaptiChat Error:",
                error
            );


            summaryBox.innerHTML = `

                <div class="error-state">

                    <div class="error-icon">
                        ⚠️
                    </div>

                    <h3>
                        Unable to generate summary
                    </h3>

                    <p>
                        Make sure the SynaptiChat
                        AI backend is running.
                    </p>

                    <small>
                        Backend:
                        http://127.0.0.1:8000
                    </small>

                </div>

            `;

        } finally {

            summarizeBtn.disabled = false;

            summarizeBtn.innerHTML =
                "✨ Summarize Chat";
        }
    }
);


/* ============================================================
   ANALYTICS
   ============================================================ */

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
            (
                (original - summary)
                / original
            ) * 100;
    }


    reduction =
        Math.max(
            0,
            Math.min(100, reduction)
        );


    originalWords.textContent =
        original;

    summaryWords.textContent =
        summary;

    reductionPercent.textContent =
        Math.round(reduction) + "%";

    analyticsMessages.textContent =
        countMessages(originalText);
}


/* ============================================================
   COPY SUMMARY
   ============================================================ */

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

            showTemporaryButtonText(
                copyBtn,
                "✅ Copied!",
                "📋 Copy"
            );

        } catch (error) {

            const temp =
                document.createElement(
                    "textarea"
                );

            temp.value =
                currentSummary;

            document.body.appendChild(temp);

            temp.select();

            document.execCommand("copy");

            document.body.removeChild(temp);

            showTemporaryButtonText(
                copyBtn,
                "✅ Copied!",
                "📋 Copy"
            );
        }
    }
);


/* ============================================================
   BUTTON FEEDBACK
   ============================================================ */

function showTemporaryButtonText(
    button,
    temporaryText,
    originalText
) {

    button.textContent =
        temporaryText;

    setTimeout(
        function () {

            button.textContent =
                originalText;

        },
        2000
    );
}


/* ============================================================
   DOWNLOAD SUMMARY
   ============================================================ */

downloadBtn.addEventListener(
    "click",
    function () {

        if (!currentSummary) {
            return;
        }


        const content =
            "SynaptiChat\n" +
            "Conversation Summary\n\n" +
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


        document.body.appendChild(link);

        link.click();

        document.body.removeChild(link);

        URL.revokeObjectURL(url);


        showTemporaryButtonText(
            downloadBtn,
            "✅ Downloaded!",
            "💾 Download"
        );
    }
);


/* ============================================================
   CLEAR CURRENT CHAT
   ============================================================ */

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


/* ============================================================
   HISTORY
   ============================================================ */

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


/* ============================================================
   SAVE HISTORY
   ============================================================ */

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
            new Date()
                .toLocaleString()
    };


    history.unshift(item);


    localStorage.setItem(
        "synaptichat-history",
        JSON.stringify(
            history.slice(0, 20)
        )
    );
}


/* ============================================================
   DISPLAY HISTORY
   ============================================================ */

function displayHistory() {

    const history =
        getHistory();


    if (!history.length) {

        historyList.innerHTML = `

            <p class="history-empty">

                No summaries yet.

                <br><br>

                Your AI summaries will appear here.

            </p>

        `;

        return;
    }


    historyList.innerHTML = "";


    history.forEach(
        function (item) {

            const historyItem =
                document.createElement(
                    "div"
                );


            historyItem.className =
                "history-item";


            historyItem.innerHTML = `

                <div class="history-item-title">

                    📝

                    ${escapeHTML(
                        item.title
                    )}

                </div>


                <div class="history-item-date">

                    ${escapeHTML(
                        item.date
                    )}

                </div>

            `;


            historyItem.addEventListener(
                "click",
                function () {

                    loadHistoryItem(
                        item
                    );

                }
            );


            historyList.appendChild(
                historyItem
            );
        }
    );
}


/* ============================================================
   LOAD HISTORY ITEM
   ============================================================ */

function loadHistoryItem(item) {

    chatInput.value =
        item.original;

    currentSummary =
        item.summary;

    currentTitle =
        item.title;


    summaryTitle.textContent =
        item.title;


    summaryBox.innerHTML = `

        <div class="ai-result">

            <section class="result-section">

                <h3 class="result-heading">
                    📝 SUMMARY
                </h3>

                <p class="generated-summary">

                    ${escapeHTML(
                        item.summary
                    )}

                </p>

            </section>

        </div>

    `;


    copyBtn.disabled = false;
    downloadBtn.disabled = false;


    updateStatistics();

    updateAnalytics(
        item.original,
        item.summary
    );
}


/* ============================================================
   CLEAR HISTORY
   ============================================================ */

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


/* ============================================================
   ESCAPE HTML
   ============================================================ */

function escapeHTML(text) {

    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/* ============================================================
   DARK MODE
   ============================================================ */

const savedTheme =
    localStorage.getItem(
        "smartchat-theme"
    );


if (savedTheme === "dark") {

    document.body.classList.add(
        "dark-mode"
    );

    themeToggle.textContent =
        "☀️";

} else {

    themeToggle.textContent =
        "🌙";
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


/* ============================================================
   INITIALIZE
   ============================================================ */

updateStatistics();

displayHistory();