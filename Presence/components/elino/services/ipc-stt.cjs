// ====== Whisper-CLI STT IPCハンドラ ======

const path = require('path');
const fs = require('fs');
const os = require('os');
const { spawn } = require('child_process');

// CREATE_NO_WINDOW フラグ (Windows)
const CREATE_NO_WINDOW = 0x08000000;

// ELINO プロジェクトルートからの相対パス
function getProjectRoot() {
    return path.resolve(__dirname, '..', '..');
}

function findWhisperCli() {
    const root = getProjectRoot();
    const dirs = [
        path.join(root, 'whisper', 'binaries'),
    ];
    for (const dir of dirs) {
        for (const sub of ['vulkan', '']) {
            const cliName = sub ? path.join(dir, sub, 'whisper-cli.exe') : path.join(dir, 'whisper-cli.exe');
            if (fs.existsSync(cliName)) return { cli: cliName, dir: sub ? path.join(dir, sub) : dir };
        }
    }
    return null;
}

function findWhisperModel(modelId) {
    const modelFiles = {
        'tiny': 'ggml-tiny.bin',
        'small': 'ggml-small.bin',
        'large-v3-turbo': 'ggml-large-v3-turbo-q5_0.bin',
        'kotoba-q5': 'ggml-kotoba-v2.2-q5_0.bin',
        'kotoba-q8': 'ggml-kotoba-v2.2-q8_0.bin',
    };
    const filename = modelFiles[modelId] || 'ggml-tiny.bin';
    const root = getProjectRoot();
    const modelPath = path.join(root, 'whisper', 'models', filename);
    return fs.existsSync(modelPath) ? modelPath : null;
}

function getModelsDir() {
    return path.join(getProjectRoot(), 'whisper', 'models');
}

function runWhisperCli(cli, args) {
    return new Promise((resolve, reject) => {
        const proc = spawn(cli, args, {
            windowsHide: true,
            creationFlags: CREATE_NO_WINDOW,
        });

        let stdout = '';
        let stderr = '';
        proc.stdout.on('data', (d) => { stdout += d.toString(); });
        proc.stderr.on('data', (d) => { stderr += d.toString(); });

        proc.on('close', (code) => {
            if (code !== 0) {
                reject(new Error(`whisper-cli exited with code ${code}: ${stderr.slice(0, 200)}`));
            } else {
                resolve(stdout);
            }
        });

        proc.on('error', (err) => {
            reject(new Error(`whisper-cli spawn error: ${err.message}`));
        });
    });
}

const MODEL_URLS = {
    'tiny': 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin',
    'small': 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin',
    'large-v3-turbo': 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin',
    'kotoba-q5': 'https://huggingface.co/Pomni/kotoba-whisper-v2.2-ggml-allquants/resolve/main/ggml-kotoba-v2.2-q5_0.bin',
    'kotoba-q8': 'https://huggingface.co/Pomni/kotoba-whisper-v2.2-ggml-allquants/resolve/main/ggml-kotoba-v2.2-q8_0.bin',
};

const MODEL_FILES = {
    'tiny': 'ggml-tiny.bin',
    'small': 'ggml-small.bin',
    'large-v3-turbo': 'ggml-large-v3-turbo-q5_0.bin',
    'kotoba-q5': 'ggml-kotoba-v2.2-q5_0.bin',
    'kotoba-q8': 'ggml-kotoba-v2.2-q8_0.bin',
};

