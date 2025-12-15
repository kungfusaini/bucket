# Well TUI

Simple terminal interface for the Well API.

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

Run the program:
```bash
./well.py
```

Or:
```bash
python3 well.py
```

### Features

- **Write Entry**: Create new tasks, notes, or bookmarks (stay in write submenu)
- **Read Entry**: View existing entries by type (stay in read submenu)  
- **Editor Integration**: Uses your preferred editor ($EDITOR)
- **Temp File Cleanup**: Automatic cleanup after editing
- **Submenu Navigation**: Stay in write/read workflows until you choose to exit

### API Endpoints

- Base URL: `https://vulkan.sumeetsaini.com/well`
- Types: `task`, `note`, `bookmark`

The `.env` file should contain your production API key and will not be tracked by git.