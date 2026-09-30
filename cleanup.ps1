Write-Host "Removing Python __pycache__ folders..."
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# Uncomment the next line if you want to delete node_modules (saves space)
# Remove-Item -Recurse -Force .\frontend\node_modules

Write-Host "Deleting old model files (older than 1 hour)..."
Get-ChildItem -Path .\ml\models -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddHours(-1) } | Remove-Item -Force

Write-Host "Cleanup finished."
