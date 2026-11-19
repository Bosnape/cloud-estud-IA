from fastapi import FastAPI
from codes import encrypt, decrypt

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, this is a secret message!"}


@app.get("/secret")
def read_secret(message: str):
    encrypted = encrypt(message)
    decrypted = decrypt(encrypted)
    return {"encrypted": encrypted, "decrypted": decrypted}