# Git Configuration Basics

## 🎯 Why Configuration Matters

Git needs to know who you are before you can make commits. This information appears in every commit you create.

## 🔧 Essential Configuration

### 1. Set Your Identity

**Your Name:**
```bash
git config --global user.name "Your Full Name"
```

**Your Email:**
```bash
git config --global user.email "your.email@example.com"
```

**Important:** Use the same email you'll use for GitHub!

### 2. Verify Your Configuration

```bash
# View all configuration
git config --list

# View specific settings
git config user.name
git config user.email
```

### 3. Set Default Branch Name

```bash
git config --global init.defaultBranch main
```

Modern convention is `main` instead of `master`.

### 4. Set Default Editor

**For Visual Studio Code:**
```bash
git config --global core.editor "code --wait"
```

**For Vim:**
```bash
git config --global core.editor "vim"
```

**For Nano:**
```bash
git config --global core.editor "nano"
```

## 📊 Configuration Levels

Git has three configuration levels:

### System (All Users)
```bash
git config --system setting value
# Location: /etc/gitconfig or C:\Program Files\Git\etc\gitconfig
```

### Global (Your User)
```bash
git config --global setting value
# Location: ~/.gitconfig or C:\Users\YourName\.gitconfig
```

### Local (Current Repository)
```bash
git config --local setting value
# Location: .git/config in your repository
```

**Priority:** Local > Global > System

## 🎨 Useful Optional Settings

### Enable Colored Output
```bash
git config --global color.ui auto
```

### Set Line Ending Preferences

**Windows:**
```bash
git config --global core.autocrlf true
```

**macOS/Linux:**
```bash
git config --global core.autocrlf input
```

### Configure Credential Helper

**Windows:**
```bash
git config --global credential.helper wincred
```

**macOS:**
```bash
git config --global credential.helper osxkeychain
```

**Linux:**
```bash
git config --global credential.helper cache
```

### Set Default Pull Behavior
```bash
git config --global pull.rebase false
```

## 🔍 View Your Configuration

### All Settings
```bash
git config --list --show-origin
```

### Specific Setting
```bash
git config user.name
git config user.email
```

### Edit Config File Directly
```bash
# Edit global config
git config --global --edit

# Edit local config (in a repository)
git config --local --edit
```

## 📝 Sample .gitconfig File

```ini
[user]
    name = John Doe
    email = john.doe@example.com

[init]
    defaultBranch = main

[core]
    editor = code --wait
    autocrlf = true

[color]
    ui = auto

[pull]
    rebase = false

[credential]
    helper = wincred

[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    lg = log --oneline --graph --decorate
```

## 🎯 Common Git Aliases

Speed up your workflow with aliases:

```bash
# Status shortcut
git config --global alias.st status

# Checkout shortcut
git config --global alias.co checkout

# Branch shortcut
git config --global alias.br branch

# Commit shortcut
git config --global alias.ci commit

# Beautiful log
git config --global alias.lg "log --oneline --graph --decorate --all"

# Last commit
git config --global alias.last "log -1 HEAD"

# Unstage files
git config --global alias.unstage "reset HEAD --"
```

**Usage:**
```bash
git st              # Instead of git status
git co main         # Instead of git checkout main
git lg              # Beautiful commit history
```

## 🐛 Troubleshooting

### Wrong Email or Name

```bash
# Change it
git config --global user.name "Correct Name"
git config --global user.email "correct@email.com"

# Verify
git config user.name
git config user.email
```

### Remove a Setting

```bash
git config --global --unset setting.name
```

### Reset All Configuration

```bash
# View config file location
git config --list --show-origin

# Edit or delete the file manually
# Global: ~/.gitconfig or C:\Users\YourName\.gitconfig
```

## ✅ Configuration Checklist

Before moving on, verify:

- [ ] `git config user.name` returns your name
- [ ] `git config user.email` returns your email
- [ ] `git config init.defaultBranch` returns "main"
- [ ] `git config --list` shows your settings
- [ ] No error messages appear

## 🚀 Next Steps

**Configuration complete?** Move on to:
- **Next:** [SSH Key Setup](./05-ssh-key-setup.md)
- **After:** [GitHub Account Creation](./06-github-account-creation.md)

---

**Questions about configuration?** Ask in the discussions!
