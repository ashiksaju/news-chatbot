import tkinter as tk
from tkinter import scrolledtext
import threading
import datetime
try:
    from PIL import Image
    from PIL.ImageTk import PhotoImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
import os
try:
    from crew import get_news_analysis
    BACKEND_AVAILABLE = True
except Exception as e:
    BACKEND_AVAILABLE = False
    _backend_import_error = str(e)

# Name for the chatbot
BOT_NAME = "ASHFIT AI"
# Font family used throughout the UI
FONT_FAMILY = "Segoe UI"

def load_dumbbell_image(size="medium"):
    """Load and return dumbbell image"""
    try:
        filename = f"dumbbell_{size}.png"
        if os.path.exists(filename):
            print(f"Loading {filename}...")
            if PIL_AVAILABLE:
                img = Image.open(filename)
                photo = PhotoImage(img)
                print(f"Successfully loaded {filename}")
                return photo
            else:
                print("PIL not available, using tkinter PhotoImage")
                # Try with tkinter's PhotoImage
                photo = tk.PhotoImage(file=filename)
                print(f"Successfully loaded {filename} with tkinter")
                return photo
        else:
            print(f"File {filename} not found")
    except Exception as e:
        print(f"Error loading {filename}: {e}")
    return None

def load_muscular_person_image():
    """Load and return muscular person image"""
    try:
        filename = "muscular_person.png"
        if os.path.exists(filename):
            print(f"Loading {filename}...")
            photo = tk.PhotoImage(file=filename)
            print(f"Successfully loaded {filename}")
            return photo
        else:
            print(f"File {filename} not found")
    except Exception as e:
        print(f"Error loading {filename}: {e}")
    return None

def create_dumbbell_icon(canvas, x, y, size=20, color="#ffffff"):
    """Draw a detailed dumbbell icon on canvas"""
    # Main bar (handle)
    bar_width = size // 2
    bar_height = size // 8
    canvas.create_rectangle(x + size//4, y + size//2 - bar_height//2, 
                           x + 3*size//4, y + size//2 + bar_height//2, 
                           fill=color, outline="", width=0)
    
    # Left weight plates
    weight_width = size // 6
    weight_height = size // 2
    # Outer left plate
    canvas.create_rectangle(x, y + size//4, x + weight_width, y + 3*size//4, 
                           fill=color, outline="", width=0)
    # Inner left plate
    canvas.create_rectangle(x + weight_width, y + size//3, x + size//4, y + 2*size//3, 
                           fill=color, outline="", width=0)
    
    # Right weight plates
    # Inner right plate
    canvas.create_rectangle(x + 3*size//4, y + size//3, x + size - weight_width, y + 2*size//3, 
                           fill=color, outline="", width=0)
    # Outer right plate
    canvas.create_rectangle(x + size - weight_width, y + size//4, x + size, y + 3*size//4, 
                           fill=color, outline="", width=0)
    
    # Add some detail lines for 3D effect
    detail_color = color if color == "#ffffff" else "#ffffff"
    canvas.create_line(x + weight_width//2, y + size//4 + 2, 
                      x + weight_width//2, y + 3*size//4 - 2, 
                      fill=detail_color, width=1)
    canvas.create_line(x + size - weight_width//2, y + size//4 + 2, 
                      x + size - weight_width//2, y + 3*size//4 - 2, 
                      fill=detail_color, width=1)
    
    return canvas

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
        
        # Schedule the finish function to run on the main thread
        root.after(0, lambda: finish(result))

    def finish(result):
        # Replace the thinking placeholder with the real response and re-enable controls
        chat_area.config(state=tk.NORMAL)
        try:
            chat_area.delete(thinking_start, tk.END)
        except Exception:
            pass

        insert_message('bot', result)
        send_button.config(state=tk.NORMAL)

    # Start the worker thread
    threading.Thread(target=worker, daemon=True).start()


# Main window
root = tk.Tk()

# Load dumbbell images
header_dumbbell = load_dumbbell_image("medium")
input_dumbbell = load_dumbbell_image("small")

