import os
import tkinter as tk
from tkinter import scrolledtext

try:
    from letta.schemas.memory import ChatMemory
except ImportError:
    ChatMemory = None

class ChatApp:
    def __init__(self, master):
        self.master = master
        master.title("WarmChat")
        master.geometry("600x700")
        master.configure(bg="#f7f5f2")

        self.chat_display = scrolledtext.ScrolledText(master, wrap=tk.WORD, state='disabled', bg='#ffffff', font=('Helvetica', 12))
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.entry = tk.Entry(master, width=80)
        self.entry.pack(padx=10, pady=(0, 10), side=tk.LEFT, expand=True, fill=tk.X)
        self.entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack(padx=10, pady=(0, 10), side=tk.RIGHT)

        if ChatMemory:
            self.memory = ChatMemory(persona="You are a friendly assistant.", human="")
        else:
            self.memory = None

    def append_to_chat(self, speaker, text):
        self.chat_display['state'] = 'normal'
        self.chat_display.insert(tk.END, f"{speaker}: {text}\n")
        self.chat_display['state'] = 'disabled'
        self.chat_display.see(tk.END)

    def send_message(self, event=None):
        user_input = self.entry.get().strip()
        if not user_input:
            return
        self.append_to_chat("You", user_input)
        if self.memory:
            self.memory.core_memory_append(None, "human", user_input)
        self.entry.delete(0, tk.END)
        response = self.get_ai_response(user_input)
        self.append_to_chat("Assistant", response)
        if self.memory:
            self.memory.core_memory_append(None, "persona", response)

    def get_ai_response(self, prompt):
        try:
            import openai
            openai.api_key = os.getenv("OPENAI_API_KEY", "")
            if not openai.api_key:
                raise RuntimeError("OPENAI_API_KEY not set")
            messages = [{"role": "system", "content": "You are a helpful assistant."}]
            if self.memory:
                for block in self.memory.blocks:
                    messages.append({"role": block.label, "content": block.value})
            messages.append({"role": "user", "content": prompt})
            completion = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"(Failed to reach API: {e})"

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
