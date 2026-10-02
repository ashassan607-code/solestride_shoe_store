# Deploying SoleStep to Azure (Phase 5: Deployment)

Target: **Azure App Service for Containers** (Linux, single container) —
the standard low-effort path for a small containerized app like this MVP.
Run these from your own machine (this repo's Dockerfile builds a container
that needs `docker` + `az` locally, or the GitHub Actions workflow below).

## 0. Prerequisites

- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed, then `az login`
- Docker installed and running
- This repo cloned locally (via `git clone`, or `git push` from the extracted project — not uploaded as a zip through the GitHub web UI)

## 1. Create the resource group and container registry

```bash
az group create --name solestep-rg --location eastus

az acr create --resource-group solestep-rg \
  --name solestepacr --sku Basic --admin-enabled true
```

`solestepacr` must be globally unique — change it if Azure rejects it.

## 2. Build and push the image

```bash
az acr login --name solestepacr

docker build -t solestepacr.azurecr.io/solestep:latest .
docker push solestepacr.azurecr.io/solestep:latest
```

## 3. Create the App Service plan and Web App

```bash
az appservice plan create --name solestep-plan \
  --resource-group solestep-rg --is-linux --sku B1

az webapp create --resource-group solestep-rg \
  --plan solestep-plan --name solestep-app \
  --deployment-container-image-name solestepacr.azurecr.io/solestep:latest
```

`solestep-app` becomes part of your live URL
(`https://solestep-app.azurewebsites.net`) — must also be globally unique.

## 4. Connect the Web App to the registry and set the port

```bash
# Give the Web App the ACR admin credentials so it can pull the image
ACR_USER=$(az acr credential show --name solestepacr --query username -o tsv)
ACR_PASS=$(az acr credential show --name solestepacr --query "passwords[0].value" -o tsv)

az webapp config container set --name solestep-app \
  --resource-group solestep-rg \
  --container-image-name solestepacr.azurecr.io/solestep:latest \
  --container-registry-url https://solestepacr.azurecr.io \
  --container-registry-user $ACR_USER \
  --container-registry-password $ACR_PASS

# Tell App Service which port the container listens on (matches Dockerfile's EXPOSE 8000)
az webapp config appsettings set --resource-group solestep-rg \
  --name solestep-app --settings WEBSITES_PORT=8000
```

## 5. Verify it's live

```bash
az webapp restart --name solestep-app --resource-group solestep-rg
```

Visit `https://solestep-app.azurewebsites.net` — you should land on the
SoleStep login screen with the logo. Sign in with a demo account (see
README) to confirm browse → cart → checkout and the seller dashboard
both work.

## 6. Optional: auto-deploy on every push (CI/CD)

`.github/workflows/deploy-azure.yml` is already in this repo. To activate it:

1. In the Azure Portal, open your Web App → **Deployment Center** →
   **Manage publish profile** → download it.
2. In GitHub: repo → **Settings → Secrets and variables → Actions**, add:
   - `ACR_LOGIN_SERVER` = `solestepacr.azurecr.io`
   - `ACR_USERNAME` / `ACR_PASSWORD` = the values from step 4 above
   - `AZURE_WEBAPP_NAME` = `solestep-app`
   - `AZURE_WEBAPP_PUBLISH_PROFILE` = contents of the file from step 1
3. Push to `main` — the workflow builds the image, pushes it to ACR, and
   redeploys the Web App automatically.

**Important:** if you set up the Web App through the Azure Portal's
Deployment Center UI instead of the CLI steps above, double-check its
"Source" is set to a container/Docker build, not "Code" with a Node.js
runtime — Azure can auto-detect the wrong stack and generate its own
conflicting workflow (`actions/setup-node`) that fails because there's
no `package.json` in a Python project.

## Known limitation carried from Phase 4

SQLite (`store.db`) lives on the container's local disk, which Azure App
Service does **not** guarantee persists across restarts or scale-outs.
Fine for this MVP demo; the production-ready follow-up is either
**Azure Database for PostgreSQL** (swap the connection in `db.py` /
`repositories.py` only — the service layer doesn't change, per the
Phase 2 design) or an **Azure Files** mount for the SQLite file.