function registerSttHandlers(ipcMain, ctx) {
    ipcMain.handle('groq-whisper:transcribe', async (event, { wavBuffer, lang }) => {
        const settings = ctx?.getSettingsCache?.();
        const apiKey = settings?.stt?.groqApiKey || settings?.providers?.groq?.apiKey;
        if (!apiKey) throw new Error('Groq APIキーが設定されていません。STT設定またはLLM設定でGroq APIキーを入力してください');

        const { Blob } = require('buffer');
        const formData = new FormData();
        const blob = new Blob([Buffer.from(wavBuffer)], { type: 'audio/wav' });
        formData.append('file', blob, 'audio.wav');
        formData.append('model', 'whisper-large-v3-turbo');
        if (lang) formData.append('language', lang);
        formData.append('response_format', 'text');

        const res = await fetch('https://api.groq.com/openai/v1/audio/transcriptions', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${apiKey}` },
            body: formData,
        });

        if (!res.ok) {
            const errText = await res.text();
            throw new Error(`Groq Whisper error (${res.status}): ${errText.slice(0, 200)}`);
        }

        return (await res.text()).trim();
    });

    ipcMain.handle('whisper:transcribe', async (event, { wavBuffer, model, prompt, lang }) => {
        const found = findWhisperCli();
        if (!found) {
            throw new Error('whisper-cli が見つかりません。whisper/binaries/ を確認してください。');
        }

        const modelPath = findWhisperModel(model || 'tiny');
        if (!modelPath) {
            throw new Error(`モデルが見つかりません: ${model || 'tiny'}。whisper/models/ にモデルを配置してください。`);
        }

        const tmpWav = path.join(os.tmpdir(), `elino-stt-${Date.now()}.wav`);
        try {
            fs.writeFileSync(tmpWav, Buffer.from(wavBuffer));

            const args = [
                '-m', modelPath,
                '-f', tmpWav,
                '--no-timestamps',
                '-l', lang || 'ja',
                '-otxt',
                '-of', tmpWav.replace(/\.wav$/, ''),
            ];

            if (prompt) {
                args.push('--prompt', prompt);
            }

            await runWhisperCli(found.cli, args);

            const txtPath = tmpWav.replace(/\.wav$/, '.txt');
            let result = '';
            if (fs.existsSync(txtPath)) {
                result = fs.readFileSync(txtPath, 'utf-8').trim();
                try { fs.unlinkSync(txtPath); } catch (_) {}
            }

            return result;
        } finally {
            try { fs.unlinkSync(tmpWav); } catch (_) {}
        }
    });

    ipcMain.handle('whisper:download-model', async (event, { modelId }) => {
        const url = MODEL_URLS[modelId];
        if (!url) throw new Error(`不明なモデル: ${modelId}`);

        const filename = MODEL_FILES[modelId];
        const modelDir = getModelsDir();
        if (!fs.existsSync(modelDir)) fs.mkdirSync(modelDir, { recursive: true });
        const dest = path.join(modelDir, filename);

        if (fs.existsSync(dest)) return 'already exists';

        const https = require('https');
        const http = require('http');

        return new Promise((resolve, reject) => {
            const tmpPath = dest + '.tmp';
            const file = fs.createWriteStream(tmpPath);

            function download(downloadUrl) {
                const client = downloadUrl.startsWith('https') ? https : http;
                client.get(downloadUrl, { headers: { 'User-Agent': 'ELINO' } }, (res) => {
                    // Follow redirects
                    if (res.statusCode === 301 || res.statusCode === 302) {
                        return download(res.headers.location);
                    }
                    if (res.statusCode !== 200) {
                        reject(new Error(`Download failed: ${res.statusCode}`));
                        return;
                    }

                    const totalSize = parseInt(res.headers['content-length'] || '0', 10);
                    let downloaded = 0;
                    let lastProgress = 0;

                    res.on('data', (chunk) => {
                        file.write(chunk);
                        downloaded += chunk.length;
                        if (totalSize > 0) {
                            const progress = Math.floor(downloaded * 100 / totalSize);
                            if (progress !== lastProgress) {
                                lastProgress = progress;
                                event.sender.send('whisper:download-progress', { modelId, progress });
                            }
                        }
                    });

                    res.on('end', () => {
                        file.close(() => {
                            fs.renameSync(tmpPath, dest);
                            resolve('downloaded');
                        });
                    });

                    res.on('error', (err) => {
                        file.close();
                        try { fs.unlinkSync(tmpPath); } catch (_) {}
                        reject(err);
                    });
                }).on('error', (err) => {
                    file.close();
                    try { fs.unlinkSync(tmpPath); } catch (_) {}
                    reject(err);
                });
            }

            download(url);
        });
    });

    ipcMain.handle('whisper:check', async () => {
        const found = findWhisperCli();
        if (!found) return { available: false, models: [] };

        const modelDir = getModelsDir();
        const modelMap = {
            'ggml-tiny.bin': 'tiny',
            'ggml-small.bin': 'small',
            'ggml-large-v3-turbo-q5_0.bin': 'large-v3-turbo',
            'ggml-kotoba-v2.2-q5_0.bin': 'kotoba-q5',
            'ggml-kotoba-v2.2-q8_0.bin': 'kotoba-q8',
        };

        const models = [];
        try {
            const files = fs.readdirSync(modelDir);
            for (const f of files) {
                if (modelMap[f]) models.push(modelMap[f]);
            }
        } catch (_) {}

        return { available: true, models };
    });
}

module.exports = { registerSttHandlers };
