# link-skills.ps1 - link every skill in this registry into the agents' skill folders (Windows).
# Flattens skills\<source>\<name>\ into <target>\<name> as directory junctions (no admin rights needed),
# then wires global\AGENTS.md into Claude Code, Codex and Cursor.
# Re-runnable: removes dead junctions, adds missing ones, reports conflicts and plain-folder copies.
# Usage: .\link-skills.ps1                  (targets ~\.claude\skills, ~\.codex\skills, ~\.cursor\skills)
#        .\link-skills.ps1 -ReplaceCopies   (also replace plain-folder copies of registry skills with junctions)
#        .\link-skills.ps1 -Targets D:\x\skills
param(
  [string[]]$Targets = @("$env:USERPROFILE\.claude\skills", "$env:USERPROFILE\.codex\skills", "$env:USERPROFILE\.cursor\skills"),
  [switch]$ReplaceCopies
)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$skills = Get-ChildItem "$root\skills" -Directory | Get-ChildItem -Directory | Where-Object { Test-Path "$($_.FullName)\SKILL.md" }

function Get-LinkTarget($item) { if ($item.LinkType -eq 'Junction' -or $item.LinkType -eq 'SymbolicLink') { @($item.Target)[0] } else { $null } }

foreach ($dst in $Targets) {
  New-Item -ItemType Directory -Force $dst | Out-Null
  foreach ($item in Get-ChildItem $dst -Force -Directory) {
    $t = Get-LinkTarget $item
    if ($t -and -not (Test-Path $t)) { cmd /c rmdir "$($item.FullName)" | Out-Null; "removed dead link: $($item.FullName)" }
  }
  foreach ($s in $skills) {
    $link = Join-Path $dst $s.Name
    if (Test-Path $link) {
      $item = Get-Item $link -Force
      $t = Get-LinkTarget $item
      if ($t) {
        if ((Resolve-Path $t).Path -ne $s.FullName) { "CONFLICT $link -> $t (wanted $($s.FullName))" }
        continue
      }
      if (-not $ReplaceCopies) { "COPY $link is a plain folder, not a link (re-run with -ReplaceCopies)"; continue }
      Remove-Item -Recurse -Force $link
      "replaced copy: $link"
    }
    cmd /c mklink /J "$link" "$($s.FullName)" | Out-Null
  }
  $n = @(Get-ChildItem $dst -Force -Directory | Where-Object { Get-LinkTarget $_ }).Count
  "${dst}: $n skills linked"
}

# Global rules: one source (global\AGENTS.md), three agents.
$global = "$root\global\AGENTS.md"
$import = "@" + ($global -replace '\\', '/')
$claudeMd = "$env:USERPROFILE\.claude\CLAUDE.md"
if (-not (Test-Path $claudeMd) -or -not (Select-String -Path $claudeMd -SimpleMatch $import -Quiet)) {
  Add-Content -Path $claudeMd -Value $import -Encoding utf8
  "Claude: added '$import' to $claudeMd"
}
$marker = "<!-- synced from $global by link-skills; edit the source, not this copy -->"
$codexMd = "$env:USERPROFILE\.codex\AGENTS.md"
if ((Test-Path $codexMd) -and -not (Select-String -Path $codexMd -SimpleMatch 'synced from' -Quiet)) {
  "Codex: $codexMd exists and was not written by this script; left as is"
} else {
  Set-Content -Path $codexMd -Value (@($marker) + (Get-Content $global -Encoding utf8)) -Encoding utf8
  "Codex: synced $codexMd"
}
"Cursor: user rules are not file-based; paste $global into Settings > Rules > User Rules after editing it."
