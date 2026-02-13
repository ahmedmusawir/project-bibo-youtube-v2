#!/bin/bash

   PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
   echo "Project: $PROJECT_ID"
   echo "========================================"
   echo

   echo "1. Checking Vertex AI API status..."
   gcloud services list --enabled --filter="name:aiplatform.googleapis.com" --project=$PROJECT_ID
   echo

   echo "2. Listing all Vertex AI quotas (filtering for 'anthropic' and 'claude')..."
   gcloud compute regions list --project=$PROJECT_ID 2>/dev/null | head -5
   echo

   echo "3. Checking quotas for us-east5 region..."
   gcloud alpha compute regions describe us-east5 --project=$PROJECT_ID 2>/dev/null | grep -i quota | head -10
   echo

   echo "4. Alternative: Using quota API to find Claude quotas..."
   echo "Searching for Anthropic/Claude related quotas..."
   gcloud alpha quotas list --service=aiplatform.googleapis.com --project=$PROJECT_ID 2>/dev/null | grep -i
   "anthropic\|claude" | head -20
