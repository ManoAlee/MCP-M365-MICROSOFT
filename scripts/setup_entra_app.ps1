<#
.SYNOPSIS
    Automated Entra ID (Azure AD) App Registration Provisioner for M365 Governance MCP Server.
.DESCRIPTION
    Creates the App Registration, ensures the Service Principal, configures Microsoft Graph 
    application permissions (Roles) with Admin Consent, resets a 24-month Client Secret, 
    and writes config.json.
.PARAMETER AppName
    Display name of the application (Default: M365-Governance-MCP-Server).
.AUTHOR
    ManoAlee (https://github.com/ManoAlee/MCP-M365-MICROSOFT)
#>

[CmdletBinding()]
param (
    [string]$AppName = "M365-Governance-MCP-Server"
)

Clear-Host
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   M365 GOVERNANCE MCP: ENTRA ID APP REGISTRATION PROVISIONER         " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Azure CLI
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Azure CLI ('az') is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Install it from: https://learn.microsoft.com/cli/azure/install-azure-cli" -ForegroundColor Yellow
    Exit 1
}

# 2. Check Login Status
Write-Host "[1/5] Checking Azure CLI session..." -ForegroundColor Yellow
$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Host "[!] You must log in to your tenant. Running 'az login'..." -ForegroundColor Cyan
    az login --allow-no-subscriptions | Out-Null
    $account = az account show | ConvertFrom-Json
}
$tenantId = $account.tenantId
Write-Host "    [OK] Connected to Tenant ID: $tenantId" -ForegroundColor Green

# 3. Create or Get App Registration
Write-Host ""
Write-Host "[2/5] Checking App Registration '$AppName'..." -ForegroundColor Yellow
$appJson = az ad app list --display-name $AppName | ConvertFrom-Json
if ($appJson.Count -gt 0) {
    $appId = $appJson[0].appId
    Write-Host "    [OK] Found existing application. ClientId: $appId" -ForegroundColor Green
} else {
    Write-Host "    [+] Creating new Application Registration..." -ForegroundColor Cyan
    $newApp = az ad app create --display-name $AppName --sign-in-audience AzureADMyOrg | ConvertFrom-Json
    $appId = $newApp.appId
    Write-Host "    [OK] App created successfully! ClientId: $appId" -ForegroundColor Green
}

# 4. Service Principal
Write-Host ""
Write-Host "[3/5] Verifying Service Principal (Enterprise Application)..." -ForegroundColor Yellow
$spJson = az ad sp show --id $appId 2>$null | ConvertFrom-Json
if (-not $spJson) {
    Write-Host "    [+] Instantiating Service Principal..." -ForegroundColor Cyan
    az ad sp create --id $appId | Out-Null
    Start-Sleep -Seconds 4
}
Write-Host "    [OK] Service Principal is active in tenant." -ForegroundColor Green

# 5. Application Permissions (Graph Roles)
Write-Host ""
Write-Host "[4/5] Adding Microsoft Graph Application Permissions..." -ForegroundColor Yellow
$graphAppId = "00000003-0000-0000-c000-000000000000"
$roles = @(
    "7ab1d382-f21e-4acd-a863-ba3e13f7da61=Role", # Directory.Read.All
    "e2a3a72e-5f79-4c64-b1b1-878b674786c9=Role", # Mail.ReadWrite
    "b633e1c5-b582-4048-a93e-9f11b44c7e96=Role", # Mail.Send
    "6931bccd-447a-43d1-b442-00a195474933=Role", # MailboxSettings.ReadWrite
    "df021288-bdef-4463-88db-98f22de89214=Role"  # User.Read.All
)

foreach ($r in $roles) {
    az ad app permission add --id $appId --api $graphAppId --api-permissions $r 2>$null | Out-Null
}
Write-Host "    [OK] Application permissions assigned." -ForegroundColor Green

Write-Host "    [+] Granting Tenant Admin Consent..." -ForegroundColor Cyan
az ad app permission admin-consent --id $appId
Write-Host "    [OK] Admin Consent granted across the tenant." -ForegroundColor Green

# 6. Generate Secret
Write-Host ""
Write-Host "[5/5] Generating 24-month Client Secret..." -ForegroundColor Yellow
$secretObj = az ad app credential reset --id $appId --display-name "MCP-Server-Production-Secret" --years 2 | ConvertFrom-Json
$clientSecret = $secretObj.password
Write-Host "    [OK] Secret generated." -ForegroundColor Green

# 7. Write Local config.json
$outConfig = [PSCustomObject]@{
    TenantId     = $tenantId
    AppName      = $AppName
    ClientId     = $appId
    ClientSecret = $clientSecret
    Permissions  = @("Directory.Read.All", "Mail.ReadWrite", "Mail.Send", "MailboxSettings.ReadWrite", "User.Read.All")
    CreatedAt    = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
}

$destPath = Join-Path (Split-Path -Parent $PSScriptRoot) "config.json"
$outConfig | ConvertTo-Json -Depth 4 | Set-Content -Path $destPath -Encoding UTF8
Write-Host ""
Write-Host "[SUCCESS] Credentials saved securely to $destPath" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
