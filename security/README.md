# Security Tools

A comprehensive suite of security and encryption utilities for file hashing, password generation, and file encryption.

## Tools

### 1. Hash Tool (`hash_tool.py`)

Calculate and verify file hashes using various algorithms.

**Features:**
- Multiple hash algorithms: MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512
- Single file or directory hashing
- Hash verification
- Multiple hash calculation at once
- Efficient chunk-based reading for large files

**Usage:**
```bash
# Calculate SHA-256 hash (default)
python hash_tool.py file.txt

# Calculate MD5 hash
python hash_tool.py file.txt -a md5

# Calculate multiple hashes
python hash_tool.py file.txt -m md5 sha1 sha256

# Verify hash
python hash_tool.py file.txt -v abc123...

# Hash all files in directory
python hash_tool.py directory/ -d

# Hash directory recursively
python hash_tool.py directory/ -d -r
```

### 2. Password Tool (`password_tool.py`)

Generate secure passwords and check password strength.

**Features:**
- Customizable password length and character sets
- Memorable passphrase generation
- Password strength checker with detailed criteria
- Batch password generation
- Character exclusion support

**Usage:**
```bash
# Generate 16-character password (default)
python password_tool.py

# Generate 20-character password
python password_tool.py -l 20

# Generate password without special characters
python password_tool.py -l 12 --no-special

# Generate memorable passphrase
python password_tool.py --memorable

# Generate 5 passwords
python password_tool.py -n 5

# Check password strength
python password_tool.py -c "MyPassword123!"
```

**Password Strength Criteria:**
- Length (≥8 characters)
- Character diversity (uppercase, lowercase, digits, special)
- No common patterns
- No repeated characters (3+)
- No sequential characters

### 3. Encryption Tool (`encryption_tool.py`)

Encrypt and decrypt files using AES-256 encryption.

**Features:**
- AES-256 encryption with Fernet
- PBKDF2 key derivation (100,000 iterations)
- Password-based encryption
- Single file or directory encryption
- Secure password prompts

**Usage:**
```bash
# Encrypt a file
python encryption_tool.py -e file.txt -o file.txt.encrypted

# Decrypt a file
python encryption_tool.py -d file.txt.encrypted -o file.txt

# Encrypt with auto-generated output name
python encryption_tool.py -e document.pdf

# Decrypt with auto-generated output name
python encryption_tool.py -d document.pdf.encrypted

# Encrypt entire directory
python encryption_tool.py -e /path/to/dir --directory

# Decrypt directory recursively
python encryption_tool.py -d /path/to/dir --directory -r
```

**Security Notes:**
- Encrypted files include a random salt
- Uses PBKDF2 with 100,000 iterations for key derivation
- Keep your password safe - there is no password recovery
- Encrypted files have `.encrypted` extension by default

## Installation

Install required dependencies:
```bash
pip install -r requirements.txt
```

## Dependencies

- `cryptography`: For AES encryption (encryption_tool.py only)
- Standard library: `hashlib`, `argparse`, `random`, `string`, `re`, `getpass`

## Examples

### Hash Multiple Files
```bash
# Hash all Python files in current directory
for file in *.py; do
    python hash_tool.py "$file"
done
```

### Batch Password Generation
```bash
# Generate 10 secure passwords
python password_tool.py -n 10 -l 20
```

### Encrypt Important Files
```bash
# Encrypt a sensitive document
python encryption_tool.py -e sensitive.pdf
# Creates: sensitive.pdf.encrypted
```

## Security Best Practices

1. **Passwords**: Use strong, unique passwords for encryption
2. **Key Storage**: Never hardcode passwords in scripts
3. **Hash Verification**: Always verify file integrity with hashes
4. **Backup**: Keep encrypted backups in multiple locations
5. **Password Manager**: Use the password generator with a password manager

## Testing

Run basic tests:
```bash
# Test hash tool
python hash_tool.py README.md

# Test password generator
python password_tool.py -l 16

# Test encryption (requires cryptography library)
echo "test data" > test.txt
python encryption_tool.py -e test.txt -p "test123"
python encryption_tool.py -d test.txt.encrypted -p "test123"
rm test.txt test.txt.encrypted test.txt.decrypted
```
