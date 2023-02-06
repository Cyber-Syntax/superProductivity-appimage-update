import hashlib
import base64
import yaml
import requests
import json
import subprocess
import re, os
# Written by Cyber-Syntax.
# 6 February 2023 

# Get the version of the latest release
response = requests.get("https://api.github.com/repos/johannesjo/super-productivity/releases/latest")
data = json.loads(response.text)
# Solve, missing "v" problem on the sha256 file.
version = data["tag_name"].replace("v", "")


# Download sha512 and appimage
def get_files():
    print("superProductivity installation started...") 
    try:                   
        # sha512
        url = [asset["browser_download_url"] for asset in data["assets"] if asset["name"] == "latest-linux.yml"][0]
        subprocess.run(["wget", "-q", "-O", "latest-linux.yml", url])
        print("Downloading latest-linux.yml...")
        # appimage
        url = [asset["browser_download_url"] for asset in data["assets"] if asset["name"].endswith(".AppImage")][0]
        subprocess.run(["wget", "-q", "-O", f"superProductivity-{version}.AppImage", url])
        print("Downloading superProductivity Appimage...")
    except:
        print("Unknown error while installing files!")
# Find path for files
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, f"superProductivity-{version}.AppImage")
hash_file = os.path.join(script_dir, "latest-linux.yml")

# open yml file to encode hash
with open(hash_file, "r") as f:
    encoded_hash = yaml.safe_load(f)["sha512"]  

def verify_file(file_path, encoded_hash):
    print("Verifying appimage with sha512")
    
    try:
        # Decode the Base64 encoded hash value
        decoded_hash = base64.b64decode(encoded_hash)
        print("yml file decoding...")
        # Calculate the SHA-512 hash of the file
        sha512 = hashlib.sha512()
        with open(file_path, "rb") as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                sha512.update(data)
        file_hash = sha512.digest()
        
        # Compare the two hash values
        return file_hash == decoded_hash
    except:
        print("Unknown error while verify file!")

def change_name_send_directory():
    print("appimage name changing and moving appimages files")
    try:
        try:
            # Change name for .desktop
            subprocess.run(["mv", f"superProductivity-{version}.AppImage", "superProductivity.AppImage"], check=True)  
        except subprocess.CalledProcessError:        
            print("Error: while changing name! Be sure file names correct.")    
            return

        try:                            
            # Give permission
            subprocess.run(["chmod", "+x", "superProductivity.AppImage"])    
            # Send appimage directory
        except subprocess.CalledProcessError:
            print("Error: while giving permission appimage")
            return

        try:
            pwd = ["pwd"]
            result_pwd = subprocess.run(pwd, capture_output=True) 
            # solve, unknown parameters     
            last = result_pwd.stdout.decode('utf-8')[:-1]                
            subprocess.run(["mv", f"{last}/superProductivity.AppImage", os.path.expanduser("~") + "/Documents/appimages/"])    
            print("Appimage succesfuly installed. It's on the appimages directory.")            
        except subprocess.CalledProcessError:
            print("Error: while moving files to appimages directory")
            return
    except:
        print("Error: While changing name and moving directory!")

def log_version():    
    f = open("superProductivity-version", "a")
    f.write(f"{version}\n")
    f.close()

    f = open("superProductivity-version", "r")
    print(f.read(), "The version is logged.")
    
    try:
        pwd = ["pwd"]
        result_pwd = subprocess.run(pwd, capture_output=True) 
        # solve, unknown parameters     
        last = result_pwd.stdout.decode('utf-8')[:-1]                
        subprocess.run(["mv", f"{last}/superProductivity-version", os.path.expanduser("~") + "/Documents/appimages/"])    
        print("Appimage version successfully logged.")            
    except subprocess.CalledProcessError:
        print("Error: while moving files to appimages directory")
        return                

def main():
    get_files()    
    result = verify_file(file_path, encoded_hash)  
        
    if result:  
        print("superProductivity verified successfully")
        # Delete sha file.   
        subprocess.run(["rm", "latest-linux.yml"])        
    else:
        print("File corrupted! Try to restart script.")        
    
    change_name_send_directory()
    log_version()

if __name__ == "__main__":
    main()
