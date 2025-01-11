from go2_module import *
from go2_webrtc_driver.constants import VUI_COLOR

import asyncio
import sys

async def main():
    dog = RobotDog()

    await dog.connect_to_robot()

    dog.video_display_stream(1280, 720)

    await dog.audio_set_volume(10)
    await dog.light_set_color(VUI_COLOR.RED)
    await dog.motion_perform_normal_action(NormalActions.HELLO)

    await dog.motion_move(1, 0, 0)
    await dog.motion_move(-1, 0, 0)

    await dog.motion_perform_normal_action(NormalActions.HEART)

    await dog.motion_switch_mode(MotionState.AI)
    await dog.motion_perform_ai_action(AIActions.HANDSTAND, True)

    await asyncio.sleep(5)

    await dog.motion_perform_ai_action(AIActions.HANDSTAND, False)

    dog.audio_play_mp3_from_file("audio/unicorn.mp3")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        sys.exit(0)
