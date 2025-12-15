# Bucket

Simple terminal interface for my well API, my solution to quickly capturing thoughts.

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with your API key:
```bash
echo "WELL_API_KEY=your_production_key_here" > .env
```

3. Make sure you have an editor set (defaults to nvim):
```bash
export EDITOR=nvim  # or vim, code, etc.
```

## Usage

Just run the program:
```bash
./bucket.py
```

### Features

- **Write Entry**: Create new tasks, notes, or bookmarks
- **Read Entry**: View and edit existing entries by type
- **Change Detection**: Automatically detects if you made changes and asks for confirmation

### API Endpoints

- Base URL: `https://vulkan.sumeetsaini.com/well`
- Types: `task`, `note`, `bookmark`
- POST: Append new entries
- GET: Read entire file content
- PUT: Replace entire file content (for editing)

