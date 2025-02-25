$scriptPath = "C:\terminal-data-editor\main.py"

$fooJSONFile = "C:\terminal-data-editor\data_files\foo.json"

$process = Start-Process -NoNewWindow -PassThru -FilePath "python" -ArgumentList "$scriptPath $fooJSONFile"

Start-Sleep -Seconds 1 

$pipeName = "ForminalPipe"
$pipePath = "\\.\pipe\$pipeName"

$commands = @(
    "cd users/0/id",
    "append 2",
    "uncast .",
    "append 2",
    "cast .",
    "cd .. .. 1/name",
    "del-val .",
    "cd ../preferences",
    "del-key theme",
    "del-val False",
    "cd ../.. ..",
    "append {'test': [1, 2, 'testing_']}",
    "save",
    "append {'will be undone': 'yes'}",
    "restore",
    "append {'will not be undone': 'yes'}",
    "save",
    "exit"
)

foreach($cmd in $commands) {
    Add-Content -Path $pipePath -Value "$cmd`n"
    Start-Sleep -Milliseconds 500 
}

$process | Wait-Process

$output = Get-Content -Path $pipePath
Write "$output"

<#
$expected = @(

)

if ($output -match $expected) {
    Write-Host "✅ Test succeded."
} else {
    Write-Host "❌ Test failed."
    Write-Host "Program output:"
    Write-Host "$output"
}

if (!(process.HasExited)) {
  Stop-Process -Id $process.Id -Force
}
#>
