import subprocess
import tempfile
import os
import shutil
from fastmcp import FastMCP

mcp = FastMCP("ManimServer")

# Get Manim executable path from environment variables or assume it's in the system PATH
MANIM_EXECUTABLE = "manim"  # MANIM_PATH "/Users/[Your_username]/anaconda3/envs/manim2/Scripts/manim.exe"

TEMP_DIRS = {}
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
os.makedirs(BASE_DIR, exist_ok=True)  # Ensure the media folder exists


def _gpu_available() -> bool:
    """
    Very simple GPU check:
    Returns True if `nvidia-smi` is found in PATH (NVIDIA GPU visible).
    """
    return shutil.which("nvidia-smi") is not None


@mcp.tool()
def execute_manim_code(
    manim_code: str,
    quality: str = "medium_quality",
) -> str:
    """
    Execute Manim animation code and generate a video.
    
    Args:
        manim_code: Complete Python code containing Manim Scene class(es).
                    Must include import statements and scene definition.
                    Should be plain Python code, not wrapped in markdown code blocks.
                    Example:
                        from manim import *
                        
                        class MyScene(Scene):
                            def construct(self):
                                circle = Circle()
                                self.play(Create(circle))

        quality: Rendering quality preset. One of:
                 - "low_quality"        -> -ql  (fast, low res)
                 - "medium_quality"     -> -qm  (default, 720p)
                 - "high_quality"       -> -qh  (1080p)
                 - "production_quality" -> -qk  (2K/4K, slow)

                 If invalid, no quality flag is added and Manim uses its default.

    Returns:
        Success message with video location, or error details if execution failed.
        Generated videos are stored in /app/media/manim_tmp/ directory.
    """
    tmpdir = os.path.join(BASE_DIR, "manim_tmp")
    os.makedirs(tmpdir, exist_ok=True)
    script_path = os.path.join(tmpdir, "scene.py")

    try:
        # Strip markdown code block markers if present
        code = manim_code.strip()
        if code.startswith("```python") or code.startswith("```"):
            code = code.split("\n", 1)[1] if "\n" in code else code
            if code.endswith("```"):
                code = code.rsplit("```", 1)[0]

        code = code.strip()

        # Write the Manim script to the temp directory
        with open(script_path, "w") as script_file:
            script_file.write(code)

        # ----------------- Build Manim command with GPU + quality logic -----------------
        cmd = [MANIM_EXECUTABLE]

        # 1) GPU vs CPU: choose renderer based on availability
        if _gpu_available():
            renderer = "opengl"
        else:
            renderer = "cairo"
        cmd.extend(["--renderer", renderer])

        # 2) Quality preset
        if quality == "low_quality":
            cmd.append("-ql")
        elif quality == "medium_quality":
            cmd.append("-qm")
        elif quality == "high_quality":
            cmd.append("-qh")
        elif quality == "production_quality":
            cmd.append("-qk")
        # If quality is something else, we skip adding a flag (Manim default)

        # Preview (-p) and script path (same behavior as before)
        cmd.extend(["-p", script_path])
        # -------------------------------------------------------------------------------

        # Execute Manim
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )

        if result.returncode == 0:
            TEMP_DIRS[tmpdir] = True
            return (
                f"Execution successful.\n"
                f"Renderer used: {renderer}\n"
                f"Quality: {quality}\n"
                f"Video generated in directory: {tmpdir}\n"
                f"Command: {' '.join(cmd)}\n"
                f"Output:\n{result.stdout}"
            )
        else:
            return (
                f"Execution failed.\n"
                f"Renderer used: {renderer}\n"
                f"Quality: {quality}\n"
                f"Command: {' '.join(cmd)}\n"
                f"Error:\n{result.stderr}\n"
                f"Output:\n{result.stdout}"
            )

    except Exception as e:
        return f"Error during execution: {str(e)}"


@mcp.tool()
def cleanup_manim_temp_dir(directory: str) -> str:
    """
    Clean up a Manim temporary directory and remove all generated files.
    
    Args:
        directory: Absolute path to the directory to clean up.
                  Typically '/app/media/manim_tmp' or a subdirectory within it.
    
    Returns:
        Success message if cleanup completed, or error details if cleanup failed.
        
    Warning:
        This permanently deletes all files in the specified directory.
        Use with caution to avoid data loss.
    """
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            return f"Cleanup successful for directory: {directory}"
        else:
            return f"Directory not found: {directory}"
    except Exception as e:
        return f"Failed to clean up directory: {directory}. Error: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
