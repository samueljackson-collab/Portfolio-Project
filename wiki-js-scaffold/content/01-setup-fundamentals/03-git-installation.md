# Git Installation Guide

## 📥 Installing Git on All Platforms

This guide covers Git installation for Windows, macOS, and Linux.

## 🪟 Windows Installation

### Method 1: Official Git Installer (Recommended)

**Step 1: Download Git**
1. Visit [git-scm.com/download/win](https://git-scm.com/download/win)
2. Download will start automatically
3. Or click "Click here to download" if it doesn't

**Step 2: Run the Installer**
1. Double-click the downloaded `.exe` file
2. Click "Yes" if prompted by User Account Control

**Step 3: Installation Options**

Follow these recommended settings:

**License Agreement**
- Click "Next" to accept GNU license

**Installation Location**
- Default: `C:\Program Files\Git`
- Click "Next" (change only if you have a reason)

**Select Components**
- ✅ Git Bash Here (Recommended)
- ✅ Git GUI Here
- ✅ Associate .git* files with default text editor
- ✅ Associate .sh files to be run with Bash
- Click "Next"

**Start Menu Folder**
- Default: "Git"
- Click "Next"

**Default Editor**
- Recommended: "Use Visual Studio Code as Git's default editor"
- Alternative: "Use Vim" (if you know Vim)
- Click "Next"

**Initial Branch Name**
- Select: "Override the default branch name for new repositories"
- Keep: "main"
- Click "Next"

**PATH Environment**
- Select: "Git from the command line and also from 3rd-party software"
- This allows Git in Command Prompt, PowerShell, and Git Bash
- Click "Next"

**SSH Executable**
- Select: "Use bundled OpenSSH"
- Click "Next"

**HTTPS Transport Backend**
- Select: "Use the OpenSSL library"
- Click "Next"

**Line Ending Conversions**
- Select: "Checkout Windows-style, commit Unix-style line endings"
- Click "Next"

**Terminal Emulator**
- Select: "Use MinTTY (the default terminal of MSYS2)"
- Click "Next"

**Default Pull Behavior**
- Select: "Default (fast-forward or merge)"
- Click "Next"

**Credential Helper**
- Select: "Git Credential Manager"
- Click "Next"

**Extra Options**
- ✅ Enable file system caching
- ✅ Enable symbolic links
- Click "Next"

**Experimental Options**
- ⬜ Leave unchecked
- Click "Install"

**Step 4: Complete Installation**
1. Wait for installation (1-2 minutes)
2. ✅ Launch Git Bash
3. Click "Finish"

### Method 2: Windows Package Managers

**Using Winget:**
```powershell
winget install --id Git.Git -e --source winget
```

**Using Chocolatey:**
```powershell
choco install git
```

**Using Scoop:**
```powershell
scoop install git
```

### Verify Windows Installation

**Open Git Bash** (Right-click desktop → "Git Bash Here")

```bash
git --version
# Should output: git version 2.40.0 or higher
```

## 🍎 macOS Installation

### Method 1: Homebrew (Recommended)

**Step 1: Install Homebrew** (if not already installed)

Open Terminal (Applications → Utilities → Terminal):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Step 2: Install Git**

```bash
brew install git
```

**Step 3: Verify Installation**

```bash
git --version
# Should output: git version 2.40.0 or higher
```

### Method 2: Official Git Installer

1. Visit [git-scm.com/download/mac](https://git-scm.com/download/mac)
2. Download the installer
3. Open the downloaded `.dmg` file
4. Follow installation prompts
5. Verify in Terminal: `git --version`

### Method 3: Xcode Command Line Tools

If you have Xcode or plan to do iOS/macOS development:

```bash
xcode-select --install
```

This installs Git along with other development tools.

### Method 4: MacPorts

```bash
sudo port install git
```

## 🐧 Linux Installation

### Debian/Ubuntu

```bash
sudo apt update
sudo apt install git
```

### Fedora

```bash
sudo dnf install git
```

### Arch Linux

```bash
sudo pacman -S git
```

### openSUSE

```bash
sudo zypper install git
```

### CentOS/RHEL

```bash
sudo yum install git
```

### Verify Linux Installation

```bash
git --version
# Should output: git version 2.30.0 or higher
```

## ✅ Post-Installation Verification

### Test Git Installation

**Open your terminal** (Git Bash on Windows, Terminal on macOS/Linux):

```bash
# Check Git version
git --version

# Check Git location
which git  # macOS/Linux
where git  # Windows

# View Git help
git --help
```

### Expected Output

```bash
$ git --version
git version 2.40.1

$ which git
/usr/bin/git

$ git --help
usage: git [--version] [--help] [-C <path>] ...
```

## 🔧 Initial Configuration

After installation, configure your identity:

```bash
# Set your name
git config --global user.name "Your Name"

# Set your email
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list
```

**Full configuration is covered in:** [Git Configuration](./04-git-configuration.md)

## 🐛 Troubleshooting

### Windows Issues

**"git: command not found"**
- Close and reopen Git Bash
- Verify PATH: System Properties → Environment Variables → Path includes Git
- Reinstall Git, ensuring "Git from command line" option is selected

**Permission Denied**
- Run Git Bash as Administrator
- Check antivirus software isn't blocking

### macOS Issues

**"git: command not found"**
- Verify installation: `which git`
- For Homebrew: `brew doctor`
- May need to add to PATH: `export PATH="/usr/local/bin:$PATH"`

**"xcrun: error"**
- Install Xcode Command Line Tools: `xcode-select --install`

### Linux Issues

**"E: Unable to locate package git"**
- Update package list: `sudo apt update` (Debian/Ubuntu)
- Check spelling and repository configuration

**Permission Issues**
- Use `sudo` for installation commands
- Verify user has sudo privileges

### General Issues

**Old Git Version**
```bash
# Check current version
git --version

# Upgrade Git
# Windows: Download and run new installer
# macOS: brew upgrade git
# Linux: sudo apt upgrade git  # or equivalent for your distro
```

## 📊 Version Comparison

| Feature | Git 2.30+ | Git 2.20-2.29 | Git < 2.20 |
|---------|-----------|---------------|------------|
| Default branch (main) | ✅ | Partial | ❌ |
| Performance improvements | ✅ | Partial | ❌ |
| Modern security | ✅ | ✅ | ⚠️ |
| GitHub compatibility | ✅ | ✅ | ✅ |
| **Recommendation** | **Use this** | Acceptable | Upgrade |

## 🎯 Next Steps

### Immediate Next Steps:
1. ✅ Verify Git is installed
2. ✅ Can run `git --version`
3. ✅ Terminal/Git Bash is accessible

### Continue Learning:
- **Next Lesson:** [Git Configuration](./04-git-configuration.md)
- **After That:** [SSH Key Setup](./05-ssh-key-setup.md)

## 💡 Pro Tips

### Multiple Git Versions
You can have different Git versions:
- System Git (from package manager)
- User Git (custom installation)
- Portable Git (no installation needed)

Check which one is active: `which git` (macOS/Linux) or `where git` (Windows)

### Keep Git Updated
```bash
# Check for updates regularly
# Windows: Re-run installer from git-scm.com
# macOS: brew upgrade git
# Linux: sudo apt upgrade git
```

### IDE Integration
Many IDEs have Git built-in:
- Visual Studio Code
- IntelliJ IDEA
- PyCharm
- Sublime Text (with plugin)

But knowing command-line Git is essential!

## 🆘 Still Having Issues?

### Get Help:
1. Check [Git's official documentation](https://git-scm.com/doc)
2. Search [Stack Overflow](https://stackoverflow.com/questions/tagged/git)
3. Ask in course discussions
4. Review [Git installation docs](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### Common Search Phrases:
- "git installation error [your OS]"
- "git command not found [your OS]"
- "how to install git on [your OS]"

---

**Installation complete?** Ready for [Git Configuration](./04-git-configuration.md)!
