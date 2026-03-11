import sys
sys.path.append('.')
from app import app

def test_app():
    assert app is not None
    print("✅ App loads successfully")
    
if __name__ == '__main__':
    test_app()
