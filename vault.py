import hashlib
import json
import os
import getpass

VAULT_FILE = "my_vault.vlt"

def derive_key(passphrase):
    """Turn your text PIN into a 32-byte encryption key."""
    return hashlib.sha256(passphrase.encode('utf-8')).digest()

def encrypt_data(plaintext, passphrase):
    """Convert your text/link into a long number string."""
    key = derive_key(passphrase)
    pt_bytes = plaintext.encode('utf-8')
    # XOR encryption: each byte of text is mixed with the key
    ct_bytes = bytes([pt_bytes[i] ^ key[i % len(key)] for i in range(len(pt_bytes))])
    # Convert encrypted bytes into ONE big number
    return str(int.from_bytes(ct_bytes, 'big'))

def decrypt_data(num_str, passphrase):
    """Turn the number string back into your original text."""
    key = derive_key(passphrase)
    num = int(num_str)
    byte_len = (num.bit_length() + 7) // 8
    ct_bytes = num.to_bytes(byte_len, 'big')
    pt_bytes = bytes([ct_bytes[i] ^ key[i % len(key)] for i in range(len(ct_bytes))])
    return pt_bytes.decode('utf-8')

def load_vault():
    if not os.path.exists(VAULT_FILE):
        return {}
    with open(VAULT_FILE, 'r') as f:
        return json.load(f)

def save_vault(vault):
    with open(VAULT_FILE, 'w') as f:
        json.dump(vault, f)

def main():
    print("=" * 55)
    print("   PERSONAL VAULT — Local Encrypted Storage")
    print("=" * 55)
    
    while True:
        print("\n[1] Add new entry")
        print("[2] List all entries")
        print("[3] Decrypt an entry")
        print("[4] Delete an entry")
        print("[5] Exit")
        
        choice = input("\nChoose (1-5): ").strip()
        
        if choice == '1':
            label = input("Label (e.g., 'github-account'): ").strip()
            data = input("Enter link or text: ").strip()
            pin = input("Set your master PIN: ").strip()
            encrypted = encrypt_data(data, pin)
            vault = load_vault()
            vault[label] = encrypted
            save_vault(vault)
            print(f"✓ Saved! Looks like: {encrypted[:40]}...")
            
        elif choice == '2':
            vault = load_vault()
            if not vault:
                print("Vault is empty.")
            else:
                print("\nStored entries (encrypted preview):")
                for label, enc in vault.items():
                    print(f" • {label}: {enc[:30]}...")
                    
        elif choice == '3':
            vault = load_vault()
            if not vault:
                print("Vault is empty.")
                continue
            label = input("Entry label: ").strip()
            if label not in vault:
                print("✗ Entry not found.")
                continue
            pin = input("Master PIN: ").strip()
            try:
                decrypted = decrypt_data(vault[label], pin)
                print(f"\n🔓 Decrypted: {decrypted}")
            except Exception:
                print("✗ Wrong PIN or corrupted data.")
                
        elif choice == '4':
            vault = load_vault()
            label = input("Entry to delete: ").strip()
            if label in vault:
                del vault[label]
                save_vault(vault)
                print("✓ Deleted.")
            else:
                print("✗ Not found.")
                
        elif choice == '5':
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()
