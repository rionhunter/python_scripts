import unittest
import os
from text_editing.remove_citations_gui import remove_citations_from_markdown

test_md_content = '''OpenAI **Codex** is a context-aware AI coding partner that can read your codebase, make edits, run commands, and even propose pull requests for review[\[1\]](https://binaryverseai.com/how-to-use-openai-codex/#:~:text=Openai%20Codex%20is%20a%20coding,tools%20you%20have%20to%20juggle). It’s available across multiple surfaces – a terminal CLI tool, IDE extensions, a web interface, GitHub integration, and more – all using the same AI “brain” behind the scenes[\[1\]](https://binaryverseai.com/how-to-use-openai-codex/#:~:text=Openai%20Codex%20is%20a%20coding,tools%20you%20have%20to%20juggle). The focus of this guide is the **Codex CLI**, the in-terminal module (e.g. usable from PowerShell, Bash, etc.), which lets you interact with Codex right in your project directory. Codex CLI is designed to feel like pair programming: you describe tasks or ask questions in natural language, and the AI agent uses your local code context to help build, refactor, or explain your software. By 2025, Codex leverages advanced models (like GPT-5-Codex) optimized for coding tasks, making it faster and more reliable at everything from quick fixes to generating entire features. Codex is included with OpenAI’s ChatGPT Plus/Pro (and higher) plans, and heavy users can also use it with API billing if needed[\[2\]](https://binaryverseai.com/how-to-use-openai-codex/#:~:text=Availability%20remains%20straightforward,the%20default%20in%20the%20cloud)[\[3\]](https://binaryverseai.com/how-to-use-openai-codex/#:~:text=You%20can%20use%20Openai%20Codex,key%20billing%20and%20keep%20going).

## Installation and Setup

Setting up the Codex CLI is straightforward. It supports macOS and Linux natively, with Windows support via WSL (Windows Subsystem for Linux) for best results[\[4\]](https://developers.openai.com/codex/cli/#:~:text=Set%20up)[\[5\]](https://developers.openai.com/codex/windows#:~:text=For%20best%20performance%20on%20Windows%2C,WSL2). You can install the CLI globally using a package manager: for example, with **npm** run npm install -g @openai/codex, or on macOS with **Homebrew** run brew install codex[\[6\]](https://developers.openai.com/codex/cli/#:~:text=Install%20Codex)[\[7\]](https://github.com/openai/codex#:~:text=Install%20globally%20with%20your%20preferred,If%20you%20use%20npm). (There are also precompiled binaries on the GitHub releases page for those who prefer a direct download[\[8\]](https://github.com/openai/codex#:~:text=codex).) Once installed, launch Codex by simply typing codex in your terminal[\[9\]](https://github.com/openai/codex#:~:text=brew%20install%20codex).
'''

expected_md_content = '''OpenAI **Codex** is a context-aware AI coding partner that can read your codebase, make edits, run commands, and even propose pull requests for review. It’s available across multiple surfaces – a terminal CLI tool, IDE extensions, a web interface, GitHub integration, and more – all using the same AI “brain” behind the scenes. The focus of this guide is the **Codex CLI**, the in-terminal module (e.g. usable from PowerShell, Bash, etc.), which lets you interact with Codex right in your project directory. Codex CLI is designed to feel like pair programming: you describe tasks or ask questions in natural language, and the AI agent uses your local code context to help build, refactor, or explain your software. By 2025, Codex leverages advanced models (like GPT-5-Codex) optimized for coding tasks, making it faster and more reliable at everything from quick fixes to generating entire features. Codex is included with OpenAI’s ChatGPT Plus/Pro (and higher) plans, and heavy users can also use it with API billing if needed.

## Installation and Setup

Setting up the Codex CLI is straightforward. It supports macOS and Linux natively, with Windows support via WSL (Windows Subsystem for Linux) for best results. You can install the CLI globally using a package manager: for example, with **npm** run npm install -g @openai/codex, or on macOS with **Homebrew** run brew install codex. (There are also precompiled binaries on the GitHub releases page for those who prefer a direct download.) Once installed, launch Codex by simply typing codex in your terminal.
'''

class TestRemoveCitations(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test_citations.md'
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(test_md_content)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_remove_citations(self):
        remove_citations_from_markdown(self.test_file)
        with open(self.test_file, 'r', encoding='utf-8') as f:
            result = f.read()
        self.assertEqual(result, expected_md_content)

if __name__ == '__main__':
    unittest.main()
