#!/bin/bash
# Quick update script for Warsaw Hussars cricket statistics

echo "🏏 Warsaw Hussars Cricket Stats - Quick Update"
echo "=============================================="
echo ""

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Generate website
echo "📊 Generating statistics website..."
python generate_website.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Website generated successfully!"
    echo ""
    
    # Check if there are changes to commit
    if [[ -n $(git status -s docs/) ]]; then
        echo "📝 Changes detected in docs/ folder"
        echo ""
        read -p "Commit message (press Enter for default): " commit_msg
        
        if [ -z "$commit_msg" ]; then
            commit_msg="Update cricket statistics - $(date +%Y-%m-%d)"
        fi
        
        echo ""
        echo "Committing changes..."
        git add docs/
        git commit -m "$commit_msg"
        
        echo ""
        read -p "Push to GitHub? (y/n): " push_confirm
        
        if [[ $push_confirm == "y" || $push_confirm == "Y" ]]; then
            echo "Pushing to GitHub..."
            git push
            echo ""
            echo "✅ Done! Your website will update in 1-2 minutes."
            echo "Visit: https://ostyk.github.io/whcc_stats/"
        else
            echo "Skipped push. You can push later with: git push"
        fi
    else
        echo "ℹ️  No changes detected in docs/ folder"
    fi
else
    echo ""
    echo "❌ Error generating website. Check the output above."
    exit 1
fi
