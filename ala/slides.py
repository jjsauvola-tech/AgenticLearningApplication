"""Render static PowerPoint slides locally, without changing the source deck."""
import os
import subprocess
import tempfile
from pathlib import Path


def preview(original, page):
    original = Path(original).resolve()
    cache = original.parent.parent / 'previews' / original.stem
    target = cache / f'{page}.png'
    if target.is_file():
        return target.read_bytes()
    if os.name != 'nt':
        raise ValueError('slide_preview_unavailable')
    cache.mkdir(parents=True, exist_ok=True)
    # Arguments travel through environment values, never executable shell text.
    script = r'''
$ErrorActionPreference = 'Stop'
$app = $null
$deck = $null
$security = $null
try {
    $app = New-Object -ComObject PowerPoint.Application
    $security = $app.AutomationSecurity
    $app.AutomationSecurity = 3
    $deck = $app.Presentations.Open($env:ALA_SLIDE_SOURCE, -1, 0, 0)
    $height = [int](1600 * $deck.PageSetup.SlideHeight / $deck.PageSetup.SlideWidth)
    $deck.Slides.Item([int]$env:ALA_SLIDE_PAGE).Export($env:ALA_SLIDE_OUTPUT, 'PNG', 1600, $height)
} finally {
    if ($deck) { $deck.Close() }
    if ($app -and $null -ne $security) { $app.AutomationSecurity = $security }
    if ($app) { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($app) }
}
'''
    with tempfile.TemporaryDirectory(prefix='ala-slide-') as temp:
        output = Path(temp) / 'slide.png'
        env = {**os.environ, 'ALA_SLIDE_SOURCE': str(original),
               'ALA_SLIDE_PAGE': str(page), 'ALA_SLIDE_OUTPUT': str(output)}
        try:
            subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', script],
                           env=env, capture_output=True, timeout=90, check=True,
                           creationflags=subprocess.CREATE_NO_WINDOW)
            data = output.read_bytes()
            if not data.startswith(b'\x89PNG\r\n\x1a\n'):
                raise ValueError('slide_preview_unavailable')
            temporary = target.with_suffix(".tmp")
            temporary.write_bytes(data)
            os.replace(temporary,target)
            return data
        except (OSError, subprocess.SubprocessError) as exc:
            raise ValueError('slide_preview_unavailable') from exc
