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

$output = [string]::Concat("executing with: ", (Get-Alias pythonPath).Definition, "`npython refers to the standard python installation or the current aktiv venv")
Write-Output $output

$startDir = Get-Location

# build the python package
Set-Location $PSScriptRoot
Write-Host "Building package" -ForegroundColor Green

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

Set-Location $PSScriptRoot
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


Write-Host "Successfully updated lcapy package in Pyodide distribution" -ForegroundColor Green
Set-Location $startDir