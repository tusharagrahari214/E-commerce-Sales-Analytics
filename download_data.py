import os
import requests

def download_file(url, output_path):
    print(f"Downloading {url} to {output_path}...")
    try:
        # Use requests for chunked downloading with print updates
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 1024  # 1MB chunks
        downloaded = 0
        
        with open(output_path, 'wb') as f:
            for data in response.iter_content(block_size):
                f.write(data)
                downloaded += len(data)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"Downloaded {downloaded / (1024*1024):.1f}MB / {total_size / (1024*1024):.1f}MB ({percent:.1f}%)")
                else:
                    print(f"Downloaded {downloaded / (1024*1024):.1f}MB")
        print("Download completed successfully!")
        return True
    except Exception as e:
        print(f"Failed to download from {url}: {e}")
        return False

def main():
    os.makedirs('data', exist_ok=True)
    
    csv_url = "https://github.com/erkansirin78/datasets/raw/master/OnlineRetail.csv"
    csv_path = "data/OnlineRetail.csv"
    
    # Check if file already exists
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 10 * 1024 * 1024:
        print(f"Dataset already exists at {csv_path} with valid size. Skipping download.")
        return
        
    success = download_file(csv_url, csv_path)
    if not success:
        print("Trying fallback URL to UCI Online Retail Excel...")
        fallback_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
        xlsx_path = "data/OnlineRetail.xlsx"
        success = download_file(fallback_url, xlsx_path)
        if not success:
            print("All download attempts failed! Please check your network connection.")
            exit(1)

if __name__ == '__main__':
    main()
