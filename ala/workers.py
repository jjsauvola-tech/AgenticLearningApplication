"""Bounded, disposable processes for third-party document parsers/renderers."""
import io
import json
import multiprocessing
import tempfile
from pathlib import Path


def _work(kind, source, destination, option):
    target = Path(destination)
    try:
        if kind == 'extract':
            from .importers import extract
            target.write_text(json.dumps(extract(option,Path(source).read_bytes())),encoding='utf-8')
        elif kind == 'pptx':
            from .slides import preview
            target.write_bytes(preview(source,option))
        elif kind == 'pdf':
            import pypdfium2 as pdfium
            with pdfium.PdfDocument(source) as pdf:
                page=pdf[option-1]
                try:
                    bitmap=page.render(scale=min(1.6,1600/max(page.get_width(),1)))
                    try:
                        image=bitmap.to_pil()
                        try: image.save(target,format='PNG')
                        finally: image.close()
                    finally: bitmap.close()
                finally: page.close()
        else:
            raise ValueError('invalid_job')
    except Exception as error:
        from .importers import ImportProblem
        # Only known application error codes cross the process boundary.
        code=str(error) if isinstance(error,(ImportProblem,ValueError)) else 'operation_failed'
        if not code.replace('_','').isalnum() or len(code)>60: code='operation_failed'
        target.with_suffix('.error').write_text(code,encoding='utf-8')


def run_worker(kind,source,option,timeout=100):
    with tempfile.TemporaryDirectory(prefix='ala-worker-') as temp:
        output=Path(temp)/'result'
        process=multiprocessing.get_context('spawn').Process(target=_work,args=(kind,str(source),str(output),option))
        process.start()
        try:
            process.join(timeout)
            if process.is_alive():
                process.terminate();process.join(5)
                if process.is_alive(): process.kill();process.join()
                raise ValueError('worker_timeout')
            error=output.with_suffix('.error')
            if error.exists(): raise ValueError(error.read_text(encoding='utf-8'))
            if process.exitcode or not output.exists(): raise ValueError('worker_failed')
            return output.read_bytes()
        finally:
            if process.is_alive(): process.terminate();process.join()
            process.close()


def extract_isolated(name,data):
    with tempfile.TemporaryDirectory(prefix='ala-import-') as temp:
        source=Path(temp)/'source'
        source.write_bytes(data)
        return json.loads(run_worker('extract',source,name).decode('utf-8'))
