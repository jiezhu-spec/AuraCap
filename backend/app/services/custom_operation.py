from __future__ import annotations

from datetime import datetime

from backend.app.core.config import Settings
from backend.app.providers.base import BaseProvider
from backend.app.services.common import load_prompt


async def run_custom_operation(
    settings: Settings,
    provider: BaseProvider,
    input_text: str,
    suffix: str | None = None,
) -> str:
    prompt = load_prompt(settings.customized_prompt_file, "Apply user's custom instructions to the input.")
    result = await provider.analyze_text(prompt=prompt, text=input_text)

    stamp = suffix or datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    out_path = settings.customized_dir / f"custom_{stamp}.md"
    out_path.write_text(
        "\n".join(
            [
                f"# Custom Operation {stamp}",
                "",
                "## Input",
                input_text,
                "",
                "## Output",
                result,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return str(out_path)
