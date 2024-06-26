"""
Runs the My Recipe Flask app from within the myrecipe package.

Sets the host, port, and debug app configurations using the environment variables.
"""

import os
from myrecipe import app

if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT", 5000)),
        # Debug is set to False by default, unless set otherwise, for security.
        debug=bool(os.environ.get("DEBUG", False))
    )
