from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Word-hint pairs
WORD_BANK = [
    ("python", "A popular programming language."),
    ("hangman", "The game you're playing."),
    ("developer", "A person who writes code."),
    ("keyboard", "A computer input device."),
    ("interface", "Point of interaction in software."),
    ("variable", "Storage for a value in code.")
]

# Initialize game
def init_game():
    word, hint = random.choice(WORD_BANK)
    return {
        "word": word,
        "hint": hint,
        "correct": [],
        "guessed": [],
        "attempts_left": 6
    }

game_state = init_game()

@app.get("/", response_class=HTMLResponse)
async def get_game(request: Request):
    word_display = " ".join([l if l in game_state["correct"] else "_" for l in game_state["word"]])
    return templates.TemplateResponse("index.html", {
        "request": request,
        "word_display": word_display,
        "attempts_left": game_state["attempts_left"],
        "guessed": game_state["guessed"],
        "hint": game_state["hint"],
        "message": ""
    })

@app.post("/guess", response_class=HTMLResponse)
async def guess_letter(request: Request, letter: str = Form(...)):
    letter = letter.lower()
    message = ""

    if letter in game_state["guessed"]:
        message = f"You already guessed '{letter}'"
    elif letter in game_state["word"]:
        game_state["correct"].append(letter)
        message = f"Good! '{letter}' is in the word."
    else:
        game_state["attempts_left"] -= 1
        message = f"Oops! '{letter}' is not in the word."

    game_state["guessed"].append(letter)

    word_display = " ".join([l if l in game_state["correct"] else "_" for l in game_state["word"]])
    win = "_" not in word_display
    lose = game_state["attempts_left"] <= 0

    if win:
        message = f"You win! The word was '{game_state['word']}'"
    elif lose:
        message = f"Game over! The word was '{game_state['word']}'"

    return templates.TemplateResponse("index.html", {
        "request": request,
        "word_display": word_display,
        "attempts_left": game_state["attempts_left"],
        "guessed": game_state["guessed"],
        "hint": game_state["hint"],
        "message": message
    })

@app.get("/reset", response_class=HTMLResponse)
async def reset_game(request: Request):
    global game_state
    game_state = init_game()
    return RedirectResponse(url="/", status_code=302)
