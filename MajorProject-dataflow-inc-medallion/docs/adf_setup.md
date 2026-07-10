# ADF Orchestration

## Why ADF is needed here
Databricks notebooks (01-05) clean/transform data but someone has to run them in the correct order, on a schedule, with failure handling. That "someone" is Azure Data Factory (ADF) — a cloud orchestration service. It doesn't process data itself; it triggers and sequences other services (here, Databricks notebooks) and stops/retries on failure.

## Core concepts

**Pipeline**: a container of activities (steps) that run in a defined order.

**Activity**: a single unit of work inside a pipeline. We use "Databricks Notebook" activities — each one tells ADF "run this specific notebook on this specific cluster."

**Linked Service**: a saved connection profile (like a credential/config bundle) that tells ADF *how* to reach an external system — in our case, which Databricks workspace, which cluster, and which access token to use. Created once, reused by every activity that needs Databricks.

**Dependency condition**: the arrow between two activities. "Succeeded" dependency means Activity B only starts if Activity A completes without error. This is how we enforce Bronze → Silver → Gold → SCD2 → Drift order automatically instead of manually clicking Run on 5 notebooks.

**Trigger**: what starts the pipeline — manual (Debug/Trigger now) or scheduled (e.g. daily at 2 AM).

## What we actually built
`adf_pipeline.json` = one pipeline, 5 activities, each a Databricks Notebook activity, chained with Succeeded dependencies:

```
Bronze_Ingest → Silver_Clean → Gold_Aggregate → SCD2_Merge → Schema_Drift_Check
```

If Bronze fails (e.g. bad CSV), Silver never runs — prevents processing garbage data downstream. That's the entire value of orchestration over manual execution.

## Step-by-step setup

1. **Create the Data Factory resource** — Azure Portal → Create a resource → search "Data Factory" → fill Resource Group, Region, Name → deploy.

2. **Open ADF Studio** — the actual workspace UI where you build pipelines (separate from the Azure Portal page).

3. **Create the Linked Service to Databricks** — Manage tab → Linked services → New → "Azure Databricks Delta Lake".
   - Authentication: Access Token (a Databricks-generated password-like key that lets ADF act on your behalf)
   - Domain: your Databricks workspace URL
   - Cluster choice: this is the compute that will actually execute the notebook code.
     - **Existing Cluster ID** — reuse an already-running cluster (fast, cheap, but requires a persistent interactive cluster, which free/serverless workspaces don't provide)
     - **New Job Cluster** — ADF spins up a temporary cluster just for this pipeline run, then tears it down (what we attempted, since we're on serverless)
   - Access Token: paste the PAT generated in Databricks (Settings → Developer → Access tokens)

4. **Import/build the pipeline** — Author → Pipelines → import `adf_pipeline.json`, or manually drag 5 Notebook activities and connect them with success arrows.

5. **Point each activity at the real notebook path** in your Databricks workspace.

6. **Run it** — Debug (one-time test) or add a Trigger (recurring schedule).

## Author 
Kapil Singhal 
