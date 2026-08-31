#!/usr/bin/env python3
"""Synchronize vendored skills with upstream repositories and ~/.agents/skills."""

from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path, PurePosixPath


CATALOG_START = "<!-- skill-catalog:start -->"
CATALOG_END = "<!-- skill-catalog:end -->"
SYNC_COMMIT = "chore(skills): sync upstream updates"


class SyncError(RuntimeError):
    pass


def run(
    *args: str,
    cwd: Path | None = None,
    check: bool = True,
    text: bool = True,
    timeout: int | None = None,
) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=text,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        raise SyncError(f"命令超时: {' '.join(args)}") from error
    if check and result.returncode != 0:
        stderr = result.stderr.strip() if text else ""
        raise SyncError(f"命令失败: {' '.join(args)}\n{stderr}")
    return result


def run_network_git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    command = ("rtk", "git", *args) if shutil.which("rtk") else ("git", *args)
    last_result = None
    for attempt in range(3):
        last_result = run(*command, cwd=cwd, check=False, timeout=120)
        if last_result.returncode == 0:
            return last_result
        if attempt < 2:
            time.sleep(1)
    stderr = last_result.stderr.strip() if last_result else ""
    raise SyncError(f"命令失败: {' '.join(command)}\n{stderr}")


def config_path() -> Path:
    configured = os.environ.get("SYNC_SKILLS_CONFIG")
    return Path(configured).expanduser() if configured else Path.home() / ".config/sync-skills/repo"


def find_repo_root() -> Path:
    configured = os.environ.get("SYNC_SKILLS_REPO")
    if configured:
        root = Path(configured).expanduser().resolve()
        if (root / "skills/sources.json").is_file():
            return root
        raise SyncError(f"SYNC_SKILLS_REPO 不是 skills 仓库: {root}")

    saved = config_path()
    if saved.is_file():
        root = Path(saved.read_text().strip()).expanduser().resolve()
        if (root / "skills/sources.json").is_file():
            return root

    candidates = [Path.cwd(), *Path(__file__).resolve().parents]
    for root in candidates:
        if (root / "skills/sources.json").is_file():
            return root
    raise SyncError("找不到 skills 仓库；请设置 SYNC_SKILLS_REPO")


def local_skills_dir() -> Path:
    configured = os.environ.get("SYNC_SKILLS_LOCAL_DIR")
    return Path(configured).expanduser().resolve() if configured else Path.home() / ".agents/skills"


def paths() -> tuple[Path, Path, Path, Path, Path]:
    repo = find_repo_root()
    skills = repo / "skills"
    return (
        repo,
        skills,
        skills / "sources.json",
        repo / "README.md",
        skills / ".sync-conflicts.json",
    )


def require_clean_repo(repo: Path) -> None:
    inside = run("git", "rev-parse", "--is-inside-work-tree", cwd=repo).stdout.strip()
    if inside != "true":
        raise SyncError(f"不是 Git 仓库: {repo}")
    status = run("git", "status", "--porcelain", "--untracked-files=all", cwd=repo).stdout
    if status:
        raise SyncError("Git working tree 不干净。请先 commit 或 stash 当前改动。")


def load_manifest(manifest_path: Path) -> dict:
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise SyncError(f"无法读取 {manifest_path}: {error}") from error
    if manifest.get("version") != 1 or not isinstance(manifest.get("skills"), list):
        raise SyncError("skills/sources.json 格式不正确")
    names = [entry.get("name") for entry in manifest["skills"]]
    if any(not isinstance(name, str) or not name for name in names) or len(names) != len(set(names)):
        raise SyncError("skills/sources.json 存在无效或重复的 skill 名称")
    return manifest


def write_manifest(manifest_path: Path, manifest: dict) -> None:
    manifest["skills"].sort(key=lambda entry: entry["name"])
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


def catalog_lines(manifest: dict) -> list[str]:
    lines = [
        CATALOG_START,
        "## Skill 来源目录",
        "",
        "| 本仓库 skill | 外部来源 | 外部 skill 路径 | 管理方式 |",
        "| --- | --- | --- | --- |",
    ]
    for entry in sorted(manifest["skills"], key=lambda item: item["name"]):
        name = f"`{entry['name']}`"
        if entry.get("managed") is False:
            source = entry.get("note", "本地维护").replace("|", "\\|")
            method = "仅仓库维护" if entry.get("deploy") is False else "本地维护"
            lines.append(f"| {name} | {source} | — | {method} |")
        else:
            url = entry["url"].removesuffix(".git")
            lines.append(
                f"| {name} | [{entry['source']}]({url}) | `{entry['path']}` | 三方合并 |"
            )
    lines.append(CATALOG_END)
    return lines


