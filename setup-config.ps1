# 激活 Windows 版 skillshare 配置
$here = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Definition }
Copy-Item (Join-Path $here 'config.windows.yaml') (Join-Path $here 'config.yaml') -Force
Write-Host "Activated config.windows.yaml -> config.yaml"
