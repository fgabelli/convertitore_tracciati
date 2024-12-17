import bcrypt

# Lista delle password in chiaro
passwords = ["password1", "password2"]

# Generazione degli hash
hashed_passwords = [bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') for password in passwords]

# Stampa gli hash generati
print("Hashed passwords:")
for i, hashed in enumerate(hashed_passwords):
    print(f"Password {i+1}: {hashed}")
