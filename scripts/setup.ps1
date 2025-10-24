python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

npm install

pre-commit install

Write-Host "Setup complete. Activate venv with .\\.venv\\Scripts\\Activate.ps1"
