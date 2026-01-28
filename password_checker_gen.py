import tkinter as tk
from tkinter import messagebox, ttk
import string
import secrets
import math
import qrcode
from PIL import Image, ImageTk

# ------------------ Core Logic ------------------

def calculate_entropy(password):
    charset = ""

    if any(c.isupper() for c in password):
        charset += string.ascii_uppercase
    if any(c.islower() for c in password):
        charset += string.ascii_lowercase
    if any(c.isdigit() for c in password):
        charset += string.digits
    if any(c in string.punctuation for c in password):
        charset += string.punctuation

    if len(charset) == 0:
        return 0

    entropy = len(password) * math.log2(len(charset))
    return entropy


def classify_entropy(entropy):
    if entropy < 28:
        return "Very Weak"
    elif entropy < 36:
        return "Weak"
    elif entropy < 60:
        return "Reasonable"
    elif entropy < 128:
        return "Strong"
    else:
        return "Very Strong"


def estimate_crack_time(entropy):
    guesses_per_second = 1e10  # Offline hash attack assumption
    seconds = (2 ** entropy) / guesses_per_second

    intervals = [
        ("years", 60 * 60 * 24 * 365),
        ("days", 60 * 60 * 24),
        ("hours", 60 * 60),
        ("minutes", 60),
        ("seconds", 1),
    ]

    for name, count in intervals:
        if seconds >= count:
            value = seconds / count
            return f"{value:.2f} {name}"

    return "less than a second"


def generate_password(length=16):
    all_chars = string.ascii_letters + string.digits + string.punctuation

    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation),
    ]

    password += [secrets.choice(all_chars) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(password)

    return ''.join(password)

# ------------------ GUI Logic ------------------

def check_strength():
    pwd = password_var.get()

    if not pwd:
        messagebox.showwarning("Input Error", "Password cannot be empty")
        return

    entropy = calculate_entropy(pwd)
    strength = classify_entropy(entropy)
    crack_time = estimate_crack_time(entropy)

    result_label.config(text=f"Strength: {strength}")
    entropy_label.config(text=f"Entropy: {entropy:.2f} bits")
    time_label.config(text=f"Estimated Crack Time: {crack_time}")


def generate_and_display():
    pwd = generate_password()
    password_var.set(pwd)
    check_strength()


def toggle_password():
    password_entry.config(show="" if show_var.get() else "*")


def generate_qr():
    pwd = password_var.get()

    if not pwd:
        messagebox.showwarning("Error", "Generate a password first")
        return

    qr = qrcode.make(pwd)
    qr_window = tk.Toplevel(root)
    qr_window.title("Password QR Code")

    img = ImageTk.PhotoImage(qr)
    label = tk.Label(qr_window, image=img)
    label.image = img
    label.pack()

    tk.Label(
        qr_window,
        text="⚠ QR codes can be shoulder-surfed. Use carefully.",
        fg="red"
    ).pack(pady=5)

# ------------------ UI Setup ------------------

root = tk.Tk()
root.title("Password Strength Checker")
root.geometry("420x350")

password_var = tk.StringVar()
show_var = tk.BooleanVar()

tk.Label(root, text="Enter Password").pack(pady=5)

password_entry = tk.Entry(root, textvariable=password_var, show="*", width=35)
password_entry.pack()

tk.Checkbutton(
    root,
    text="Show Password",
    variable=show_var,
    command=toggle_password
).pack()

tk.Button(root, text="Check Strength", command=check_strength).pack(pady=5)
tk.Button(root, text="Generate Password", command=generate_and_display).pack(pady=5)
tk.Button(root, text="Generate QR Code", command=generate_qr).pack(pady=5)

result_label = tk.Label(root, text="Strength:")
result_label.pack(pady=5)

entropy_label = tk.Label(root, text="Entropy:")
entropy_label.pack()

time_label = tk.Label(root, text="Estimated Crack Time:")
time_label.pack()

root.mainloop()
