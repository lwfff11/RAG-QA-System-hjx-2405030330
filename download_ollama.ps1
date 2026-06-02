# Ollama 自动下载脚本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Ollama 自动下载器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$downloadUrl = "https://ollama.com/download/OllamaSetup.exe"
$outputPath = Join-Path $PSScriptRoot "OllamaSetup.exe"

Write-Host "下载地址: $downloadUrl" -ForegroundColor Yellow
Write-Host "保存位置: $outputPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "正在开始下载..." -ForegroundColor Green
Write-Host ""

try {
    # 使用 BITS 服务下载（更稳定）
    $job = Start-BitsTransfer -Source $downloadUrl -Destination $outputPath -DisplayName "下载 Ollama" -Priority High -Asynchronous
    
    Write-Host "下载进度:" -ForegroundColor Cyan
    
    # 显示进度
    while ($job.JobState -eq "Transferring" -or $job.JobState -eq "Connecting") {
        $job = Get-BitsTransfer -JobId $job.JobId
        $percent = [Math]::Round(($job.BytesTransferred / $job.BytesTotal) * 100, 2)
        $transferredMB = [Math]::Round($job.BytesTransferred / 1MB, 2)
        $totalMB = [Math]::Round($job.BytesTotal / 1MB, 2)
        Write-Host "`r进度: $percent% ($transferredMB MB / $totalMB MB)" -NoNewline -ForegroundColor White
        Start-Sleep -Seconds 1
    }
    
    Complete-BitsTransfer -JobId $job.JobId
    
    Write-Host ""
    Write-Host ""
    Write-Host "✅ 下载完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "安装程序位置: $outputPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "请双击运行 OllamaSetup.exe 进行安装" -ForegroundColor Cyan
    Write-Host ""
    
    # 询问是否立即安装
    $answer = Read-Host "是否立即运行安装程序？(Y/N)"
    if ($answer -eq "Y" -or $answer -eq "y") {
        Start-Process $outputPath
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ 下载失败: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "请尝试手动下载:" -ForegroundColor Yellow
    Write-Host "1. 打开浏览器访问: https://ollama.com/download" -ForegroundColor White
    Write-Host "2. 下载 Windows 版本的安装程序" -ForegroundColor White
    Write-Host ""
}

Write-Host "按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")