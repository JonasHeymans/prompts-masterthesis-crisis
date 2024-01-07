import tkinter as tk
from tkinter import filedialog, Scrollbar, messagebox
import openai
import subprocess
import datetime as dt


openai.api_key = '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'
messages = [{"role": "system", "content": ""}]

def convert_rtf_to_txt(filepath):
    output_filepath = filepath.replace('.rtf', '.txt')
    subprocess.run(["textutil", "-convert", "txt", filepath, "-output", output_filepath])
    with open(output_filepath, 'r') as f:
        return f.read()

def save_prompt():
    filepath = filedialog.asksaveasfilename(defaultextension=".rtf", filetypes=[("RTF files", "*.rtf"), ("Text files", "*.txt")])
    if filepath:
        prompt_text = prompt_display.get("1.0", "end-1c")
        if filepath.endswith('.rtf'):
            save_as_rtf(prompt_text, filepath)
        else:
            with open(filepath, 'w') as f:
                f.write(prompt_text)

def save_as_rtf(text, filepath):
    with open(filepath, 'w') as f:
        f.write(r"{\rtf1\ansi\ansicpg1252\cocoartf1671\cocoasubrtf600")
        f.write("\n")
        f.write(text.replace('\n', '\\par '))
        f.write("\n")
        f.write("}")

def load_prompt():
    filepath = filedialog.askopenfilename(filetypes=[("RTF files", "*.rtf"), ("Text files", "*.txt")])
    if filepath:
        text = convert_rtf_to_txt(filepath)
        messages[0]["content"] = text
        prompt_display.delete("1.0", tk.END)
        prompt_display.insert(tk.END, text)

def save_chat_history():
    now = dt.datetime.now().strftime()
    filepath = f"{now}/chat_history.rtf"  # You can change this to your desired file path
    with open(filepath, 'a') as f:
        f.write(r"{\rtf1\ansi\ansicpg1252\cocoartf1671\cocoasubrtf600")
        f.write("\n")
        for message in messages:
            text = message["content"].replace('\n', '\\par ')
            f.write(f"{message['role']}: {text}\\par ")
        f.write("\n")
        f.write("}")


def load_chat_history():
    filepath = filedialog.askopenfilename(defaultextension=".rtf", filetypes=[("RTF files", "*.rtf")])
    if filepath:
        with open(filepath, 'r') as f:
            # Skip the RTF header
            f.readline()
            chat_data = f.read().split('\\par ')
            global messages
            messages = []
            for line in chat_data:
                if line.startswith("user:"):
                    messages.append({"role": "user", "content": line[6:]})
                elif line.startswith("assistant:"):
                    messages.append({"role": "assistant", "content": line[11:]})

def process_input():
    user_input = text_field.get("1.0", "end-1c")
    if user_input:
        print(f"Sending to OpenAI:, {user_input}")
        messages.append({"role": "user", "content": user_input})
        chat = openai.ChatCompletion.create(
            model="gpt-4-1106-preview", messages=messages
        )
        reply = chat.choices[0].message["content"]
        clear_output()  # Clear the output before displaying new messages
        display_message(reply.strip('"'), "assistant")
        text_field.delete("1.0", tk.END)
        messages.append({"role": "assistant", "content": reply})
        # display_message("Assignment received successfully.", "assistant")
        save_chat_history()  # Automatically save the chat history

        # # Display the last two messages (one from the user and one from the assistant)
        # if len(messages) > 2:
        #     for message in messages[-2:]:
        #         display_message(message['content'], message['role'])


def clear_output():
    chat_log.config(state=tk.NORMAL)
    chat_log.delete("1.0", tk.END)
    chat_log.config(state=tk.DISABLED)

def display_message(message, role):
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, message + "\n", role)
    chat_log.config(state=tk.DISABLED)
    chat_log.see(tk.END)

def clear_chat_log():
    chat_log.config(state=tk.NORMAL)
    chat_log.delete("1.0", tk.END)
    chat_log.config(state=tk.DISABLED)


def set_font_styles():
    chat_log.tag_configure("user", foreground="blue")
    chat_log.tag_configure("assistant", foreground="green")

root = tk.Tk()
root.title("JonasBot")
root.geometry("800x800")

load_prompt_button = tk.Button(root, text="Load Prompt", command=load_prompt)
load_prompt_button.pack()

load_chat_button = tk.Button(root, text="Load Chat", command=load_chat_history)
load_chat_button.pack()

prompt_display = tk.Text(root, wrap="word", height=10, width=80)
prompt_display.pack(pady=10)
prompt_scroll = Scrollbar(root, command=prompt_display.yview)
prompt_scroll.pack(side=tk.RIGHT, fill=tk.Y)
prompt_display.config(yscrollcommand=prompt_scroll.set)

text_field = tk.Text(root, wrap="word", height=5, width=80)
text_field.pack(pady=10)

send_button = tk.Button(root, text="Send", command=process_input)
send_button.pack()

clear_chat_button = tk.Button(root, text="Clear Chat", command=clear_chat_log)
clear_chat_button.pack()

chat_log = tk.Text(root, wrap="word", height=20, width=80)
chat_log.pack(padx=10, pady=10)
chat_log.config(state=tk.DISABLED)
chat_scroll = Scrollbar(root, command=chat_log.yview)
chat_scroll.pack(side=tk.RIGHT, fill=tk.Y)
chat_log.config(yscrollcommand=chat_scroll.set)

save_prompt_button = tk.Button(root, text="Save Prompt", command=save_prompt)
save_prompt_button.pack()

set_font_styles()

root.mainloop()

