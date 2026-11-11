"""Lightweight built-in HTML test console served at GET / for local inspection."""

CONSOLE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Inteliedu 3D Generation Agent — Test Console</title>
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; background: #f8fafc; color: #0f172a; margin: 0; padding: 24px; }
    .container { max-width: 980px; margin: 0 auto; }
    .card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
    h1 { margin: 0 0 6px; font-size: 22px; }
    h2 { margin: 0 0 10px; font-size: 16px; }
    .muted { color: #64748b; font-size: 13px; }
    .row { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin-top: 12px; }
    label { display: block; font-size: 12px; font-weight: 600; margin-bottom: 4px; color: #334155; }
    input, select { width: 100%; box-sizing: border-box; padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; }
    .actions { display: flex; gap: 10px; margin-top: 14px; flex-wrap: wrap; }
    button { border: 0; border-radius: 8px; padding: 9px 14px; font-size: 13px; font-weight: 600; cursor: pointer; }
    .btn-primary { background: #2563eb; color: #fff; }
    .btn-secondary { background: #0f172a; color: #fff; }
    .btn-light { background: #e2e8f0; color: #0f172a; }
    pre { background: #0f172a; color: #e2e8f0; padding: 14px; border-radius: 10px; overflow-x: auto; font-size: 12px; max-height: 440px; }
    a { color: #2563eb; text-decoration: none; font-weight: 600; }
    .banner { padding: 12px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 12px; display: none; }
    .banner.warn { display: block; background: #fef3c7; border: 1px solid #f59e0b; color: #78350f; }
    .banner.ok { display: block; background: #dcfce7; border: 1px solid #22c55e; color: #14532d; }
    .video-box { display: none; }
    .video-box.active { display: block; }
    video { width: 100%; max-height: 460px; border-radius: 10px; background: #000; }
    .meta { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 10px; font-size: 13px; color: #334155; }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <h1>Inteliedu 3D &amp; AI Video Generation Agent</h1>
      <div class="muted">
        API Docs: <a href="/docs">/docs</a> &bull;
        Health: <a href="/health">/health</a> &bull;
        Capabilities: <a href="/api/v1/3d-agent/capabilities">/api/v1/3d-agent/capabilities</a>
      </div>
    </div>

    <div class="card">
      <div class="row">
        <div>
          <label>Topic / Student Question</label>
          <input id="topic" value="Explain the Solar System" />
        </div>
        <div>
          <label>Class (6–12)</label>
          <input id="cls" type="number" min="1" max="12" value="8" />
        </div>
        <div>
          <label>Subject</label>
          <input id="subject" value="Science" />
        </div>
        <div>
          <label>Duration (sec)</label>
          <input id="duration" type="number" min="5" max="300" value="60" />
        </div>
      </div>
      <div class="actions">
        <button class="btn-primary" onclick="runPlan()">1. Plan Storyboard (/plan)</button>
        <button class="btn-secondary" onclick="runGenerate()">2. Generate Job (/generate)</button>
        <button class="btn-light" onclick="checkCaps()">Check Capabilities</button>
        <button class="btn-light" onclick="listVideos()">List Stored Videos</button>
      </div>
    </div>

    <div id="statusBanner" class="banner"></div>

    <div id="videoCard" class="card video-box">
      <h2 id="videoTitle">Generated Video Output</h2>
      <video id="player" controls playsinline>
        <track id="subTrack" kind="subtitles" srclang="en" label="English" default />
      </video>
      <div class="meta">
        <span id="videoMeta"></span>
        <a id="videoLink" href="#" target="_blank">Open MP4</a>
        <a id="thumbLink" href="#" target="_blank">Open Thumbnail</a>
      </div>
    </div>

    <div class="card">
      <label>Live Agent Output (JSON)</label>
      <pre id="out">Click a button above to test the 3D Generation Agent...</pre>
    </div>
  </div>

  <script>
    const out = document.getElementById('out');
    const banner = document.getElementById('statusBanner');
    const videoCard = document.getElementById('videoCard');
    const player = document.getElementById('player');
    const subTrack = document.getElementById('subTrack');
    const videoTitle = document.getElementById('videoTitle');
    const videoMeta = document.getElementById('videoMeta');
    const videoLink = document.getElementById('videoLink');
    const thumbLink = document.getElementById('thumbLink');

    function payload() {
      return {
        topic: document.getElementById('topic').value,
        class: Number(document.getElementById('cls').value || 8),
        subject: document.getElementById('subject').value || 'Science',
        board: 'State Board',
        duration: Number(document.getElementById('duration').value || 60),
        include_narration: true,
        include_subtitles: true
      };
    }

    function renderVideo(video) {
      if (!video || !video.video_url) {
        videoCard.classList.remove('active');
        return;
      }
      videoCard.classList.add('active');
      videoTitle.textContent = video.title || video.topic || 'Generated Video';
      player.src = video.video_url;
      if (video.thumbnail_url) {
        player.poster = video.thumbnail_url;
        thumbLink.href = video.thumbnail_url;
        thumbLink.style.display = 'inline';
      } else {
        thumbLink.style.display = 'none';
      }
      if (video.subtitle_url) {
        subTrack.src = video.subtitle_url;
      }
      videoLink.href = video.video_url;
      videoMeta.textContent = `Engine: ${video.generation_engine} | Duration: ${video.duration}s | Resolution: ${video.resolution}`;
    }

    function renderResponse(data) {
      out.textContent = JSON.stringify(data, null, 2);
      banner.className = 'banner';
      banner.textContent = '';

      const video = data.video || (Array.isArray(data.videos) && data.videos[0]) || null;
      if (video && video.video_url) {
        banner.className = 'banner ok';
        banner.textContent = 'Video ready! Playing generated MP4 below.';
        renderVideo(video);
        return;
      }

      renderVideo(null);
      if (data.status === 'blocked') {
        banner.className = 'banner warn';
        const deps = (data.missing_dependencies || []).join('; ');
        banner.textContent = 'No video rendered because rendering backends are unconfigured (' + deps + '). Generated Blender script(s) were saved in generated/scripts/.';
      }
    }

    async function showJson(res) {
      const text = await res.text();
      try {
        renderResponse(JSON.parse(text));
      } catch {
        out.textContent = text;
      }
    }

    async function checkCaps() {
      out.textContent = 'Loading capabilities...';
      await showJson(await fetch('/api/v1/3d-agent/capabilities'));
    }

    async function listVideos() {
      out.textContent = 'Fetching videos...';
      await showJson(await fetch('/api/v1/3d-agent/videos'));
    }

    async function runPlan() {
      out.textContent = 'Planning storyboard...';
      const res = await fetch('/api/v1/3d-agent/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload())
      });
      await showJson(res);
    }

    async function runGenerate() {
      out.textContent = 'Starting generation job...';
      const res = await fetch('/api/v1/3d-agent/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload())
      });
      const data = await res.json();
      renderResponse(data);
      if (data.job_id && !data.cached && !['completed', 'blocked', 'failed', 'skipped'].includes(data.status)) {
        const timer = setInterval(async () => {
          const stRes = await fetch('/api/v1/3d-agent/status/' + data.job_id);
          const st = await stRes.json();
          renderResponse(st);
          if (['completed', 'blocked', 'failed', 'skipped'].includes(st.status)) {
            clearInterval(timer);
          }
        }, 500);
      }
    }
  </script>
</body>
</html>
"""
