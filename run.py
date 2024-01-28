from myrecipe import app 
import os

if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT", 5000)),
        debug=bool(os.environ.get("DEBUG", True))
    )