def update_readme(readme_path: Path, manifest: dict) -> None:
    text = readme_path.read_text()
    start = text.find(CATALOG_START)
    end = text.find(CATALOG_END)
    if start == -1 or end == -1 or end < start:
        raise SyncError("README.md 缺少 skill catalog 标记")
    end += len(CATALOG_END)
    catalog = "\n".join(catalog_lines(manifest))
    readme_path.write_text(text[:start] + catalog + text[end:])


def valid_skill_name(name: str) -> str:
    if not name or name in {".", ".."} or Path(name).name != name or "/" in name or "\\" in name:
        raise SyncError(f"无效的 skill 名称: {name!r}")
    return name


def remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def clear_directory(path: Path, keep: set[str] | None = None) -> None:
    keep = keep or set()
    for child in path.iterdir():
        if child.name not in keep:
            remove_path(child)


def copy_contents(source: Path, destination: Path, keep: set[str] | None = None) -> None:
    if not source.is_dir():
        raise SyncError(f"skill 目录不存在: {source}")
    keep = keep or set()
    destination.mkdir(parents=True, exist_ok=True)
    clear_directory(destination, keep)
    for child in source.iterdir():
        if (
            child.name in keep
            or child.name in {".git", ".DS_Store", "__pycache__"}
            or child.suffix == ".pyc"
        ):
            continue
        target = destination / child.name
        if child.is_dir() and not child.is_symlink():
            shutil.copytree(
                child,
                target,
                symlinks=True,
                ignore=shutil.ignore_patterns(".git", ".DS_Store", "__pycache__", "*.pyc"),
            )
        elif child.is_symlink():
            target.symlink_to(os.readlink(child))
        else:
            shutil.copy2(child, target)


def mirror_for(url: str) -> Path:
    key = hashlib.sha256(url.encode()).hexdigest()[:16]
    return local_skills_dir().parent / "cache/sync-skills/repos" / f"{key}.git"


def cached_checkout(url: str) -> Path | None:
    key = hashlib.sha256(url.encode()).hexdigest()[:16]
    candidate = Path.home() / ".skills-manager/cache/repos" / key
    return candidate if (candidate / ".git").is_dir() else None


def update_mirror(repo: Path, url: str) -> Path:
    mirror = mirror_for(url)
    mirror.parent.mkdir(parents=True, exist_ok=True)
    if mirror.exists():
        valid = run("git", "rev-parse", "--is-bare-repository", cwd=mirror, check=False)
        head = run("git", "rev-parse", "--verify", "HEAD^{commit}", cwd=mirror, check=False)
        partial = run("git", "config", "--get", "remote.origin.promisor", cwd=mirror, check=False)
        if (
            valid.returncode != 0
            or valid.stdout.strip() != "true"
            or head.returncode != 0
            or partial.stdout.strip() == "true"
        ):
            shutil.rmtree(mirror)
    if mirror.exists():
        run_network_git("fetch", "origin", "--prune", cwd=mirror)
    else:
        try:
            seed = cached_checkout(url)
            if seed:
                shutil.copytree(seed / ".git", mirror, symlinks=True)
                run("git", "config", "core.bare", "true", cwd=mirror)
                run("git", "remote", "set-url", "origin", url, cwd=mirror)
                run_network_git("fetch", "origin", "--prune", cwd=mirror)
            else:
                run_network_git("clone", "--mirror", url, str(mirror), cwd=repo)
        except SyncError:
            if mirror.exists():
                shutil.rmtree(mirror)
            raise
    return mirror


