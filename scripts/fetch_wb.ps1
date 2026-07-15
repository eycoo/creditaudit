# Ambil data mentah World Bank (Indonesia) untuk benchmark uji F2-01.
# Network di-sandbox di harness; jalankan manual:
#   pwsh -File scripts/fetch_wb.ps1
# Menyimpan JSON mentah eksak ke data/raw/wb_<code>.json (gitignored).
# Lalu: python scripts/curate_benchmark_uji.py
$out = Join-Path $PSScriptRoot "../data/raw"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$codes = @(
 "SH.DYN.MORT","SP.DYN.IMRT.IN","SP.DYN.LE00.IN","SH.STA.MMRT","SH.IMM.MEAS",
 "SH.IMM.IDPT","SH.TBS.INCD","SH.DYN.NMRT","SH.XPD.CHEX.GD.ZS",
 "AG.PRD.FOOD.XD","AG.PRD.CROP.XD","AG.YLD.CREL.KG","NV.AGR.TOTL.ZS","AG.LND.AGRI.ZS",
 "FP.CPI.TOTL.ZG","FP.CPI.TOTL","AG.LND.ARBL.ZS","SL.AGR.EMPL.ZS"
)
foreach ($c in $codes) {
  $f = Join-Path $out "wb_$c.json"
  if ((Test-Path $f) -and (Get-Item $f).Length -gt 200) { "SKIP $c (cached)"; continue }
  $u = "https://api.worldbank.org/v2/country/IDN/indicator/$c`?format=json&per_page=300&date=1970:2024"
  $done = $false
  for ($try = 1; $try -le 3 -and -not $done; $try++) {
    try {
      $r = Invoke-WebRequest -Uri $u -TimeoutSec 60 -UseBasicParsing
      [IO.File]::WriteAllText($f, $r.Content)
      $j = $r.Content | ConvertFrom-Json
      $n = ($j[1] | Where-Object { $_.value -ne $null } | Measure-Object).Count
      "OK $c : $n pts"; $done = $true
    } catch { Start-Sleep -Seconds 2 }
  }
  if (-not $done) { "FAIL $c" }
}
"=== DONE ==="
