#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataFair Project Cleanup Script
Entfernt redundante und leere Dateien
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Bereinige das DataFair Projekt"""
    
    print("🧹 DataFair Project Cleanup Starting...")
    print("=" * 50)
    
    # Files to delete (redundant/empty)
    files_to_delete = [
        "backend/app_minimal.py",
        "backend/run.py", 
        "backend/seed_database.py",
        "backend/app/auth.py",
        "frontend/assets/js/app.js",
        "frontend/assets/css/test..css",
        "frontend/assets/css/main.css",
        "frontend/assets/css/components.css",
        "backend/app/routes/enterprise_routes.py",
        "backend/app/routes/payment_routes.py",
        "backend/app/utils/decorators.py"
    ]
    
    # Empty directories to check
    dirs_to_check = [
        "backend/app/utils",
        "legal",
        "docs"
    ]
    
    deleted_count = 0
    kept_count = 0
    
    # Delete redundant files
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            try:
                # Check if file is actually empty or redundant
                if should_delete_file(file_path):
                    os.remove(file_path)
                    print(f"❌ Deleted: {file_path}")
                    deleted_count += 1
                else:
                    print(f"⚠️  Kept (has content): {file_path}")
                    kept_count += 1
            except Exception as e:
                print(f"🚫 Error deleting {file_path}: {e}")
        else:
            print(f"🔍 Not found: {file_path}")
    
    # Clean up empty directories
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            try:
                # Check if directory is empty or only contains empty files
                if is_directory_empty_or_useless(dir_path):
                    shutil.rmtree(dir_path)
                    print(f"📁 Removed empty directory: {dir_path}")
                    deleted_count += 1
                else:
                    print(f"📁 Kept (has useful content): {dir_path}")
                    kept_count += 1
            except Exception as e:
                print(f"🚫 Error removing directory {dir_path}: {e}")
    
    # Clean up __pycache__ directories
    print("\n🗑️  Cleaning Python cache files...")
    cache_cleaned = clean_pycache()
    
    print("\n" + "=" * 50)
    print("✅ Cleanup completed!")
    print(f"❌ {deleted_count} files/directories removed")
    print(f"✅ {kept_count} files kept (non-empty)")
    print(f"🗑️  {cache_cleaned} cache directories cleaned")
    
    print("\n📋 Project structure is now cleaner!")
    print("🚀 You can now restart your application.")

def should_delete_file(file_path):
    """Check if a file should be deleted"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # File is empty
        if not content:
            return True
        
        # File only has comments or minimal content
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        content_lines = [line for line in lines if not line.startswith(('#', '//', '/*', '*', '"""', "'''"))]
        
        # Only comments or very minimal content
        if len(content_lines) <= 2:
            return True
            
        # Specific patterns for redundant files
        if 'console.log' in content and len(content_lines) == 1:
            return True  # Only console.log
            
        return False
        
    except Exception:
        return False  # Keep file if we can't read it

def is_directory_empty_or_useless(dir_path):
    """Check if directory is empty or only contains useless files"""
    try:
        items = os.listdir(dir_path)
        
        if not items:
            return True  # Completely empty
        
        # Check if all files are empty or useless
        for item in items:
            item_path = os.path.join(dir_path, item)
            if os.path.isfile(item_path):
                if not should_delete_file(item_path):
                    return False  # Has useful file
            elif os.path.isdir(item_path):
                if not is_directory_empty_or_useless(item_path):
                    return False  # Has useful subdirectory
        
        return True  # All files are useless
        
    except Exception:
        return False  # Keep if we can't check

def clean_pycache():
    """Remove all __pycache__ directories"""
    count = 0
    for root, dirs, files in os.walk("."):
        for dir_name in dirs[:]:  # Copy list to modify during iteration
            if dir_name == '__pycache__':
                pycache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(pycache_path)
                    count += 1
                    dirs.remove(dir_name)  # Don't traverse into deleted directory
                except Exception as e:
                    print(f"🚫 Error removing {pycache_path}: {e}")
    return count

if __name__ == '__main__':
    # Ask for confirmation
    print("🧹 DataFair Project Cleanup")
    print("This will remove redundant and empty files.")
    print("Make sure you have a backup if needed!")
    
    response = input("\n⚠️  Continue with cleanup? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        cleanup_project()
    else:
        print("🚫 Cleanup cancelled.")