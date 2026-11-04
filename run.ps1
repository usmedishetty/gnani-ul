# PowerShell project task runner for GallaVaani
param(
    [string]$Task = "test"
)

switch ($Task) {
    "test" {
        python -m pytest -q -m "not live"
    }
    "test-live" {
        python -m pytest -q -m "live"
    }
    Default {
        python -m pytest -q -m "not live"
    }
}

