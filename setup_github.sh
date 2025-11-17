#!/bin/bash
# Quick setup script for GitHub repository

echo "JSON Analysis Tool - GitHub Setup"
echo "=================================="

# Add all files to git
echo "Adding files to git..."
git add .

# Commit files
echo "Creating initial commit..."
git commit -m "Initial commit: JSON Analysis Tool with Windows build automation"

echo ""
echo "Next steps:"
echo "1. Go to github.com and create a new repository"
echo "2. Copy the repository URL (e.g., https://github.com/username/json-analysis-tool.git)"
echo "3. Run these commands:"
echo ""
echo "   git remote add origin YOUR_REPO_URL"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "4. Go to your GitHub repository"
echo "5. Click 'Actions' tab"
echo "6. The build will start automatically"
echo "7. Download the .exe from 'Artifacts' when build completes"
echo ""
echo "Repository is ready for GitHub!"