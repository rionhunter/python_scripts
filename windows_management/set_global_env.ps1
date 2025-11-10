    # Set‑GlobalEnvVar.ps1
    #
    # Prompts for a name and value, then sets that environment variable
    # in the Machine (system‑wide) scope.  Must be run as Administrator.

    $varName  = Read-Host 'Enter environment variable name'
    $varValue = Read-Host "Enter value for `$varName"

    try {
        [System.Environment]::SetEnvironmentVariable($varName, $varValue, 'Machine')
        Write-Host "✅ Machine‑level environment variable '$varName' set to '$varValue'."
    }
    catch {
        Write-Error "❌ Failed to set Machine‑level environment variable. $_"
    }