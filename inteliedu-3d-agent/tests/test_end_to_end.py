"""Comprehensive tests covering Phases 2-8 (Tests 1-7 + FFmpeg/MCP/Runway/API)."""

from __future__ import annotations

import ast
import json
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

AGENT_ROOT = Path(__file__).resolve().parent.parent
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from app.agent.graph import ThreeDGenerationGraph
from app.agent.routing import select_generation_route
from app.agent.topic_understanding import TopicUnderstandingModule
from app.agent.video_planner import VideoPlannerModule
from app.api.routes import get_generation_service
from app.api.schemas import GenerationRequest, SceneSpec
from app.blender.scene_generator import BlenderSceneGenerator
from app.config import Settings, get_settings
from app.main import create_app
from app.mcp.blender_client import BlenderMCPClient
from app.mcp.client import MCPClientManager, MCPServerConfig
from app.mcp.tool_registry import ToolRegistry
from app.runway.client import RunwayAPIClient
from app.runway.generator import RunwayGenerator
from app.services.generation_service import GenerationService
from app.storage.metadata import MetadataRepository
from app.utils.error_handler import DependencyUnavailableError, MCPToolValidationError
from app.video.processor import VideoProcessor
from app.video.subtitles import generate_srt_for_storyboard
from app.video.thumbnail import generate_thumbnail
from app.video.validator import VideoValidator

MCP_TEST_SERVER = Path(__file__).resolve().parent / "fixtures" / "mcp_blender_test_server.py"


def _make_test_settings(tmp_path: Path, *, with_mcp_harness: bool = False) -> Settings:
    settings = Settings(
        app_env="test",
        generated_dir=str(tmp_path / "generated"),
        llm_api_key=None,
        groq_api_key=None,
        gemini_api_key=None,
        blender_executable_path=str(tmp_path / "nonexistent_blender.exe"),
        blender_mcp_command=sys.executable if with_mcp_harness else "",
        blender_mcp_args=f'"{MCP_TEST_SERVER}"' if with_mcp_harness else "",
        runway_api_key=None,
        runway_mcp_url=None,
        runway_mcp_command=None,
        database_url=None,
        video_default_width=640,
        video_default_height=360,
        video_default_fps=24,
        max_retries=1,
    )
    settings.ensure_directories()
    return settings


def _make_ffmpeg_clip(ffmpeg_bin: str, dest: Path, duration: float = 1.5, size: str = "640x360") -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg_bin,
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"testsrc2=size={size}:rate=24:duration={duration}",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(dest),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stderr
    return dest


def _make_ffmpeg_audio(ffmpeg_bin: str, dest: Path, duration: float = 2.0) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg_bin,
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"sine=frequency=440:duration={duration}",
        "-c:a",
        "pcm_s16le",
        str(dest),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stderr
    return dest


# ---------------------------------------------------------------------------
# Phase 2 & 3: MCP Tool Discovery, Validation & Topic/Storyboard Planning
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mcp_discovery_and_schema_validation(tmp_path: Path):
    settings = _make_test_settings(tmp_path, with_mcp_harness=True)
    registry = ToolRegistry()
    manager = MCPClientManager(registry=registry)
    cfg = MCPServerConfig(
        name="blender_mcp",
        transport="stdio",
        command=settings.blender_mcp_command,
        args=settings.parsed_blender_mcp_args(),
    )
    tools = await manager.discover_tools(cfg)
    tool_names = {t.name for t in tools}
    assert {"get_scene_info", "execute_blender_code"}.issubset(tool_names)

    # Invalid arguments must fail JSON schema validation before tool execution
    with pytest.raises(MCPToolValidationError):
        await manager.call_tool(cfg, "execute_blender_code", {"wrong_param": "print(1)"})

    info_res = await manager.call_tool(cfg, "get_scene_info", {})
    assert not info_res.is_error
    assert isinstance(info_res.structured_content, dict)
    assert "objects" in info_res.structured_content


@pytest.mark.asyncio
async def test_non_visual_question_skips_video_generation(tmp_path: Path):
    settings = _make_test_settings(tmp_path)
    graph = ThreeDGenerationGraph(settings=settings)
    req = GenerationRequest(topic="What is the capital of France?", subject="Geography", duration=30)
    final_state = await graph.run("job-skip-001", req)

    assert final_state["video_required"] is False
    assert final_state["status"] == "skipped"
    assert final_state.get("storyboard") is None