# Professional black and grey theme
BG = "#1a1a1a"          # dark black
PANEL = "#2d2d2d"       # dark grey panel
ACCENT = "#4a90e2"      # professional blue
USER_BG = "#3a3a3a"     # dark grey for user bubble
BOT_BG = "#404040"      # lighter grey for bot bubble
INPUT_BG = "#2d2d2d"    # dark grey input
TEXT_COLOR = "#ffffff"  # white text
SECONDARY_TEXT = "#b0b0b0"  # light grey text

root.title(f"{BOT_NAME} - Professional Fitness Assistant")
root.geometry("1200x900")
root.resizable(True, True)
root.configure(bg=BG)
root.minsize(1000, 700)
root.state('zoomed') if root.tk.call('tk', 'windowingsystem') == 'win32' else None

# Header with professional styling
header = tk.Frame(root, bg=PANEL, height=120)
header.pack(fill=tk.X, padx=0, pady=0)
header.pack_propagate(False)

# Left side with dumbbell icon and title
left_header = tk.Frame(header, bg=PANEL)
left_header.pack(side=tk.LEFT, fill=tk.Y, padx=30, pady=20)

# Real dumbbell image in header
if header_dumbbell:
    icon_label = tk.Label(left_header, image=header_dumbbell, bg=PANEL)
    icon_label.pack(side=tk.LEFT, padx=(0,20))
else:
    # Fallback to canvas drawing if image fails
    icon_canvas = tk.Canvas(left_header, width=50, height=50, bg=PANEL, highlightthickness=0)
    icon_canvas.pack(side=tk.LEFT, padx=(0,20))
    create_dumbbell_icon(icon_canvas, 5, 10, 40, TEXT_COLOR)

# Title and subtitle container
title_frame = tk.Frame(left_header, bg=PANEL)
title_frame.pack(side=tk.LEFT, fill=tk.Y)

title_lbl = tk.Label(title_frame, text=BOT_NAME, bg=PANEL, fg=TEXT_COLOR, font=(FONT_FAMILY, 24, 'bold'))
title_lbl.pack(anchor='w')

subtitle = tk.Label(title_frame, text="Professional Fitness Assistant", bg=PANEL, fg=SECONDARY_TEXT, font=(FONT_FAMILY, 14))
subtitle.pack(anchor='w')

# Right side with status
right_header = tk.Frame(header, bg=PANEL)
right_header.pack(side=tk.RIGHT, fill=tk.Y, padx=30, pady=20)

# Status indicator with better styling
status_frame = tk.Frame(right_header, bg=PANEL)
status_frame.pack(side=tk.RIGHT)

status_canvas = tk.Canvas(status_frame, width=16, height=16, bg=PANEL, highlightthickness=0)
status_canvas.pack(side=tk.LEFT, padx=(0,10))
status_dot = status_canvas.create_oval(2,2,14,14, fill="#00ff88" if BACKEND_AVAILABLE else "#ff4444")

status_lbl = tk.Label(status_frame, text="Online" if BACKEND_AVAILABLE else "Offline", 
                     bg=PANEL, fg="#00ff88" if BACKEND_AVAILABLE else "#ff4444", 
                     font=(FONT_FAMILY, 12, 'bold'))
status_lbl.pack(side=tk.LEFT)

# Chat display with professional styling
chat_panel = tk.Frame(root, bg=BG)
chat_panel.pack(padx=25, pady=(15,20), fill=tk.BOTH, expand=True)

chat_area = scrolledtext.ScrolledText(
    chat_panel, wrap=tk.WORD, state=tk.DISABLED, font=(FONT_FAMILY, 13), 
    bg=PANEL, fg=TEXT_COLOR, relief=tk.FLAT, bd=0, insertbackground=TEXT_COLOR,
    selectbackground=ACCENT, selectforeground="white"
)

# Professional message styling
import tkinter.font as tkfont
_user_font = tkfont.Font(family=FONT_FAMILY, size=13, weight='bold')
_bot_font = tkfont.Font(family=FONT_FAMILY, size=13)
_thinking_font = tkfont.Font(family=FONT_FAMILY, size=13, slant='italic')

# Professional bubble styling with better spacing
chat_area.tag_config('user', foreground=TEXT_COLOR, background=USER_BG, font=_user_font, 
                    lmargin1=150, lmargin2=150, rmargin=30, spacing1=8, spacing3=8)
