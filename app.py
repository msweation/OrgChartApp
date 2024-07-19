from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    print(f"Templates directory: {os.path.join(os.getcwd(), 'templates')}")
    print(f"Static directory: {os.path.join(os.getcwd(), 'static')}")
    app.run(debug=True)
