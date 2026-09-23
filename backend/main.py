from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from summarizer import summarize_text


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="SynaptiChat API",
    description="AI-powered Chat Log Summarization System",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class ChatRequest(BaseModel):
    text: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Welcome to SynaptiChat API",
        "status": "running"
    }


# ============================================================
# SUMMARIZE CHAT
# ============================================================

@app.post("/summarize")
def summarize(request: ChatRequest):

    if not request.text.strip():

        raise HTTPException(
            status_code=400,
            detail="Please enter some chat text to summarize."
        )

    try:

        result = summarize_text(request.text)

        # ----------------------------------------------------
        # The AI summarizer returns a dictionary containing:
        # summary
        # actions
        # deadlines
        # ----------------------------------------------------

        if not isinstance(result, dict):

            raise HTTPException(
                status_code=500,
                detail="Invalid response from AI summarizer."
            )


        summary = result.get(
            "summary",
            ""
        )


        if not isinstance(summary, str) or not summary.strip():

            raise HTTPException(
                status_code=500,
                detail="The AI model did not generate a summary."
            )


        # ----------------------------------------------------
        # Return complete structured result to frontend
        # ----------------------------------------------------

        return {
            "summary": summary.strip(),

            "actions": result.get(
                "actions",
                []
            ),

            "deadlines": result.get(
                "deadlines",
                []
            )
        }


    except HTTPException:
        raise


    except Exception as e:

        print(
            "Summarization error:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating the summary."
        )


# ============================================================
# LOGIN
# ============================================================

@app.post("/login")
def login(request: LoginRequest):

    email = str(
        request.email
    ).strip()

    password = request.password


    # --------------------------------------------------------
    # Password length
    # --------------------------------------------------------

    if len(password) < 8:

        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 8 characters."
        )


    # --------------------------------------------------------
    # Uppercase requirement
    # --------------------------------------------------------

    if not any(
        char.isupper()
        for char in password
    ):

        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one uppercase letter."
        )


    # --------------------------------------------------------
    # Number requirement
    # --------------------------------------------------------

    if not any(
        char.isdigit()
        for char in password
    ):

        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one number."
        )


    # --------------------------------------------------------
    # Special character requirement
    # --------------------------------------------------------

    if not any(
        not char.isalnum()
        for char in password
    ):

        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one special character."
        )


    return {
        "message": "Login successful",
        "email": email
    }