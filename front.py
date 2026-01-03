import tkinter as tk
from tkinter import scrolledtext
import threading
import datetime
try:
    from crew import get_news_analysis
    BACKEND_AVAILABLE = True
except Exception as e:
    BACKEND_AVAILABLE = False
    _backend_import_error = str(e)

# Name for the chatbot
BOT_NAME = "ASH BOT"
# Font family used throughout the UI (widely available on Linux)
FONT_FAMILY = "DejaVu Sans"

def insert_message(role: str, text: str):
    """Insert a message into chat_area with timestamp and role tag."""
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    chat_area.config(state=tk.NORMAL)
    if role.lower() == 'you' or role.lower() == 'user':
        chat_area.insert(tk.END, f"[{ts}] You: ", 'user')
        chat_area.insert(tk.END, text + "\n\n")
    else:
        chat_area.insert(tk.END, f"[{ts}] {BOT_NAME}: ", 'bot')
        chat_area.insert(tk.END, text + "\n\n")
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)

def send_message():
    user_msg = user_input.get().strip()
    if not user_msg:
        return

    # Display user message using formatted insert
    insert_message('you', user_msg)

    user_input.delete(0, tk.END)

    # Remember where the thinking placeholder starts so we can replace it later
    thinking_start = None
    chat_area.config(state=tk.NORMAL)
    thinking_start = chat_area.index(tk.END)
    chat_area.insert(tk.END, f"{BOT_NAME}: Thinking...\n\n", 'thinking')
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)
    send_button.config(state=tk.DISABLED)

    # Run backend call on a worker thread
    def worker():
        try:
            if BACKEND_AVAILABLE:
                result = get_news_analysis(user_msg)
                if result is None:
                    result = "No result from backend."
            else:
                result = "Backend not available: " + _backend_import_error

        except Exception as exc:
            result = "Error while fetching analysis: " + str(exc)

    def finish():
            # Replace the thinking placeholder with the real response and re-enable controls
            chat_area.config(state=tk.NORMAL)
            try:
                chat_area.delete(thinking_start, tk.END)
            except Exception:
                pass

            insert_message('bot', result)
            send_button.config(state=tk.NORMAL)

            root.after(0, finish)


# Main window
root = tk.Tk()
# Colors and theme
BG = "#0f1724"          # dark navy
PANEL = "#0b1220"       # slightly lighter panel
ACCENT = "#7c3aed"      # purple
USER_BG = "#e0f2fe"     # light blue for user bubble
BOT_BG = "#d1fae5"      # light green for bot bubble
INPUT_BG = "#f8fafc"    # input background (light)
TEXT_COLOR = "#e6eef8"  # light text on dark bg

root.title(BOT_NAME)
root.geometry("620x660")
root.resizable(False, False)
root.configure(bg=BG)

# Header
header = tk.Frame(root, bg=PANEL, height=64)
header.pack(fill=tk.X, padx=8, pady=(8, 6))

# Bot title and status
title_lbl = tk.Label(header, text=BOT_NAME, bg=PANEL, fg=TEXT_COLOR, font=(FONT_FAMILY, 16, 'bold'))
title_lbl.pack(side=tk.LEFT, padx=(12,8))

# status indicator
status_canvas = tk.Canvas(header, width=16, height=16, bg=PANEL, highlightthickness=0)
status_canvas.pack(side=tk.LEFT)
status_dot = status_canvas.create_oval(2,2,14,14, fill="#10b981" if BACKEND_AVAILABLE else "#ef4444")

# small subtitle
subtitle = tk.Label(header, text="AI News Assistant", bg=PANEL, fg="#9fb3d1", font=(FONT_FAMILY, 10))
subtitle.pack(side=tk.LEFT, padx=(8,0))

# Chat display (panel)
chat_panel = tk.Frame(root, bg=PANEL)
chat_panel.pack(padx=8, pady=(0,8), fill=tk.BOTH, expand=True)

chat_area = scrolledtext.ScrolledText(
    chat_panel, wrap=tk.WORD, state=tk.DISABLED, font=(FONT_FAMILY, 11), bg=PANEL, fg=TEXT_COLOR, relief=tk.FLAT, bd=0, insertbackground=TEXT_COLOR
)

# configure tags for styling using Font objects
import tkinter.font as tkfont
_user_font = tkfont.Font(family=FONT_FAMILY, size=11, weight='bold')
_bot_font = tkfont.Font(family=FONT_FAMILY, size=11)
_thinking_font = tkfont.Font(family=FONT_FAMILY, size=11, slant='italic')
# margins emulate bubbles: user on right, bot on left
chat_area.tag_config('user', foreground='#042b5b', background=USER_BG, font=_user_font, lmargin1=80, lmargin2=80, rmargin=8)
chat_area.tag_config('bot', foreground='#065f46', background=BOT_BG, font=_bot_font, lmargin1=8, lmargin2=8, rmargin=80)
chat_area.tag_config('meta', foreground='#9fb3d1', font=(FONT_FAMILY, 9))
chat_area.tag_config('thinking', foreground='#94a3b8', font=_thinking_font)
chat_area.pack(padx=12, pady=12, fill=tk.BOTH, expand=True)

# Input area
input_panel = tk.Frame(root, bg=INPUT_BG, height=90)
input_panel.pack(fill=tk.X, padx=8, pady=(0,8))

# User input (single-line) kept for simplicity
user_input = tk.Entry(input_panel, font=(FONT_FAMILY, 12), bg="white", fg="#0b1220")
user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(12,8), pady=12, ipady=6)

# Buttons frame
buttons_frame = tk.Frame(input_panel, bg=INPUT_BG)
buttons_frame.pack(side=tk.RIGHT, padx=(0,12), pady=12)

# Send button (accent)
send_button = tk.Button(buttons_frame, text="Send", command=send_message, bg=ACCENT, fg="white", activebackground="#5b21b6", relief=tk.FLAT)
send_button.pack(side=tk.TOP, fill=tk.X)

# Clear button
def clear_chat():
    chat_area.config(state=tk.NORMAL)
    chat_area.delete('1.0', tk.END)
    chat_area.config(state=tk.DISABLED)

clear_button = tk.Button(buttons_frame, text="Clear", command=clear_chat, bg="#374151", fg="white", relief=tk.FLAT)
clear_button.pack(side=tk.TOP, pady=(8,0), fill=tk.X)

# Export button
def export_conversation():
    try:
        raw = chat_area.get('1.0', tk.END).strip()
        if not raw:
            return
        fname = f"conversation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(raw)
        status_text.set(f"Saved to {fname}")
    except Exception as e:
        status_text.set(f"Export failed: {e}")

export_button = tk.Button(buttons_frame, text="Export", command=export_conversation, bg="#111827", fg="white", relief=tk.FLAT)
export_button.pack(side=tk.TOP, pady=(8,0), fill=tk.X)

# Backend status label
status_text = tk.StringVar()
if BACKEND_AVAILABLE:
    status_text.set(f"{BOT_NAME} backend: available")
else:
    status_text.set(f"{BOT_NAME} backend: unavailable")

status_label = tk.Label(root, textvariable=status_text, anchor='w', bg=BG, fg=TEXT_COLOR)
status_label.pack(fill=tk.X, padx=12, pady=(0,8))

# Enter key binding (Enter sends, Shift+Enter inserts newline)
def on_enter(event):
    if event.state & 0x0001:  # Shift held
        user_input.insert(tk.END, "\n")
    else:
        send_message()
    return 'break'

root.bind('<Return>', on_enter)
root.bind('<Shift-Return>', on_enter)

root.mainloop()

