# WarmChat

WarmChat is a minimal desktop chat application inspired by the look of Claude. It connects to language models like ChatGPT and optionally integrates the [letta](https://github.com/letta-ai/letta) memory system.

## Features

- Friendly Tkinter based UI with a layout similar to Claude
- Optional integration with `letta` for advanced memory management
- Uses OpenAI's API by default; set `OPENAI_API_KEY` in your environment

## Setup

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

If `letta` is unavailable, the chat still works but without advanced memory features.
