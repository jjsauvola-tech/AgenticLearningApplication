"""Copy installed dependency licence files into a Windows distribution."""
import importlib.metadata
import sys
import shutil
from pathlib import Path

target=Path(sys.argv[1])/'THIRD_PARTY_NOTICES'
target.mkdir(parents=True,exist_ok=True)
packages=['python-docx','python-pptx','pypdf','pypdfium2','Pillow','lxml','typing_extensions','XlsxWriter','numpy','cryptography','cffi','charset-normalizer']
lines=['# Included runtime dependencies','', 'Generated from the build environment. Individual notices are copied alongside this index.','']
for package in packages:
    try:dist=importlib.metadata.distribution(package)
    except importlib.metadata.PackageNotFoundError:continue
    lines.append(f'- {dist.metadata["Name"]} {dist.version}')
    for entry in dist.files or []:
        if any(token in str(entry).lower() for token in ('license','licence','copying','notice')):
            p=Path(dist.locate_file(entry))
            if p.is_file() and p.stat().st_size<5_000_000:
                dest=target/package/str(entry).replace('../','').replace('..\\','')
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(p,dest)
for candidate in [Path(sys.base_prefix)/'LICENSE.txt',Path(sys.base_prefix)/'LICENSE']:
    if candidate.exists():shutil.copyfile(candidate,target/'PYTHON_LICENSE.txt')
(target/'INDEX.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
