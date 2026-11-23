
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import threading
import ollama

# COSC 4272 - AI Study Assistant
# Student: Brice Nyindie Djiwa
# AI Model: Ollama Llama 3.2


# Get an AI-generated answer
def get_answer(question):
    question = question.strip()

    if not question:
        return "Please enter a computer science question."

    try:
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful Computer Science "
                        "Study Assistant. Explain programming, "
                        "networking, databases, cybersecurity, "
                        "and artificial intelligence clearly. "
                        "Provide examples when useful."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        return response["message"]["content"]

    except Exception as error:
        return (
            "Unable to connect to the AI model.\n"
            "Make sure Ollama is running and "
            "Llama 3.2 is installed.\n\n"
            f"Error: {error}"
        )


# Display the AI-generated answer
def display_answer(answer):
    chat_box.config(state=tk.NORMAL)

    chat_box.insert(
        tk.END,
        f"Assistant: {answer}\n\n"
    )

    chat_box.see(tk.END)
    chat_box.config(state=tk.DISABLED)

    ask_button.config(
        text="Ask Question",
        state=tk.NORMAL
    )

    entry.config(state=tk.NORMAL)
    entry.focus_set()


# Process the question in a background thread
def process_question(question):
    answer = get_answer(question)
    root.after(0, display_answer, answer)


# Handle the Ask Question button
def ask_question():
    if ask_button["state"] == tk.DISABLED:
        return

    question = entry.get().strip()

    if not question:
        return

    current_time = datetime.now().strftime("%H:%M:%S")

    chat_box.config(state=tk.NORMAL)

    chat_box.insert(
        tk.END,
        f"\n[{current_time}] You: {question}\n"
    )

    chat_box.see(tk.END)
    chat_box.config(state=tk.DISABLED)

    entry.delete(0, tk.END)
    entry.config(state=tk.DISABLED)

    ask_button.config(
        text="Thinking...",
        state=tk.DISABLED
    )

    worker = threading.Thread(
        target=process_question,
        args=(question,),
        daemon=True
    )

    worker.start()


# Clear the conversation
def clear_chat():
    chat_box.config(state=tk.NORMAL)
    chat_box.delete("1.0", tk.END)

    chat_box.insert(
        tk.END,
        "Welcome! Ask me a computer science question.\n"
    )

    chat_box.config(state=tk.DISABLED)


# Create the main application window
root = tk.Tk()

root.title("AI Study Assistant - COSC 4272")
root.geometry("750x550")
root.configure(bg="#edf2f7")


# Application title
title = tk.Label(
    root,
    text="AI Study Assistant",
    font=("Arial", 22, "bold"),
    bg="#edf2f7",
    fg="#17365d"
)

title.pack(pady=12)


# Subtitle
subtitle = tk.Label(
    root,
    text="Computer Science Learning Assistant",
    font=("Arial", 12),
    bg="#edf2f7"
)

subtitle.pack()


# Conversation display
chat_box = scrolledtext.ScrolledText(
    root,
    wrap=tk.WORD,
    font=("Arial", 11),
    height=19
)

chat_box.pack(
    padx=20,
    pady=15,
    fill=tk.BOTH,
    expand=True
)

chat_box.insert(
    tk.END,
    "Welcome! Ask me a computer science question.\n"
)

chat_box.config(state=tk.DISABLED)


# Question input
entry = tk.Entry(
    root,
    font=("Arial", 12)
)

entry.pack(
    padx=20,
    pady=5,
    fill=tk.X
)


# Ask Question button
ask_button = tk.Button(
    root,
    text="Ask Question",
    command=ask_question,
    bg="#1769aa",
    fg="white",
    font=("Arial", 11, "bold")
)

ask_button.pack(pady=5)


# Clear Chat button
clear_button = tk.Button(
    root,
    text="Clear Chat",
    command=clear_chat,
    font=("Arial", 10)
)

clear_button.pack(pady=5)


# Allow Enter key to submit a question
entry.bind(
    "<Return>",
    lambda event: ask_question()
)

entry.focus_set()


# Start the application
root.mainloop()
