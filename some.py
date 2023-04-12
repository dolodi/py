import poe
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk

conversation_history = []

def send_message_threaded(event=None):
    threading.Thread(target=send_message).start()

def is_scrollbar_at_bottom(scrollbar):
    return scrollbar.get()[1] == 1.0

def send_message():
    message = user_input.get()
    if not message.strip():
        return

    # Add user message to the conversation history
    conversation_history.append(f"User: {message}")

    chat_box.configure(state='normal')
    chat_box.insert(tk.END, f"User: {message}\n")
    chat_box.see(tk.END)
    chat_box.configure(state='disabled')
    user_input.delete(0, tk.END)

    # Show the loading spinner
    loading_spinner.grid(row=2, column=0, columnspan=2)
    loading_spinner.start()

    # Combine conversation history into a single string
    conversation_text = "\n".join(conversation_history)

    # Truncate conversation history to fit within the token limit
    max_tokens = 4096
    tokens = len(conversation_text)  # Replace this with a function to count tokens if needed
    while tokens > max_tokens:
        # Remove the oldest message from the conversation history
        conversation_history.pop(0)
        conversation_text = "\n".join(conversation_history)
        tokens = len(conversation_text)  # Replace this with a function to count tokens if needed

    # Connect to the GPT model and get the response
    token = poe.Account.create(logging=True)

    chat_box.configure(state='normal')
    chat_box.insert(tk.END, "GPT-4: ")
    chat_box.see(tk.END)
    chat_box.configure(state='disabled')

    for response in poe.StreamingCompletion.create(
        model='gpt-4',
        prompt=conversation_text,
        token=token
    ):
        gpt_response = response.completion.choices[0].text

         # Remove 'GPT-4' from the response if it's present
        if 'GPT-4' in gpt_response:
            gpt_response = gpt_response.replace('GPT-4', '')
        

        # Add the GPT response to the chat box
        chat_box.configure(state='normal')
        chat_box.insert(tk.END, gpt_response)
        chat_box.see(tk.END)
        chat_box.configure(state='disabled')
        root.update()

    chat_box.configure(state='normal')
    chat_box.insert(tk.END, "\n")
    chat_box.see(tk.END)
    chat_box.configure(state='disabled')

    # Hide the loading spinner
    loading_spinner.stop()
    loading_spinner.grid_forget()

    # Add AI response to the conversation history
    conversation_history.append(f" {gpt_response}")

root = tk.Tk()
root.title("ChatGPT")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

chat_box = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=15, state='disabled')
chat_box.grid(row=0, column=0, columnspan=2, pady=(0, 10))

chat_box_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=chat_box.yview)
chat_box.configure(yscrollcommand=chat_box_scrollbar.set)
chat_box_scrollbar.grid(row=0, column=2, sticky='ns')

user_input = tk.Entry(frame, width=40)
user_input.grid(row=1, column=0, pady=(0, 10), sticky="ew")

send_button = tk.Button(frame, text="Send", command=send_message_threaded)
send_button.grid(row=1, column=1, pady=(0, 10), sticky="ew")

# Bind the Enter key to the send_message_threaded function
root.bind('<Return>', send_message_threaded)

# Create a loading spinner
loading_spinner = ttk.Progressbar(frame, mode="indeterminate", length=100)

# Initially, do not display the loading spinner
loading_spinner.grid_forget()

root.mainloop()