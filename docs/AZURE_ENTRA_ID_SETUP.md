# Azure Entra ID App Registration Guide

Follow this guide to provision and configure the Microsoft Entra ID App Registration required for the **MCP M365 Server**.

---

## 1. Automated Provisioning via PowerShell (Recommended)

Run the included automated setup script using the Microsoft.Graph PowerShell module:

```powershell
# In PowerShell 7+ or Windows PowerShell 5.1 with Microsoft.Graph module installed:
.\scripts\setup_entra_app.ps1 -AppName "M365-Governance-MCP-Server"
```

The script will:
1. Connect to Microsoft Graph as Tenant Administrator.
2. Register an application named `M365-Governance-MCP-Server`.
3. Configure the required **Application** permissions.
4. Prompt to grant **Admin Consent** automatically.
5. Generate a client secret and output a starter `config.json` and `.env`.

---

## 2. Manual Provisioning via Microsoft Entra Admin Center

If you prefer to configure the application manually via the Azure Portal:

### Step 1: Register Application
1. Navigate to the [Microsoft Entra Admin Center](https://entra.microsoft.com/) -> **Applications** -> **App registrations**.
2. Click **+ New registration**.
3. Set **Name**: `M365-Governance-MCP-Server`.
4. Set **Supported account types**: `Accounts in this organizational directory only (Single tenant)`.
5. Leave Redirect URI blank.
6. Click **Register**.
7. Note down the **Application (client) ID** and **Directory (tenant) ID**.

### Step 2: Configure Application API Permissions
1. Under **Manage**, select **API permissions** -> **+ Add a permission**.
2. Select **Microsoft Graph** -> **Application permissions** (NOT Delegated).
3. Check the following permissions:
   - `Mail.Send`: Send automated operational notifications.
   - `Mail.ReadWrite`: Access mailbox messages for activity summaries.
   - `MailboxSettings.ReadWrite`: Manage out-of-office auto-replies.
   - `User.Read.All`: Query directory users and organizational profile.
   - `Directory.Read.All`: Query licensing SKUs and tenant configuration.
4. Click **Add permissions**.
5. Click **Grant admin consent for <Your Tenant>** and confirm with **Yes**.

### Step 3: Create Client Secret
1. Under **Manage**, select **Certificates & secrets** -> **Client secrets** tab -> **+ New client secret**.
2. Enter a description (e.g. `MCP Server Secret`) and select an expiration period (e.g. 180 days or 730 days).
3. Click **Add**.
4. **Important**: Immediately copy the **Value** column (the secret value will never be displayed again).

---

## 3. Configuring the MCP Server

Create a `.env` file in the project root:

```ini
M365_TENANT_ID=your-azure-tenant-id-guid
M365_CLIENT_ID=your-entra-app-client-id-guid
M365_CLIENT_SECRET=your-secret-value-string
M365_PRIMARY_ADMIN=admin@yourdomain.com
MCP_LOG_LEVEL=INFO
```

Alternatively, you can provide a `config.json` (ensure it remains excluded from git):

```json
{
  "TenantId": "your-azure-tenant-id-guid",
  "ClientId": "your-entra-app-client-id-guid",
  "ClientSecret": "your-secret-value-string",
  "PrimaryAdmin": "admin@yourdomain.com"
}
```

---

## 4. Verification

Test the authentication pipeline by running:

```bash
python -m unittest discover tests
```

You are now ready to launch the MCP Server in Claude Desktop, Cursor, or any MCP client!
