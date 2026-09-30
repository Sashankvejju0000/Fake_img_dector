Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

function Download-IfNeeded($url, $dest) {
    if (-Not (Test-Path $dest)) {
        Write-Host "Downloading $url ..."
        Invoke-WebRequest -Uri $url -OutFile $dest
    } else {
        Write-Host "$dest already exists - skipping download"
    }
}



# 1️⃣ Ensure Docker Desktop is installed (winget)
if (-Not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker not found – installing via winget..."
    winget install --id Docker.DockerDesktop -e --source winget
    Write-Host "After installation, log out and back in, then re-run this script."
    exit 1
} else {
    Write-Host "Docker is already installed."
}

# 2️⃣ Install latest ngrok (>=3.20.0)
$ngrokDir = "$HOME\ngrok"
$ngrokZip = "$ngrokDir\ngrok.zip"
$ngrokExe = "$ngrokDir\ngrok.exe"
New-Item -ItemType Directory -Force -Path $ngrokDir | Out-Null
Download-IfNeeded "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-windows-amd64.zip" $ngrokZip
Expand-Archive -Path $ngrokZip -DestinationPath $ngrokDir -Force
$env:PATH = "$ngrokDir;$env:PATH"
Write-Host "ngrok version:" ; ngrok version

# 3️⃣ Set ngrok auth token if not configured
if (-Not (Test-Path "$HOME\.ngrok2\ngrok.yml")) {
    $token = Read-Host "Enter your ngrok authtoken"
    ngrok authtoken $token
} else {
    Write-Host "ngrok authtoken already configured."
}

# 4️⃣ Install Nginx for Windows (official zip)
$nginxDir = "C:\Program Files\nginx"
if (-Not (Test-Path "$nginxDir\nginx.exe")) {
    Write-Host "Downloading Nginx..."
    $nginxZip = "$HOME\nginx.zip"
    Download-IfNeeded "https://nginx.org/download/nginx-1.25.5.zip" $nginxZip
    Expand-Archive -Path $nginxZip -DestinationPath $HOME -Force
    Move-Item -Path "$HOME\nginx-1.25.5" -Destination $nginxDir
    Write-Host "Nginx extracted to $nginxDir"
} else {
    Write-Host "Nginx already installed."
}

# 5️⃣ Copy custom nginx.conf into Nginx config folder
$customConf = "C:\Users\spiky\.gemini\antigravity-ide\brain\9f7329b4-c0f6-474a-8208-6794a275bdee\nginx\nginx.conf"
Copy-Item -Force -Path $customConf -Destination "$nginxDir\conf\nginx.conf"

# 6️⃣ Restart Nginx
Write-Host "Restarting Nginx..."
Stop-Process -Name nginx -ErrorAction SilentlyContinue
Start-Process "$nginxDir\nginx.exe"

# 7️⃣ Copy Dockerfile and docker-compose.yml into project root
$projectRoot = "C:\Users\spiky\OneDrive\Desktop\project1\frontend\Fake_img_dector"
Copy-Item -Force -Path "C:\Users\spiky\.gemini\antigravity-ide\brain\9f7329b4-c0f6-474a-8208-6794a275bdee\backend\Dockerfile" -Destination "$projectRoot\backend\Dockerfile"
Copy-Item -Force -Path "C:\Users\spiky\.gemini\antigravity-ide\brain\9f7329b4-c0f6-474a-8208-6794a275bdee\docker-compose.yml" -Destination "$projectRoot\docker-compose.yml"

# 8️⃣ Build and start Docker stack
Write-Host "Building and starting Docker stack..."
Push-Location $projectRoot
docker compose up -d
Pop-Location

# 9️⃣ Give services a moment then start ngrok tunnel on port 80
Start-Sleep -Seconds 5
Write-Host "Starting ngrok tunnel on port 80..."
Start-Process -FilePath "$ngrokExe" -ArgumentList "http 80" -NoNewWindow
Start-Sleep -Seconds 3

# 10️⃣ Retrieve public URL (requires ngrok API, simple way: read from log file)
$logFile = "$HOME\ngrok.log"
if (Test-Path $logFile) {
    $publicUrl = (Select-String -Path $logFile -Pattern 'Forwarding\s+(https://[^\s]+) ->' | Select-Object -First 1).Matches[0].Groups[1].Value
    Write-Host "\n===== NGROK PUBLIC URL ====="
    Write-Host $publicUrl
    Write-Host "============================\n"
} else {
    Write-Host 'ngrok log not found - you can run "ngrok http 80" manually to see the public URL.'
}

# 11️⃣ Run cleanup script (optional)
$cleanup = 'C:\Users\spiky\.gemini\antigravity-ide\brain\9f7329b4-c0f6-474a-8208-6794a275bdee\cleanup.ps1'
if (Test-Path $cleanup) { . $cleanup }

Write-Host 'Setup complete. Use the public URL above in your front-end.'
