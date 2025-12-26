# SSH Key Setup for GitHub

## 🔐 What is SSH?

SSH (Secure Shell) provides secure authentication to GitHub without entering your password every time.

## 🎯 Why Use SSH Keys?

- ✅ **More Secure** - Stronger than password authentication
- ✅ **More Convenient** - No password entry on every push/pull
- ✅ **Required** - For some GitHub operations
- ✅ **Professional** - Industry standard practice

## 📋 Prerequisites

- Git installed and configured
- Terminal/Git Bash access
- GitHub account (we'll create in next lesson if needed)

## 🔑 Generate SSH Key

### Step 1: Check for Existing Keys

```bash
ls -la ~/.ssh
```

Look for files named `id_rsa.pub`, `id_ed25519.pub`, or similar. If they exist, you might already have SSH keys.

### Step 2: Generate New SSH Key

**Using Ed25519 (Recommended):**
```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
```

**Using RSA (if Ed25519 not supported):**
```bash
ssh-keygen -t rsa -b 4096 -C "your.email@example.com"
```

**Replace** `your.email@example.com` with your actual email (same as Git config).

### Step 3: Save the Key

```
Enter file in which to save the key (/home/you/.ssh/id_ed25519):
```

**Press Enter** to accept default location.

### Step 4: Set Passphrase (Optional but Recommended)

```
Enter passphrase (empty for no passphrase):
```

**Options:**
- **Set a passphrase** - More secure (recommended)
- **Leave empty** - More convenient

Type your passphrase and press Enter (it won't show on screen).

### Step 5: Confirm

You should see:
```
Your identification has been saved in /home/you/.ssh/id_ed25519
Your public key has been saved in /home/you/.ssh/id_ed25519.pub
The key fingerprint is:
SHA256:... your.email@example.com
```

## 🔓 Add SSH Key to ssh-agent

### Windows (Git Bash)

```bash
# Start ssh-agent
eval "$(ssh-agent -s)"

# Add your key
ssh-add ~/.ssh/id_ed25519
```

### macOS

```bash
# Start ssh-agent
eval "$(ssh-agent -s)"

# Add key to agent and keychain
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

### Linux

```bash
# Start ssh-agent
eval "$(ssh-agent -s)"

# Add your key
ssh-add ~/.ssh/id_ed25519
```

## 📤 Add SSH Key to GitHub

### Step 1: Copy Your Public Key

**macOS:**
```bash
pbcopy < ~/.ssh/id_ed25519.pub
```

**Linux:**
```bash
cat ~/.ssh/id_ed25519.pub
# Then manually select and copy the output
```

**Windows (Git Bash):**
```bash
cat ~/.ssh/id_ed25519.pub | clip
```

**Or display and copy manually:**
```bash
cat ~/.ssh/id_ed25519.pub
```

### Step 2: Add to GitHub

1. Go to [GitHub.com](https://github.com)
2. Click your profile photo → **Settings**
3. In sidebar, click **SSH and GPG keys**
4. Click **New SSH key** or **Add SSH key**
5. **Title**: "My Laptop" or descriptive name
6. **Key type**: Authentication Key
7. **Key**: Paste your public key
8. Click **Add SSH key**
9. Confirm with your GitHub password if prompted

## ✅ Test SSH Connection

```bash
ssh -T git@github.com
```

**First time?** You'll see:
```
The authenticity of host 'github.com (IP)' can't be established.
...
Are you sure you want to continue connecting (yes/no)?
```

Type `yes` and press Enter.

**Success looks like:**
```
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

## 🔧 Configure Git to Use SSH

### Clone with SSH URLs

**Instead of HTTPS:**
```bash
git clone https://github.com/username/repo.git
```

**Use SSH:**
```bash
git clone git@github.com:username/repo.git
```

### Convert Existing Repository

```bash
# Check current URL
git remote -v

# Change to SSH
git remote set-url origin git@github.com:username/repo.git

# Verify
git remote -v
```

## 🐛 Troubleshooting

### "Permission denied (publickey)"

**Solutions:**
```bash
# 1. Verify key is added to agent
ssh-add -l

# 2. Add key if missing
ssh-add ~/.ssh/id_ed25519

# 3. Verify key on GitHub
# Go to github.com/settings/keys

# 4. Test connection with verbose output
ssh -vT git@github.com
```

### "Could not open a connection to your authentication agent"

```bash
# Start ssh-agent
eval "$(ssh-agent -s)"

# Then add key
ssh-add ~/.ssh/id_ed25519
```

### Wrong Key Being Used

```bash
# Specify key explicitly in SSH config
# Create/edit ~/.ssh/config

Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
```

## 💡 Multiple SSH Keys

### For Multiple GitHub Accounts

Create `~/.ssh/config`:

```
# Work account
Host github-work
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_work

# Personal account
Host github-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal
```

**Usage:**
```bash
# Clone with work account
git clone git@github-work:company/repo.git

# Clone with personal account
git clone git@github-personal:username/repo.git
```

## 🔐 Security Best Practices

### ✅ Do's
- ✅ Use a passphrase
- ✅ Use Ed25519 keys (modern and secure)
- ✅ Keep private key private (never share `id_ed25519`)
- ✅ Add keys to specific devices only
- ✅ Remove keys from GitHub when device is lost/sold

### ❌ Don'ts
- ❌ Share your private key (`id_ed25519`)
- ❌ Commit SSH keys to Git repositories
- ❌ Email SSH keys
- ❌ Use same key across all services
- ❌ Leave keys on shared/public computers

## 📁 SSH Key Files

### Understanding the Files

**Private Key** (`id_ed25519` or `id_rsa`)
- ⚠️ **Keep Secret!** - Never share
- Stays on your computer only
- Used to prove your identity

**Public Key** (`id_ed25519.pub` or `id_rsa.pub`)
- ✅ Safe to share - Add to GitHub
- Verifies signatures from private key
- Can be freely distributed

## ✅ SSH Setup Checklist

Before continuing, verify:

- [ ] SSH key generated successfully
- [ ] Public key added to GitHub
- [ ] `ssh -T git@github.com` succeeds
- [ ] No "permission denied" errors
- [ ] Key is added to ssh-agent

## 🚀 Next Steps

**SSH configured?** You're ready for:
- **Next:** [GitHub Account Creation](./06-github-account-creation.md)
- **Or:** Already have an account? Jump to [Git Fundamentals](../02-git-fundamentals/01-repository-basics.md)

---

**SSH issues?** Ask in the discussions with error messages!
