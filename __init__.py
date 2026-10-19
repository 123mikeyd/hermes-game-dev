"""Native Hermes game-dev plugin; only documented PluginContext APIs."""
from pathlib import Path

from . import game_dev_tools, schemas


def register(ctx):
    """Register read-only tools and immediate bundled skill directories."""
    ctx.register_tool(name="game_dev_inspect", toolset="game-dev",
                      schema=schemas.INSPECT, handler=game_dev_tools.game_dev_inspect)
    ctx.register_tool(name="game_dev_asset_audit", toolset="game-dev",
                      schema=schemas.ASSET_AUDIT, handler=game_dev_tools.game_dev_asset_audit)
    ctx.register_tool(name="game_dev_checklist", toolset="game-dev",
                      schema=schemas.CHECKLIST, handler=game_dev_tools.game_dev_checklist)
    skills = Path(__file__).parent / "skills"
    if skills.is_dir() and not game_dev_tools._link(skills.lstat()):
        for child in sorted(skills.iterdir()):
            skill = child / "SKILL.md"
            if (child.is_dir() and not game_dev_tools._link(child.lstat())
                    and skill.is_file() and not game_dev_tools._link(skill.lstat())):
                if skill.resolve().is_relative_to(skills.resolve()):
                    ctx.register_skill(child.name, skill)
