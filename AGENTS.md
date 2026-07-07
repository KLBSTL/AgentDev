# AgentDev Agent Defaults

## Default Python Environment

- For Python, PyTorch, Transformers, Hugging Face, local LLM, or GPU-related commands, prefer the `DL` conda environment by default.
- Use the direct interpreter path when possible:

```powershell
& E:\Anaconda\envs\DL\python.exe <script.py>
```

- Before diagnosing model/runtime issues, check with:

```powershell
& E:\Anaconda\envs\DL\python.exe -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

## Default Network Proxy

- When network access, Hugging Face downloads, package downloads, API calls, or model downloads are slow or failing, first try the local proxy:

```powershell
$env:HTTP_PROXY="http://127.0.0.1:7892"
$env:HTTPS_PROXY="http://127.0.0.1:7892"
```

- For Hugging Face model downloads, prefer the proxy and, when useful, the mirror:

```powershell
$env:HF_ENDPOINT="https://hf-mirror.com"
```

## Command Output

- Keep command output concise by default. For long downloads, training, tests, or model runs, write verbose output to log files and inspect only tails, file sizes, progress summaries, and final errors.
