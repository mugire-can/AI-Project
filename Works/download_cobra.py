import requests
import os

def download_cobra_image():
    """Download a king cobra image from Unsplash API"""
    
    # Using Unsplash's public API (no key needed for basic source endpoint)
    url = "https://source.unsplash.com/800x600/?king-cobra,snake"
    
    print("Downloading king cobra image...")
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            filename = "king_cobra.jpg"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Image downloaded successfully: {filename}")
            print(f"✓ File size: {len(response.content) / 1024:.2f} KB")
            print(f"✓ Saved to: {os.path.abspath(filename)}")
            return filename
        else:
            print(f"✗ Failed to download. Status code: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error downloading image: {e}")
        return None

if __name__ == "__main__":
    download_cobra_image()
