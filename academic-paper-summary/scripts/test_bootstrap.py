"""Exercise Python discovery without installing packages or changing system settings."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest


class BootstrapTests(unittest.TestCase):
    def command(self, python):
        scripts=Path(__file__).resolve().parent
        if os.name=='nt':
            shell=shutil.which('powershell')
            if not shell:self.skipTest('PowerShell unavailable')
            return [shell,'-NoProfile','-File',str(scripts/'bootstrap.ps1'),'-CheckOnly','-PythonPath',python]
        shell=shutil.which('sh')
        if not shell:self.skipTest('POSIX shell unavailable')
        return [shell,str(scripts/'bootstrap.sh'),'--check-only','--python',python]

    def test_explicit_runtime_discovery(self):
        result=subprocess.run(self.command(sys.executable),capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('Discovery only',result.stdout)

    def test_missing_runtime_gives_install_guidance(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=subprocess.run(self.command(str(Path(tmp)/'missing-python')),capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,2,result.stderr)
            self.assertIn('https://www.python.org/downloads/',result.stderr)
            self.assertEqual(list(Path(tmp).iterdir()),[])

    def test_discovered_runtime_precedes_local_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            args=self.command(sys.executable)
            flag='-PythonPath' if os.name=='nt' else '--python'
            args[args.index(flag)]='-RuntimePython' if os.name=='nt' else '--runtime-python'
            args += ['-VenvPath' if os.name=='nt' else '--venv',str(Path(tmp)/'not-created')]
            result=subprocess.run(args,capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(list(Path(tmp).iterdir()),[])


if __name__=='__main__':unittest.main()