chat_area.tag_config('bot', foreground=TEXT_COLOR, background=BOT_BG, font=_bot_font, 
                    lmargin1=30, lmargin2=30, rmargin=150, spacing1=8, spacing3=8)
chat_area.tag_config('thinking', foreground=SECONDARY_TEXT, font=_thinking_font, 
                    lmargin1=30, lmargin2=30)
chat_area.pack(padx=0, pady=0, fill=tk.BOTH, expand=True)

# Display initial greeting message
def show_initial_greeting():
    welcome_msg = "Hi! My name is Ash, your personal fitness companion. How may I help you?"
    insert_message('bot', welcome_msg)

# Show greeting after a short delay to ensure UI is ready
root.after(500, show_initial_greeting)

# Professional input area
input_panel = tk.Frame(root, bg=INPUT_BG, height=120)
input_panel.pack(fill=tk.X, padx=25, pady=(0,20))
input_panel.pack_propagate(False)

# Input with real dumbbell image
input_container = tk.Frame(input_panel, bg=INPUT_BG)
input_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=20)

# Real dumbbell image next to input
if input_dumbbell:
    input_icon_label = tk.Label(input_container, image=input_dumbbell, bg=INPUT_BG)
    input_icon_label.pack(side=tk.LEFT, padx=(0,15))
else:
    # Fallback to canvas drawing if image fails
    input_icon = tk.Canvas(input_container, width=40, height=40, bg=INPUT_BG, highlightthickness=0)
    input_icon.pack(side=tk.LEFT, padx=(0,15))
    create_dumbbell_icon(input_icon, 6, 10, 28, "#ffffff")

# Professional input field
user_input = tk.Entry(input_container, font=(FONT_FAMILY, 14), bg="#404040", fg=TEXT_COLOR, 
                     relief=tk.FLAT, bd=0, insertbackground=TEXT_COLOR)
user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=12, padx=(0,20))

# Professional buttons
buttons_frame = tk.Frame(input_container, bg=INPUT_BG)
buttons_frame.pack(side=tk.RIGHT)

# Send button with better styling
send_button = tk.Button(buttons_frame, text="Send", command=send_message, 
                       bg=ACCENT, fg="white", activebackground="#357abd", 
                       relief=tk.FLAT, font=(FONT_FAMILY, 12, 'bold'), 
                       padx=25, pady=12)
send_button.pack(side=tk.LEFT, padx=(0,10))

# Clear button
def clear_chat():
    chat_area.config(state=tk.NORMAL)
    chat_area.delete('1.0', tk.END)
    chat_area.config(state=tk.DISABLED)

clear_button = tk.Button(buttons_frame, text="Clear", command=clear_chat, 
                        bg="#555555", fg="white", activebackground="#666666",
                        relief=tk.FLAT, font=(FONT_FAMILY, 12), padx=20, pady=12)
clear_button.pack(side=tk.LEFT, padx=(0,10))

# Export button
def export_conversation():
    try:
        raw = chat_area.get('1.0', tk.END).strip()
        if not raw:
            return
        fname = f"conversation_export.txt"
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(raw)
        status_text.set(f"Exported: {fname}")
    except Exception as e:
        status_text.set(f"Export failed: {e}")

export_button = tk.Button(buttons_frame, text="Export", command=export_conversation, 
                         bg="#333333", fg="white", activebackground="#444444",
                         relief=tk.FLAT, font=(FONT_FAMILY, 12), padx=20, pady=12)
export_button.pack(side=tk.LEFT)

# Professional footer status
footer = tk.Frame(root, bg=PANEL, height=40)
footer.pack(fill=tk.X, padx=0, pady=0)
footer.pack_propagate(False)

status_text = tk.StringVar()
if BACKEND_AVAILABLE:
    status_text.set("Backend: Connected | Ready for fitness queries | AI Engine: Groq Llama-3.1")
else:
    status_text.set("Backend: Disconnected | Limited functionality | Check API configuration")

status_label = tk.Label(footer, textvariable=status_text, anchor='w', 
                       bg=PANEL, fg=SECONDARY_TEXT, font=(FONT_FAMILY, 11))
status_label.pack(fill=tk.X, padx=30, pady=12)

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