@pytest.mark.asyncio
async def test_all_blender_templates_generate_valid_python_syntax(tmp_path: Path):
    settings = _make_test_settings(tmp_path)
    generator = BlenderSceneGenerator(settings=settings)
    templates = [
        "rotating_cube",
        "geometrical_shapes",
        "solar_system",
        "water_cycle",
        "anatomy_asset",
        "atomic_structure",
        "photosynthesis",
        "electric_circuits",
        "volcano_formation",
        "generic_stem",
    ]
    for idx, tpl in enumerate(templates, start=1):
        scene = SceneSpec(
            scene_id=idx,
            title=f"Template {tpl}",
            educational_objective="Verify template syntax",
            description="Automated template syntax check",
            objects=["ObjectA", "ObjectB"],
            animation_instructions="Animate cleanly",
            duration=4,
            template_name=tpl,
        )
        out_mp4 = tmp_path / "generated" / "renders" / f"{tpl}.mp4"
        script_path = generator.generate_script("syntax-job", scene, out_mp4, width=640, height=360, fps=24)
        ast.parse(script_path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Phase 8 End-to-End Tests 1-7
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_1_rotating_cube_end_to_end_via_mcp(tmp_path: Path):
    settings = _make_test_settings(tmp_path, with_mcp_harness=True)
    graph = ThreeDGenerationGraph(settings=settings)
    req = GenerationRequest(topic="Rotating Cube", **{"class": 7}, subject="Mathematics", duration=10)

    state = await graph.run("job-test1-cube", req)
    assert state["status"] == "completed", state.get("errors")
    assert state["actual_engine_used"] == "blender_mcp"
    video = state["stored_video"]
    assert Path(video["local_video_path"]).is_file()
    assert Path(video["local_thumbnail_path"]).is_file()
    assert state["validation_report"]["passed"] is True


@pytest.mark.asyncio
async def test_2_solar_system_educational_video_and_accuracy(tmp_path: Path):
    settings = _make_test_settings(tmp_path, with_mcp_harness=True)
    graph = ThreeDGenerationGraph(settings=settings)
    req = GenerationRequest(
        topic="Explain the Solar System",
        **{"class": 8},
        subject="Science",
        board="State Board",
        duration=24,
        include_subtitles=True,
    )

    state = await graph.run("job-test2-solar", req)
    assert state["status"] == "completed", state.get("errors")
    sb = state["storyboard"]
    assert len(sb["scenes"]) == 6
    assert sb["scale_disclosure"] and "not" in sb["scale_disclosure"].lower()

    # Check generated bpy script contains all 8 planets in heliocentric order + scale disclosure
    script_text = Path(state["generated_scripts"][0]).read_text(encoding="utf-8")
    for planet in ("Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"):
        assert planet in script_text
    assert "not to scale" in script_text.lower()
    assert state["validation_report"]["educational"]["passed"] is True


@pytest.mark.asyncio
async def test_3_water_cycle_educational_video(tmp_path: Path):
    settings = _make_test_settings(tmp_path, with_mcp_harness=True)
    graph = ThreeDGenerationGraph(settings=settings)
    req = GenerationRequest(topic="Water Cycle", **{"class": 6}, subject="Science", duration=16)

    state = await graph.run("job-test3-water", req)
    assert state["status"] == "completed", state.get("errors")
    titles = " ".join(s["title"].lower() for s in state["storyboard"]["scenes"])
    assert "evaporation" in titles
    assert "condensation" in titles
    assert "precipitation" in titles
    assert state["validation_report"]["passed"] is True


@pytest.mark.asyncio
async def test_4_human_heart_reuses_approved_existing_glb_asset(tmp_path: Path):
    settings = _make_test_settings(tmp_path, with_mcp_harness=True)
    topic_mod = TopicUnderstandingModule(settings=settings)
    req = GenerationRequest(topic="Human Heart", **{"class": 10}, subject="Biology", duration=15)

    info = await topic_mod.analyze(req)
    assert info.existing_asset_filename == "real_human_anatomy.glb"
    assert (settings.existing_models_dir / "real_human_anatomy.glb").is_file()

    route = select_generation_route(info, None, BlenderSceneGenerator(settings))
    assert route.primary_engine == "existing_asset_blender"
    assert route.priority_tier == 1

    graph = ThreeDGenerationGraph(settings=settings)
    state = await graph.run("job-test4-heart", req)
    assert state["status"] == "completed", state.get("errors")
    script_text = Path(state["generated_scripts"][0]).read_text(encoding="utf-8")
    assert "real_human_anatomy.glb" in script_text
    assert "import_scene.gltf" in script_text


@pytest.mark.asyncio
async def test_5_fallback_when_blender_mcp_unavailable(tmp_path: Path):
    # Neither Blender MCP nor blender.exe exists on this host -> must NOT fake video
    settings = _make_test_settings(tmp_path, with_mcp_harness=False)
    graph = ThreeDGenerationGraph(settings=settings)
    req = GenerationRequest(topic="Solar System", **{"class": 8}, subject="Science", duration=20)

    state = await graph.run("job-test5-no-blender", req)
    assert state["status"] == "blocked"
    assert state.get("stored_video") is None
    assert len(state["missing_dependencies"]) >= 1
    # Reproducible bpy script artifact is still generated and preserved
    assert len(state["generated_scripts"]) >= 1
    assert Path(state["generated_scripts"][0]).is_file()


@pytest.mark.asyncio
async def test_6_runway_unavailable_fallback_and_official_api_adapter(tmp_path: Path):
    # Part A: Without RUNWAY_API_KEY or Runway MCP, Runway must fail transparently without fake output
    settings = _make_test_settings(tmp_path, with_mcp_harness=False)
    graph = ThreeDGenerationGraph(settings=settings)
    req = GenerationRequest(
        topic="Historical environment of Indus Valley Civilization",
        **{"class": 6},
        subject="History",
        duration=15,
    )
    state = await graph.run("job-test6-no-runway", req)
    assert state["status"] == "blocked"
    assert any("RUNWAY_API_KEY" in dep for dep in state["missing_dependencies"])

    # Part B: Verify official Runway Developer API v1 headers, 429 retry, and task polling
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append((request.method, str(request.url), dict(request.headers)))
        assert request.headers.get("x-runway-version") == "2024-11-06"
        assert request.headers.get("authorization") == "Bearer test_rw_key"
        if request.url.path == "/v1/text_to_video":
            if len([c for c in calls if "/text_to_video" in c[1]]) == 1:
                return httpx.Response(429, headers={"Retry-After": "0.01"}, json={"error": "rate limit"})
            return httpx.Response(200, json={"id": "rw-task-123"})
        if request.url.path == "/v1/tasks/rw-task-123":
            return httpx.Response(
                200,
                json={"id": "rw-task-123", "status": "SUCCEEDED", "output": ["https://cdn.example/clip.mp4"]},
            )
        return httpx.Response(404)

    settings_rw = Settings(
        generated_dir=str(tmp_path / "generated"),
        runway_api_key="test_rw_key",
        runway_api_base_url="https://api.dev.runwayml.com/v1",
        runway_api_version="2024-11-06",
    )
    api = RunwayAPIClient(settings=settings_rw)

    # Monkeypatch httpx.AsyncClient to inject MockTransport
    orig_client = httpx.AsyncClient

    class MockedAsyncClient(orig_client):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = httpx.MockTransport(handler)
            super().__init__(*args, **kwargs)

    httpx.AsyncClient = MockedAsyncClient  # type: ignore
    try:
        task_id = await api.create_text_to_video("Ancient Indus Valley street at sunrise", duration=5)
        assert task_id == "rw-task-123"
        result = await api.wait_for_task(task_id, poll_interval_seconds=0.01)
        assert result.status == "SUCCEEDED"
        assert result.outputs == ["https://cdn.example/clip.mp4"]
    finally:
        httpx.AsyncClient = orig_client  # type: ignore


@pytest.mark.asyncio
async def test_real_ffmpeg_processing_audio_subtitles_and_validation(tmp_path: Path):
    """Uses the real installed FFmpeg & FFprobe binaries to verify processing & validation."""
    settings = _make_test_settings(tmp_path)
    ffmpeg_bin = settings.resolved_ffmpeg_path

    clip1 = _make_ffmpeg_clip(ffmpeg_bin, tmp_path / "clip1.mp4", duration=1.5, size="640x360")
    clip2 = _make_ffmpeg_clip(ffmpeg_bin, tmp_path / "clip2.mp4", duration=1.5, size="640x360")
    audio = _make_ffmpeg_audio(ffmpeg_bin, tmp_path / "narration.wav", duration=3.0)

    planner = VideoPlannerModule(settings=settings)
    topic_info = await TopicUnderstandingModule(settings=settings).analyze(
        GenerationRequest(topic="Rotating Cube", duration=10)
    )
    storyboard = await planner.create_storyboard(topic_info, requested_duration=10)
    # Match storyboard scene count to 2 rendered test clips for validation check
    storyboard.scenes.append(
        SceneSpec(
            scene_id=2,
            title="Cube Summary",
            educational_objective="Review cube edges and vertices",
            description="Summary view",
            objects=["Cube"],
            animation_instructions="Slow spin",
            duration=4,
            narration="All six faces of a cube are equal squares.",
            template_name="rotating_cube",
        )
    )
    srt_path = generate_srt_for_storyboard(storyboard, tmp_path / "subs.srt")
    assert srt_path and srt_path.is_file()

    processor = VideoProcessor(settings=settings)
    final_mp4 = await processor.process_video(
        job_id="ffmpeg-real-test",
        clip_paths=[clip1, clip2],
        output_path=tmp_path / "final.mp4",
        narration_audio_path=audio,
        subtitle_path=srt_path,
    )
    thumb = await generate_thumbnail(final_mp4, tmp_path / "thumb.jpg", timestamp_seconds=0.5, settings=settings)
    assert thumb.is_file() and thumb.stat().st_size > 0

    validator = VideoValidator(settings=settings)
    report = await validator.validate(
        video_path=final_mp4,
        storyboard=storyboard,
        rendered_scene_count=2,
        require_audio=True,
        is_simulated=False,
    )
    assert report.passed is True
    assert report.technical.video_codec == "h264"
    assert report.technical.has_audio is True
    # Must NOT upscale 640x360 source when allow_upscale=False
    assert report.technical.width == 640
    assert report.technical.height == 360


def test_7_api_storage_caching_retrieval_and_deletion(tmp_path: Path):
    settings = _make_test_settings(tmp_path, with_mcp_harness=True)
    repo = MetadataRepository(settings)
    service = GenerationService(settings=settings, metadata_repo=repo)

    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_generation_service] = lambda: service

    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["capabilities"]["ffmpeg"]["available"] is True

        # 1. Plan-only endpoint
        plan_resp = client.post(
            "/api/v1/3d-agent/plan",
            json={"topic": "Solar System", "class": 8, "subject": "Science", "duration": 60},
        )
        assert plan_resp.status_code == 200
        plan_data = plan_resp.json()
        assert plan_data["storyboard"]["video_title"] == "Understanding the Solar System"
        assert len(plan_data["storyboard"]["scenes"]) == 6

        # 2. Generate job asynchronously
        gen_resp = client.post(
            "/api/v1/3d-agent/generate",
            json={"topic": "Rotating Cube", "class": 7, "subject": "Mathematics", "duration": 8},
        )
        assert gen_resp.status_code == 200
        job_id = gen_resp.json()["job_id"]

        # Poll job completion
        status_data = None
        for _ in range(40):
            st = client.get(f"/api/v1/3d-agent/status/{job_id}")
            assert st.status_code == 200
            status_data = st.json()
            if status_data["status"] in ("completed", "failed", "blocked"):
                break
            time.sleep(0.25)

        assert status_data is not None
        assert status_data["status"] == "completed", status_data.get("errors")
        video = status_data["video"]
        video_id = video["video_id"]

        # 3. Duplicate request should hit cache
        cached_resp = client.post(
            "/api/v1/3d-agent/generate",
            json={"topic": "Rotating Cube", "class": 7, "subject": "Mathematics", "duration": 8},
        )
        assert cached_resp.status_code == 200
        assert cached_resp.json()["cached"] is True
        assert cached_resp.json()["video"]["video_id"] == video_id

        # 4. Retrieve video metadata, list, and stream asset
        get_resp = client.get(f"/api/v1/3d-agent/video/{video_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["video"]["video_id"] == video_id

        list_resp = client.get("/api/v1/3d-agent/videos")
        assert list_resp.status_code == 200
        assert list_resp.json()["count"] >= 1

        asset_resp = client.get(video["video_url"])
        assert asset_resp.status_code == 200
        assert len(asset_resp.content) > 1000

        # 5. Delete video cleanly
        del_resp = client.delete(f"/api/v1/3d-agent/video/{video_id}")
        assert del_resp.status_code == 200
        assert client.get(f"/api/v1/3d-agent/video/{video_id}").status_code == 404


def test_api_retry_blocked_job_and_auth_guard(tmp_path: Path):
    settings = _make_test_settings(tmp_path, with_mcp_harness=False)
    settings.agent_api_key = "test-secret-token"
    repo = MetadataRepository(settings)
    service = GenerationService(settings=settings, metadata_repo=repo)

    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_generation_service] = lambda: service

    with TestClient(app) as client:
        # Unauthenticated request must return 401
        unauth = client.post("/api/v1/3d-agent/plan", json={"topic": "Solar System"})
        assert unauth.status_code == 401

        headers = {"Authorization": "Bearer test-secret-token"}
        gen_resp = client.post(
            "/api/v1/3d-agent/generate",
            headers=headers,
            json={"topic": "Rotating Cube", "class": 7, "subject": "Mathematics", "duration": 8},
        )
        assert gen_resp.status_code == 200
        job_id = gen_resp.json()["job_id"]

        for _ in range(30):
            st = client.get(f"/api/v1/3d-agent/status/{job_id}", headers=headers).json()
            if st["status"] in ("blocked", "failed", "completed"):
                break
            time.sleep(0.1)
        assert st["status"] == "blocked"

        retry_resp = client.post(f"/api/v1/3d-agent/retry/{job_id}", headers=headers)
        assert retry_resp.status_code == 200
        assert retry_resp.json()["retried_from_job_id"] == job_id

