# PowerShell runner for GallaVaani Gnani AI live smoke test
param(
    [string]$VoiceClip,
    [string]$WaClip,
    [string]$Phrase
)

$argsList = @("scripts/smoke_test_gnani.py")
if ($VoiceClip) { $argsList += "--voice-clip"; $argsList += $VoiceClip }
if ($WaClip) { $argsList += "--wa-clip"; $argsList += $WaClip }
if ($Phrase) { $argsList += "--phrase"; $argsList += $Phrase }

python @argsList

