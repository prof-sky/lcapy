param (
[string]$pythonPath
)
if($pythonPath){
    Set-Alias pythonPath $pythonPath
    $pytestFolder = Split-Path -Path $pythonPath
    $pytestPath = Join-Path -Path $pytestFolder -ChildPath "pytest.exe"
    Set-Alias pytest $pytestPath
}
else{
    Set-Alias pythonPath python
    Set-Alias pytest pytest
}

function adjustAndMoveSolvePy{

    $content = Get-Content -Path "NonLcapyFiles\solve.py"

    $versionLine = [string]::Concat("# for lcapy version: ", $version, "`r`n")
    $line1 = "import warnings`r`n"
    $line2 = "warnings.filterwarnings('ignore')`r`n"
    $content = $versionLine + $line1 + $line2 + ($content -join "`r`n")
    Set-Content -Path "..\Pyodide\solve.py" -Value $content

    Write-Output "Copied solve.py to: ..\Pyodide\"
}

function adjustAndMoveGenerateSVGFilesPy{
    $content = Get-Content -Path "NonLcapyFiles\generateSVGFiles.py"

    $versionLine = [string]::Concat("# for lcapy version: ", $version, "`r`n")
    $content = $versionLine + ($content -join "`r`n")
    Set-Content -Path "..\Pyodide\Scripts\generateSVGFiles.py" -Value $content

    Write-Output "Copied generateSVGFiles.py to: ..\Pyodide\Scripts"
}

$output = [string]::Concat("executing with: ", (Get-Alias pythonPath).Definition, "`npython refers to the standard python installation or the current aktiv venv")
Write-Output $output

$startDir = Get-Location

# Make sure the tests pass before building the Package
Write-Host "Execute base lcapy tests" -ForegroundColor Green
Start-Sleep -Milliseconds 200
Set-Location $PSScriptRoot/lcapy/tests
pytest -n 8

if ($LASTEXITCODE -ne 0)
{
    Write-Host "An error occured while executing lcapy-inskale tests" -ForegroundColor Red
    Set-Location $startDir
    return
}


Write-Host "Execute lcapy-inskale tests" -ForegroundColor Green
Start-Sleep -Milliseconds 200
Set-Location $PSScriptRoot/NonLcapyFiles/tests
pytest

if ($LASTEXITCODE -ne 0)
{
    Write-Host "An error occured while executing lcapy-inskale tests" -ForegroundColor Red
    Set-Location $startDir
    return
}

# build the python package
Set-Location $PSScriptRoot
Write-Host "Building package" -ForegroundColor Green
Start-Sleep -Milliseconds 1000

try{
    pythonPath setup.py sdist bdist_wheel
}
catch{
    Write-Host "An error occured while building the package" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Set-Location $startDir
    return
}

Set-Location $PSScriptRoot
$version = pythonPath setup.py --version

try{
    adjustAndMoveSolvePy
}
catch{
    Write-Host "An error occured while handling solve.py" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Set-Location $startDir
    return
}

try{
    adjustAndMoveGenerateSVGFilesPy
}
catch{
    Write-Host "An error occured while handling GenerateSVGFiles.py" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Set-Location $startDir
    return
}


Set-Location $PSScriptRoot
Write-Host "Successfully tested and build package" -ForegroundColor Green
Write-Host ([string]::Concat("Version is: ", $version)) -ForegroundColor Green

$oldPackages = Get-ChildItem -Path "..\Pyodide\Packages" -Filter "*lcapy*" -Recurse
foreach($item in $oldPackages){
    $path = [string]::Concat("..\Pyodide\Packages\", $item)
    Remove-Item -Path $path
    Write-Output ([string]::Concat("Removed: ", $path))
}

try{
    $newPackage = Get-ChildItem -Path "dist" -Filter "*.whl" -File | Sort-Object -Property LastWriteTime -Descending | Select-Object -First 1
}
catch {
    Write-Host "couldn't find new package in .\dist" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Set-Location $startDir
    return
}


try{
    Copy-Item -Path ([string]::Concat("dist\", $newPackage)) -Destination "..\Pyodide\Packages\"
}
catch {
    Write-Host "could not copy new package" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Set-Location $startDir
    return
}
Write-Output ([string]::Concat("Copied ", $newPackage, " to: ..\Pyodide\Packages\"))


Write-Host "Successfully updated solve.py, generateSVGFiles.py and lcapy package in Pyodide distribution" -ForegroundColor Green
Set-Location $startDir