# GoldMine - Multi-Bot Automation Platform

A comprehensive PyQt5-based desktop application for managing and automating interactions with multiple blockchain and Web3 applications, including profile management, wallet integration, and automated farming tasks.

## 🌟 Features

### 🤖 Supported Platforms

- **Blum** - Automated engagement with Blum ecosystem
- **Wolf Game** - Game automation with intelligent pathfinding and resource management
- **Sonic** - Arcade game automation
- **Wow** - Automated gameplay
- **Twitter/X** - Automated interactions and engagement
- **Telegram** - Bot automation and messaging
- **IMX** - Immutable X integration
- **Pawns** - Network participation bot

### 💼 Browser & Profile Management

- **GPM Integration** - Load and manage GPM browser profiles
- **ADS Power Integration** - ADS browser profile management
- **Chrome** - Direct Chrome browser profile loading
- **Wallet Integration**:
  - Metamask
  - Phantom
  - Rabby
  - Ronin
  - TonKeeper

### 🔧 Core Features

- Multi-threaded task execution for parallel farming
- JSON-based profile and configuration management
- Real-time logging and monitoring
- Keyboard & mouse automation
- Selenium-based web automation
- Screenshot and image recognition capabilities
- Excel integration for data management

## 📋 Requirements

- Python 3.8+
- PyQt5 and related libraries
- Selenium with ChromeDriver
- OpenCV for image processing
- Various automation and cryptocurrency libraries

## 🚀 Installation & Setup

### 1. Clone or Extract the Project

```bash
cd /Users/robgm/Documents/GoldMine/GoldMine
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Application

Edit `src/ui/JSON_FILE/config.json`:

```json
{
  "gpm_url": "http://your-gpm-server:19995",
  "adspower_url": "http://your-adspower-server:50325/",
  "chrome_path": "/path/to/chrome",
  "screen_index": "1"
}
```

## 🎯 Usage

### Quick Start

```bash
./run.sh
```

Or manually:

```bash
source venv/bin/activate
python src/main.py
```

### Via Terminal

```bash
cd /Users/robgm/Documents/GoldMine/GoldMine
source venv/bin/activate
python src/main.py
```

### GUI Walkthrough

1. **Dashboard** - View and manage all profiles from GPM, ADS, or Chrome
2. **Load Profiles** - Click "Cargar GPM", "Cargar ADS", or "Cargar Google Chrome" to import profiles
3. **Select Automation** - Choose from the available automated tasks:
   - Click on any bot module (Blum, Wolf Game, Sonic, etc.)
   - Select profiles to execute tasks on
   - Configure task parameters
4. **Monitor Execution** - View live logs in the Log Window
5. **View Analytics** - Check farming results in the Analytics section

## 📁 Project Structure

```
GoldMine/
├── src/
│   ├── main.py                 # Application entry point
│   ├── clean.py               # Cleanup utilities
│   └── ui/                    # PyQt5 GUI implementation
│       ├── main_window.py     # Main application window
│       ├── pages.py           # Page components
│       ├── components.py      # Reusable UI components
│       ├── api_manager.py     # API integrations (GPM, ADS)
│       ├── config.py          # Configuration management
│       ├── entrypoint.py      # Application entry
│       ├── JSON_FILE/         # Configuration JSON files
│       ├── Blum/              # Blum bot automation
│       ├── WolfGame/          # Wolf Game bot
│       ├── Sonic/             # Sonic games automation
│       ├── Wow/               # Wow game automation
│       ├── twitter/           # Twitter automation
│       ├── TelegramTool/      # Telegram bot automation
│       ├── Wallets/           # Wallet integrations
│       ├── FarmeosTelegram/   # Farming tools
│       ├── PaymentPage/       # Payment integration
│       └── Imx/               # Immutable X integration
├── requirements.txt           # Python dependencies
├── run.sh                     # Quick launch script
└── README.md                  # This file
```

## ⚙️ Configuration Files

### config.json

Main configuration file for API endpoints and preferences:

- `gpm_url` - GPM browser manager endpoint
- `adspower_url` - ADS Power browser manager endpoint
- `chrome_path` - Custom Chrome browser path (optional)
- `screen_index` - Display index for multi-monitor setups

### keys.json

API keys and subscription information (automatically managed by the application)

### profiles.json

Saved user profiles and automation configurations

### farm_logs.json

Automated farming activity logs and results

## 🔒 Security & Privacy

- **Do NOT commit sensitive data** to version control:
  - API keys or authentication tokens
  - Wallet addresses or private keys
  - Personal file paths
  - Server IP addresses or URLs
- Store credentials in environment variables or `.env` files
- Use `.gitignore` to exclude sensitive JSON files

## 🐛 Troubleshooting

### "Can't open/read file" errors

- Ensure media files exist in `ui/media/` directories
- Check file paths in configuration

### API Connection Errors

- Verify GPM server is running on configured URL
- Verify ADS Power server is running
- Check firewall and network settings

### Import Errors

- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again
- Check Python version is 3.8+

## 📝 Development

### Adding New Bot

1. Create new folder in `src/ui/`
2. Create `YourBotPage.py` for UI
3. Create `Backend/YourBotScript.py` for automation logic
4. Register in `pages.py`

### Debugging

Enable debug mode in `src/ui/config.py`:

```python
DEBUG = True
```

## 📦 Building Executable

Convert to standalone .exe or .app:

```bash
source venv/bin/activate
auto-py-to-exe
```

## 📄 License

See [License.txt](src/License.txt) for licensing information.

## 🤝 Contributing

Contributions are welcome! Please ensure:

- No sensitive data is committed
- Code follows project structure
- All dependencies are in `requirements.txt`
- Documentation is updated

## ⚠️ Disclaimer

This tool is provided for educational and legitimate automation purposes only. Users are responsible for ensuring compliance with:

- Terms of Service of all targeted platforms
- Local laws and regulations
- Ethical automation practices

Unauthorized access or abuse of services is prohibited.

## 📞 Support

For issues, questions, or contributions, please refer to the project repository.

---

**Last Updated:** April 2026  
**Version:** 1.0
