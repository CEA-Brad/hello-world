import os
import tkinter as tk

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

        # sidebar for conversation titles
        self.sidebar = tk.Frame(master, width=180, bg="#ececec")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(self.sidebar, text="Conversations", bg="#ececec", font=("Helvetica", 14, "bold")).pack(pady=10)

        # main chat container
        self.chat_container = tk.Frame(master, bg="#f7f5f2")
        self.chat_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # scrolling area for messages
        self.canvas = tk.Canvas(self.chat_container, bg="#f7f5f2", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.chat_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.messages_frame = tk.Frame(self.canvas, bg="#f7f5f2")
        self.canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")
        self.messages_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # input area styled like modern chats
        self.entry = tk.Entry(self.chat_container, font=("Helvetica", 12), bg="#ffffff", relief=tk.FLAT)
        self.entry.pack(padx=10, pady=(0, 10), side=tk.LEFT, expand=True, fill=tk.X)
        self.entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(
            self.chat_container,
            text="Send",
            command=self.send_message,
            bg="#4a90e2",
            fg="white",
            relief=tk.FLAT,
        )
        self.send_button.pack(padx=10, pady=(0, 10), side=tk.RIGHT)

        if ChatMemory:
            self.memory = ChatMemory(persona="You are a friendly assistant.", human="")
        else:
            self.memory = None

    def append_to_chat(self, speaker, text):
        frame = tk.Frame(self.messages_frame, bg="#f7f5f2")
        bg = "#e1ffc7" if speaker == "You" else "#ffffff"
        anchor = "e" if speaker == "You" else "w"
        label = tk.Label(
            frame,
            text=text,
            bg=bg,
            wraplength=400,
            justify=tk.LEFT,
            font=("Helvetica", 12),
            padx=10,
            pady=5,
        )
        label.pack(anchor=anchor, pady=2, padx=10)
        frame.pack(fill=tk.BOTH, anchor=anchor)
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

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
