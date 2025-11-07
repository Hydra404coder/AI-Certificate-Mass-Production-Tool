const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

function runPython() {
  const cwd = __dirname; // project root
  const mainPath = path.join(cwd, 'main.py');

  // Try py (Windows launcher), then python, then python3
  const candidates = [
    { cmd: 'py', args: ['-3', mainPath], shell: true },
    { cmd: 'python', args: [mainPath], shell: true },
    { cmd: 'python3', args: [mainPath], shell: true },
  ];

  function trySpawn(index = 0) {
    if (index >= candidates.length) return null;
    const c = candidates[index];
    try {
      const proc = spawn(c.cmd, c.args, {
        cwd,
        detached: false,
        shell: c.shell,
        stdio: 'inherit', // let Python use parent's stdio (should allow GUI)
      });
      proc.stdout && proc.stdout.on('data', data => {
        console.log(`[main.py stdout]: ${data}`);
      });
      proc.stderr && proc.stderr.on('data', data => {
        console.error(`[main.py stderr]: ${data}`);
      });
      proc.on('error', err => {
        console.error(`[main.py error]:`, err);
      });
      proc.on('exit', (code, signal) => {
        console.log(`[main.py exited] code=${code} signal=${signal}`);
      });
      return proc;
    } catch (e) {
      console.error(`[main.py spawn error]:`, e);
      return trySpawn(index + 1);
    }
  }

  return trySpawn(0);
}

app.post('/start', (req, res) => {
  const proc = runPython();
  if (!proc) {
    return res.status(500).json({ status: 'error', message: 'Unable to find Python (py/python/python3) to run main.py' });
  }
  // Let the GUI start; do not wait
  res.json({ status: 'ok', message: 'Launching main.py' });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Node backend listening on http://localhost:${PORT}`);
});
