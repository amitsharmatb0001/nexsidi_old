# fix_tasktype.ps1
# Removes TaskType from all Python files in the project

Write-Host "`n🔍 Finding all files with TaskType..." -ForegroundColor Cyan

cd E:\nexsidi\backend

# Find all Python files with TaskType
$files = Get-ChildItem -Recurse -Include *.py | Where-Object {
    (Get-Content $_.FullName -Raw) -match "TaskType"
}

Write-Host "Found $($files.Count) files with TaskType references`n" -ForegroundColor Yellow

# Show which files will be modified
Write-Host "Files to be fixed:" -ForegroundColor Yellow
foreach ($file in $files) {
    Write-Host "  - $($file.FullName)" -ForegroundColor Gray
}

Write-Host "`n❓ Do you want to fix these files? (Y/N): " -ForegroundColor Yellow -NoNewline
$confirm = Read-Host

if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "❌ Cancelled." -ForegroundColor Red
    exit
}

Write-Host "`n🔧 Fixing files..." -ForegroundColor Cyan

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $originalContent = $content
    
    # Remove TaskType from imports
    $content = $content -replace ',\s*TaskType\s*', ''
    $content = $content -replace '\s*TaskType\s*,', ''
    $content = $content -replace 'import\s+TaskType', ''
    
    # Replace TaskType enum usage with strings
    $content = $content -replace 'TaskType\.CODE_GENERATION', '"code_generation"'
    $content = $content -replace 'TaskType\.CODE_REVIEW', '"code_review"'
    $content = $content -replace 'TaskType\.ANALYSIS', '"analysis"'
    $content = $content -replace 'TaskType\.GENERAL', '"general"'
    $content = $content -replace 'TaskType\.CHAT', '"general"'
    
    # Only save if content changed
    if ($content -ne $originalContent) {
        # Create backup
        $backupPath = "$($file.FullName).backup"
        Copy-Item $file.FullName $backupPath -Force
        
        # Save fixed content
        Set-Content -Path $file.FullName -Value $content -NoNewline
        
        Write-Host "  ✅ Fixed: $($file.Name)" -ForegroundColor Green
        Write-Host "     Backup: $($file.Name).backup" -ForegroundColor Gray
    }
}

Write-Host "`n✅ All files fixed!" -ForegroundColor Green
Write-Host "`n📋 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Test imports: python -c `"from app.agents.base import BaseAgent; print('✅')`"" -ForegroundColor White
Write-Host "  2. Start server: python -m uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "`n💡 Backups created with .backup extension" -ForegroundColor Yellow