def resolve_revision(mirror: Path, ref: str | None) -> str:
    candidates = (
        [ref, f"refs/remotes/origin/{ref}", f"refs/heads/{ref}", f"refs/tags/{ref}"]
        if ref
        else ["refs/remotes/origin/HEAD", "HEAD"]
    )
    for candidate in candidates:
        result = run(
            "git", "rev-parse", "--verify", f"{candidate}^{{commit}}", cwd=mirror, check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
    raise SyncError(f"找不到上游 ref: {ref}")


def skill_tree(mirror: Path, revision: str, skill_path: str) -> str:
    folder = PurePosixPath(skill_path).parent
    treeish = f"{revision}^{{tree}}" if str(folder) == "." else f"{revision}:{folder}"
    result = run("git", "rev-parse", "--verify", treeish, cwd=mirror, check=False)
    if result.returncode != 0:
        raise SyncError(f"上游中找不到 skill 目录: {skill_path}")
    return result.stdout.strip()


def extract_tree(mirror: Path, tree: str, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    archive = run("git", "archive", "--format=tar", tree, cwd=mirror, text=False).stdout
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
        tar.extractall(destination, filter="data")


def commit_snapshot(worktree: Path, message: str) -> str:
    run("git", "add", "-A", cwd=worktree)
    run("git", "commit", "--allow-empty", "-q", "-m", message, cwd=worktree)
    return run("git", "rev-parse", "HEAD", cwd=worktree).stdout.strip()


def stage_blob(worktree: Path, stage: int, relative_path: str) -> bytes | None:
    result = run("git", "show", f":{stage}:{relative_path}", cwd=worktree, check=False, text=False)
    return result.stdout if result.returncode == 0 else None


def conflict_text(content: bytes | None) -> str:
    if content is None:
        return "[deleted]\n"
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError from error


def materialize_conflicts(worktree: Path, conflict_paths: list[str]) -> list[dict[str, str]]:
    conflicts = []
    for relative_path in conflict_paths:
        base = stage_blob(worktree, 1, relative_path)
        local = stage_blob(worktree, 2, relative_path)
        upstream = stage_blob(worktree, 3, relative_path)
        target = worktree / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            target.write_text(
                "<<<<<<< local\n"
                f"{conflict_text(local)}"
                "||||||| base\n"
                f"{conflict_text(base)}"
                "=======\n"
                f"{conflict_text(upstream)}"
                ">>>>>>> upstream\n"
            )
            conflicts.append({"path": relative_path, "kind": "text"})
        except ValueError:
            remove_path(target)
            target.with_name(target.name + ".sync-conflict").write_text(
                "二进制文件冲突；比较同目录的 .local、.base 和 .upstream 文件。\n"
            )
            for label, content in (("local", local), ("base", base), ("upstream", upstream)):
                if content is not None:
                    target.with_name(f"{target.name}.{label}").write_bytes(content)
            conflicts.append({"path": relative_path, "kind": "binary"})
    return conflicts


def merge_skill(
    name: str,
    local_dir: Path,
    mirror: Path,
    base_tree: str,
    latest_tree: str,
) -> list[dict[str, str]]:
    with tempfile.TemporaryDirectory(prefix=f"sync-{name}-") as temp:
        temp_root = Path(temp)
        base_dir = temp_root / "base"
        upstream_dir = temp_root / "upstream"
        worktree = temp_root / "merge"
        extract_tree(mirror, base_tree, base_dir)
        extract_tree(mirror, latest_tree, upstream_dir)
        worktree.mkdir()
        run("git", "init", "-q", cwd=worktree)
        run("git", "config", "user.name", "sync-skills", cwd=worktree)
        run("git", "config", "user.email", "sync-skills@local", cwd=worktree)

        copy_contents(base_dir, worktree, {".git"})
        base_commit = commit_snapshot(worktree, "base")
        run("git", "checkout", "-q", "-b", "local", cwd=worktree)
        copy_contents(local_dir, worktree, {".git"})
        commit_snapshot(worktree, "local")
        run("git", "checkout", "-q", "-b", "upstream", base_commit, cwd=worktree)
        copy_contents(upstream_dir, worktree, {".git"})
        commit_snapshot(worktree, "upstream")
        run("git", "checkout", "-q", "local", cwd=worktree)

        merge = run("git", "merge", "--no-edit", "--no-ff", "upstream", cwd=worktree, check=False)
        conflicts = []
        if merge.returncode != 0:
            output = run(
                "git", "diff", "--name-only", "--diff-filter=U", "-z", cwd=worktree
            ).stdout
            conflict_paths = [path for path in output.split("\0") if path]
            if not conflict_paths:
                raise SyncError(f"{name} 合并失败:\n{merge.stderr.strip()}")
            conflicts = materialize_conflicts(worktree, conflict_paths)

        copy_contents(worktree, local_dir, {".git"})
        return conflicts


def commit_paths(repo: Path, message: str, changed_paths: list[Path]) -> bool:
    relative = [str(path.relative_to(repo)) for path in changed_paths]
    run("git", "add", "-A", "--", *relative, cwd=repo)
    staged = run("git", "diff", "--cached", "--quiet", cwd=repo, check=False)
    if staged.returncode == 0:
        return False
    run("git", "commit", "-m", message, cwd=repo)
    return True


def write_repo_config(repo: Path) -> None:
    destination = config_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(str(repo) + "\n")


def deploy_skills(repo: Path, skills_dir: Path, manifest: dict, local_dir: Path) -> None:
    entries = [entry for entry in manifest["skills"] if entry.get("deploy") is not False]
    for entry in entries:
        if not (skills_dir / entry["name"]).is_dir():
            raise SyncError(f"仓库缺少 skill 目录: {entry['name']}")

    local_dir.mkdir(parents=True, exist_ok=True)
    stage_root = Path(tempfile.mkdtemp(prefix=".sync-skills-", dir=local_dir))
    incoming = stage_root / "incoming"
    backups = stage_root / "backups"
    incoming.mkdir()
    backups.mkdir()
    replaced: list[tuple[str, bool]] = []
    try:
        for entry in entries:
            name = entry["name"]
            copy_contents(skills_dir / name, incoming / name)
        for entry in entries:
            name = entry["name"]
            destination = local_dir / name
            backup = backups / name
            had_backup = destination.exists() or destination.is_symlink()
            if had_backup:
                destination.rename(backup)
            try:
                (incoming / name).rename(destination)
            except Exception:
                if had_backup:
                    backup.rename(destination)
                raise
            replaced.append((name, had_backup))
    except Exception:
        for name, had_backup in reversed(replaced):
            destination = local_dir / name
            backup = backups / name
            remove_path(destination)
            if had_backup:
                backup.rename(destination)
        raise
    finally:
        shutil.rmtree(stage_root, ignore_errors=True)
    write_repo_config(repo)
    print(f"已同步到 {local_dir}")


def sync_upstream() -> int:
    repo, skills_dir, manifest_path, _, conflict_report = paths()
    local_dir = local_skills_dir()
    require_clean_repo(repo)
    manifest = load_manifest(manifest_path)
    updated: list[str] = []
    all_conflicts: list[dict[str, str]] = []
    mirrors: dict[str, Path] = {}

    with tempfile.TemporaryDirectory(prefix="sync-skills-") as temp:
        staging_root = Path(temp)
        for entry in manifest["skills"]:
            name = entry["name"]
            if entry.get("managed") is False:
                print(f"跳过 {name}: 本地维护")
                continue
            required = ("url", "path", "base_tree")
            if any(not entry.get(field) for field in required):
                raise SyncError(f"{name} 缺少来源字段")

            print(f"检查 {name} ...")
            mirror = mirrors.get(entry["url"])
            if mirror is None:
                mirror = update_mirror(repo, entry["url"])
                mirrors[entry["url"]] = mirror
            revision = resolve_revision(mirror, entry.get("ref"))
            latest_tree = skill_tree(mirror, revision, entry["path"])
            if latest_tree == entry["base_tree"]:
                print("  无更新")
                continue

            staged_skill = staging_root / name
            copy_contents(skills_dir / name, staged_skill)
            conflicts = merge_skill(
                name, staged_skill, mirror, entry["base_tree"], latest_tree
            )
            entry["base_tree"] = latest_tree
            updated.append(name)
            all_conflicts.extend({"skill": name, **conflict} for conflict in conflicts)
            print("  已合并" if not conflicts else f"  有 {len(conflicts)} 个冲突")

        for name in updated:
            copy_contents(staging_root / name, skills_dir / name)

    if updated:
        write_manifest(manifest_path, manifest)
    if all_conflicts:
        conflict_report.write_text(
            json.dumps({"conflicts": all_conflicts}, ensure_ascii=False, indent=2) + "\n"
        )
        print(f"发现冲突，未 commit，也未同步本机。详情见 {conflict_report.relative_to(repo)}。")
        return 1

    remove_path(conflict_report)
    if updated:
        changed = [manifest_path, *(skills_dir / name for name in updated)]
        commit_paths(repo, SYNC_COMMIT, changed)
        print(f"已更新 {len(updated)} 个 skills。")
    else:
        print("所有外部 skills 都没有更新；继续使用仓库版本。")
    deploy_skills(repo, skills_dir, manifest, local_dir)
    return 0


def lock_entry(local_dir: Path, name: str) -> dict | None:
    lock_path = local_dir.parent / ".skill-lock.json"
    if not lock_path.is_file():
        return None
    try:
        return json.loads(lock_path.read_text()).get("skills", {}).get(name)
    except json.JSONDecodeError as error:
        raise SyncError(f"无法读取 {lock_path}: {error}") from error


def manifest_entry_for_add(local_dir: Path, name: str, source: Path) -> dict:
    tracked = lock_entry(local_dir, name)
    if (
        tracked
        and tracked.get("sourceType") == "github"
        and tracked.get("source")
        and tracked.get("sourceUrl")
        and tracked.get("skillPath")
        and tracked.get("skillFolderHash")
    ):
        entry = {
            "name": name,
            "source": tracked["source"],
            "url": tracked["sourceUrl"],
            "path": tracked["skillPath"],
            "base_tree": tracked["skillFolderHash"],
        }
        if tracked.get("ref"):
            entry["ref"] = tracked["ref"]
        return entry
    entry = {"name": name, "managed": False, "note": "本地维护，暂无外部 Git 来源"}
    if source.is_symlink():
        entry["deploy"] = False
        entry["note"] = f"本机链接 {source.resolve()}，仓库保留快照但不覆盖该链接"
    return entry


def add_skill(name: str) -> int:
    name = valid_skill_name(name)
    repo, skills_dir, manifest_path, readme_path, _ = paths()
    local_dir = local_skills_dir()
    require_clean_repo(repo)
    manifest = load_manifest(manifest_path)
    if any(entry["name"] == name for entry in manifest["skills"]):
        raise SyncError(f"skill 已在仓库中: {name}")
    source = local_dir / name
    if not source.is_dir():
        raise SyncError(f"请先把 skill 安装到 {source}")
    if not (source / "SKILL.md").is_file():
        raise SyncError(f"skill 缺少 SKILL.md: {source}")
    destination = skills_dir / name
    if destination.exists() or destination.is_symlink():
        raise SyncError(f"仓库目录已存在但未登记: {destination}")

    copy_contents(source.resolve() if source.is_symlink() else source, destination)
    manifest["skills"].append(manifest_entry_for_add(local_dir, name, source))
    write_manifest(manifest_path, manifest)
    update_readme(readme_path, manifest)
    commit_paths(repo, f"chore(skills): add {name}", [destination, manifest_path, readme_path])
    deploy_skills(repo, skills_dir, manifest, local_dir)
    print(f"已添加 {name}")
    return 0


def remove_skill(name: str) -> int:
    name = valid_skill_name(name)
    repo, skills_dir, manifest_path, readme_path, _ = paths()
    local_dir = local_skills_dir()
    require_clean_repo(repo)
    manifest = load_manifest(manifest_path)
    matches = [entry for entry in manifest["skills"] if entry["name"] == name]
    if not matches:
        raise SyncError(f"skill 不在仓库中: {name}")

    destination = skills_dir / name
    remove_path(destination)
    manifest["skills"] = [entry for entry in manifest["skills"] if entry["name"] != name]
    write_manifest(manifest_path, manifest)
    update_readme(readme_path, manifest)
    commit_paths(repo, f"chore(skills): remove {name}", [destination, manifest_path, readme_path])
    deploy_skills(repo, skills_dir, manifest, local_dir)
    remove_path(local_dir / name)
    print(f"已删除 {name}")
    return 0


def parse_command(arguments: list[str]) -> tuple[str, str | None]:
    if not arguments:
        return "sync", None
    if len(arguments) != 2:
        raise SyncError("用法: sync-skills [添加|删除] <skill-name>")
    command, name = arguments
    commands = {"添加": "add", "add": "add", "删除": "remove", "remove": "remove"}
    if command not in commands:
        raise SyncError("用法: sync-skills [添加|删除] <skill-name>")
    return commands[command], name


def main(arguments: list[str]) -> int:
    command, name = parse_command(arguments)
    if command == "add":
        return add_skill(name or "")
    if command == "remove":
        return remove_skill(name or "")
    return sync_upstream()


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except SyncError as error:
        print(f"sync-skills: {error}", file=sys.stderr)
        raise SystemExit(2)
