import os
import subprocess

def assemble_video(assets_dir: str, scene_count: int, output_filename: str = "final_video.mp4") -> str:
    """Concatenates video scenes, merges the audio track, and outputs the final video."""
    
    concat_file = os.path.join(assets_dir, "concat.txt")
    output_path = os.path.join(assets_dir, output_filename)
    audio_path = os.path.join(assets_dir, "music.mp3")

    # 1. Create FFmpeg concatenation list file
    with open(concat_file, "w") as f:
        for i in range(1, scene_count + 1):
            scene_path = f"scene_{i}.mp4"
            f.write(f"file '{scene_path}'\n")

    # 2. Build FFmpeg command to stitch video clips and overlay audio
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-i", audio_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "1920k",
        "-shortest",
        output_path
    ]

    # 3. Execute assembly process
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"FFmpeg Assembly Failed:\n{result.stderr}")

    return output_path