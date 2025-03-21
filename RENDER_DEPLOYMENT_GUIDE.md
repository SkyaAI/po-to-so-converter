# Render Deployment Guide for PO to SO Converter

This guide will help you deploy your Purchase Order to Sales Order Conversion System as a permanent website using Render.

## Prerequisites

1. A GitHub account (free)
2. A Render account (free, sign up at https://render.com)

## Step 1: Update Your GitHub Repository

1. Go to your GitHub repository (SkyaAI/po-to-so-converter)
2. Add the following new files:
   - `Dockerfile` (I've provided this)
   - `render.yaml` (I've provided this)
3. Make sure all your application files are present:
   - `app.py`
   - `document_parser.py`
   - `data_extractor.py`
   - `sales_order_generator.py`
   - `csv_exporter.py`
   - `requirements.txt`

## Step 2: Sign Up for Render

1. Go to [Render](https://render.com) and sign up for a free account
2. You can sign up using your GitHub account for easier integration

## Step 3: Deploy on Render

### Option 1: Deploy via Blueprint (Recommended)

1. In your Render dashboard, click "New" and select "Blueprint"
2. Connect your GitHub repository (SkyaAI/po-to-so-converter)
3. Render will automatically detect the `render.yaml` file and configure your service
4. Click "Apply Blueprint"
5. Wait for the deployment to complete (this may take a few minutes)

### Option 2: Deploy as a Web Service

If the Blueprint option doesn't work:

1. In your Render dashboard, click "New" and select "Web Service"
2. Connect your GitHub repository (SkyaAI/po-to-so-converter)
3. Configure the service:
   - Name: po-to-so-converter
   - Environment: Docker
   - Branch: main
   - Build Command: `docker build -t po-to-so-converter .`
   - Start Command: `docker run -p 8501:8501 po-to-so-converter`
4. Click "Create Web Service"
5. Wait for the deployment to complete

## Step 4: Access Your Application

Once deployment is complete, Render will provide you with a URL to access your application (e.g., https://po-to-so-converter.onrender.com).

## Step 5: Embed in Squarespace

1. Log in to your Squarespace account and go to the page where you want to embed the app
2. Add a new "Code" block (in the Squarespace editor)
3. Paste the following HTML code, replacing `YOUR_RENDER_URL` with your actual Render app URL:

```html
<iframe
  src="YOUR_RENDER_URL"
  height="800"
  width="100%"
  style="border: none; border-radius: 4px; overflow: hidden;"
  allow="camera;microphone"
></iframe>
```

4. Save your changes

## Troubleshooting

- If you encounter errors during deployment, check the Render logs
- If the iframe appears too small on your Squarespace site, adjust the `height` value in the HTML code
- If you need to update your application, simply push changes to your GitHub repository and Render will automatically redeploy

## Maintaining Your Deployment

Your application will remain permanently deployed on Render. The free tier includes:
- 750 hours of runtime per month
- Automatic HTTPS
- Automatic deployments when you push to GitHub

For production use with higher traffic, you may want to upgrade to a paid plan in the future.
