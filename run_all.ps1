Write-Host "Running Extraction Eval..."
python -m eval.run_extraction_eval --limit 2
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`nRunning Cost Latency Eval..."
python -m eval.run_cost_latency_eval --limit 2
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`nRunning Ablation Eval..."
python -m eval.run_ablation --limit 2
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`nRunning Quantization Eval..."
python -m eval.run_quantization_eval --limit 2
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`nRunning Code Eval..."
python -m eval.run_code_eval
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`nAll evaluations completed successfully!"
