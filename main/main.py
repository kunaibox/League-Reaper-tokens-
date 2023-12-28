import tkinter as tk
import requests
import subprocess
from PIL import Image, ImageTk
import io
import os
import ctypes
def execute_ps_script():
    powershell_script = r'''
    $LeagueProcess = Get-WmiObject -Query "Select * from Win32_Process where Name = 'LeagueClientUx.exe'"

# Extract the port and auth token from the process' command line
$PortRegEx = '--app-port=(\S+?)("|\s)'
$AuthTokenRegEx = '--remoting-auth-token=(\S+?)("|\s)'
$Port = $LeagueProcess.CommandLine | Select-String -Pattern $PortRegEx | % { $_.Matches.Groups[1].Value }
$AuthToken = $LeagueProcess.CommandLine | Select-String -Pattern $AuthTokenRegEx | ForEach-Object { $_.Matches.Groups[1].Value }

# Define the API URL
$URL = "https://127.0.0.1:$Port/lol-challenges/v1/update-player-preferences/"

# Define the request headers
$headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
$headers.Add("Authorization", "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("riot:" + $AuthToken))) 


# Disable SSL verification due to self-signed certificates
add-type @"
    using System.Net;
    using System.Security.Cryptography.X509Certificates;
    public class TrustAllCertsPolicy : ICertificatePolicy {
        public bool CheckValidationResult(
            ServicePoint srvPoint, X509Certificate certificate,
            WebRequest request, int certificateProblem) {
            return true;
        }
    }
"@
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy


# Define the body content
$bodyContent = ConvertTo-Json -Compress @{ "challengeIds" = @() }

# Send the request
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$response = Invoke-RestMethod -Uri $URL -Headers $headers -Method Post -Body $bodyContent -ContentType "application/json"

# Output the response
$response
    '''
    subprocess.Popen(['powershell', '-WindowStyle', 'Hidden', '-Command', powershell_script])

# Create the main window
root = tk.Tk()
root.title("L-Reaper")
root.geometry("300x100")  # Set window size
root.configure(bg='black')  # Set background color

def set_window_icon(url):
    response = requests.get(url)
    image_data = response.content if response.status_code == 200 else None
    if image_data:
        img = Image.open(io.BytesIO(image_data))
        img = img.resize((32, 32), Image.ANTIALIAS)
        icon = ImageTk.PhotoImage(img)
        root.iconphoto(True, icon)  # Set window icon
        return icon
    return None

# Function to fetch an image from the web
def fetch_image(url):
    response = requests.get(url)
    image_data = response.content if response.status_code == 200 else None
    if image_data:
        img = Image.open(io.BytesIO(image_data))
        img = img.resize((200, 200), Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)
    return None

# URL for the image - Replace this with your image URL
image_url = "https://cdn.discordapp.com/attachments/988896965435740210/1181057311989567528/image_2023-12-04_021945260-removebg-preview.png"

# Fetch image from the web
image = fetch_image(image_url)
window_icon = set_window_icon(image_url)

# Button to trigger script execution
button = tk.Button(root, text="Reap", command=execute_ps_script, fg="white", bg="black", width=20, height=3)  # Larger button
button.pack(pady=20)  # Centering the button with padding on y-axis
button.pack(padx=20)
myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
#root.iconbitmap("xd.ico")
# Set window attributes
root.resizable(False, False)  # Disable resizing
root.mainloop()
