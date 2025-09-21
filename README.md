# Python Based Command Terminal  

## Overview  
The **Python Based Command Terminal** is a client-side web app that recreates a Linux-like shell directly in your browser.  
It operates on a **sandboxed virtual filesystem** stored in your browser’s `localStorage`, ensuring your real system files remain untouched.  
This provides a completely safe environment for **learning and experimenting** with shell commands.  

A standout capability is its **AI integration through OpenRouter**.  
If you enter something the terminal doesn’t recognize, it interprets your input as plain English, asks the AI to convert it into the right shell command, and runs it automatically.  

---

## ✨ Key Features  
- **Virtual Filesystem**  
  Create, edit, and remove files/folders in a protected environment that persists between sessions.  

- **Standard Unix Commands**  
  Includes common commands like `ls`, `cd`, `mkdir`, `cat`, `rm`, `mv`, and a lightweight `ps`.  

- **AI-Assisted Commands**  
  Convert natural language into shell commands on the fly.  
  Example:  
  _“make a folder called my_project”_ → `mkdir my_project`.  

- **Downloadable Tool**  
  Option to download a Python pseudo-compiler for offline usage.  

---

## 🚀 Getting Started  
This project runs as a single-page app. No installation needed.  

1. Clone or download this repository.  
2. Open `index.html` in a modern browser (Chrome, Firefox, Edge).  
3. Start using the **virtual terminal** immediately.  

---

## 🔑 API Key Setup (for AI features)  
To use natural language command conversion, you’ll need an **OpenRouter API key**.  

1. **Get a Key**  
   Sign up at [OpenRouter.ai](https://openrouter.ai), then go to **Keys** in your account and create a new one.  

2. **Enter the Key**  
   Copy your key and paste it into the **“OpenRouter API Key”** field in the app’s control bar.  

3. **Save the Key**  
   Click **Save Key**.  
   It will be securely stored in your browser’s localStorage and remembered for future sessions.  

---

## 🖥️ Usage  
- Type `help` to view the full list of available commands.  
- Use the shell just like a real Linux terminal.  

### Example  
```bash
mkdir test_folder
cd test_folder
ls
