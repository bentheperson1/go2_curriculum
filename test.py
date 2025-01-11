from go2_module import *
import asyncio
import sys

async def main():
    dog = RobotDog()

    await dog.connect_to_robot()

    dog.video_display_stream()

    dog.motion_perform_normal_action(NormalActions.HELLO)

    dog.motion_move(1, 0, 0)

    dog.motion_move(-1, 0, 0)

    dog.motion_perform_normal_action(NormalActions.HEART)

    dog.audio_play_mp3_from_file("audio/demo.mp3")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        sys.exit(0)