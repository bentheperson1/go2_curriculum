import asyncio
from go2_module import RobotDog, NormalActions, AIActions, MotionState

async def main():
    dog = RobotDog()
    
    await dog.connect_to_robot()

    volume = await dog.audio_get_volume()
    print(f"Current volume: {volume}")

    brightness = await dog.light_get_brightness()
    print(f"Current brightness: {brightness}")

    await dog.audio_set_volume(7)
    await dog.light_set_brightness(8)
    print("Updated volume to 7 and brightness to 8.")

    await dog.motion_switch_mode(MotionState.NORMAL)
    
    print("Performing the 'HELLO' action...")
    await dog.motion_perform_normal_action(NormalActions.HELLO)

    await asyncio.sleep(5)

    dog.audio_play_mp3_from_file("sounds/demo.mp3")
    print("Playing sound...")

    await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
