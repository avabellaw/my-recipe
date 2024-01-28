import os

os.environ.setdefault("IP", "0.0.0.0")
os.environ.setdefault("PORT", "5000")
os.environ.setdefault("SECRET_KEY", "TheBigSecretKey")
os.environ.setdefault("DEBUG", "TRUE")
os.environ.setdefault("DEVELOPMENT", "TRUE")
os.environ.setdefault("DB_URL", "postgresql://postgres@localhost:5432/taskmanager")