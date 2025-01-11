import asyncio
import logging
import threading
import time
import cv2
import numpy as np
import json
import os

from queue import Queue
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
from go2_webrtc_driver.constants import RTC_TOPIC, SPORT_CMD
from aiortc import MediaStreamTrack
from aiortc.contrib.media import MediaPlayer

class MotionState:
	NORMAL: str = "normal"
	AI: str = "ai"

class NormalActions:
	DAMP: str = "Damp"
	LAY_DOWN: str = "StandDown"
	STAND_UP: str = "RecoveryStand"
	SIT_DOWN: str = "Sit"
	HELLO: str = "Hello"
	STRETCH: str = "Stretch"
	JUMP_FORWARD: str = "FrontJump"
	WIGGLE_HIPS: str = "WiggleHips"
	POUNCE: str = "FrontPounce"
	HEART: str = "FingerHeart"
	DANCE1: str = "Dance1"
	DANCE2: str = "Dance2"

class AIActions:
	HANDSTAND: str = "Handstand"
	CROSS_STEP: str = "CrossStep"
	ONE_SIDE_STEP: str = "OnesidedStep"
	FRONT_FLIP: str = "FrontFlip"
	LEFT_FLIP: str = "LeftFlip"
	RIGHT_FLIP: str = "RightFlip"
	BACK_FLIP: str = "BackFlip"
	BOUND: str = "Bound"

class RobotDog:
	def __init__(self):
		self.conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
		self.frame_queue = Queue()
		self.window_title = "Dog Video"
		self.current_motion_switcher_mode = ""

		logging.basicConfig(level=logging.INFO)
		
		logging.debug("Successfully initialized Go2 module.")

	async def connect_to_robot(self):
		await self.conn.connect()

		self.motion_switch_mode("normal")

	async def _video_recv_camera_stream(self, track: MediaStreamTrack):
		while True:
			try:
				frame = await track.recv()
			except:
				pass
			
			img = frame.to_ndarray(format="bgr24")
			self.frame_queue.put(img)

	def _video_run_asyncio_loop(self, loop):
		asyncio.set_event_loop(loop)
		
		async def setup():
			try:
				await self.conn.connect()
				self.conn.video.switchVideoChannel(True)
				self.conn.video.add_track_callback(self._video_recv_camera_stream)
			except:
				pass
		
		loop.run_until_complete(setup())
		loop.run_forever()

	def _video_show_camera_thread(self, width, height):
		img = np.zeros((height, width, 3), dtype=np.uint8)
		cv2.imshow(self.window_title, img)
		cv2.waitKey(1)
		
		loop = asyncio.new_event_loop()
		
		t = threading.Thread(target=self._video_run_asyncio_loop, args=(loop,))
		t.start()
		
		try:
			while True:
				if not self.frame_queue.empty():
					img = self.frame_queue.get()
					cv2.imshow(self.window_title, img)
					
					if cv2.waitKey(1) & 0xFF == ord('q'):
						break
				else:
					time.sleep(0.01)
		finally:
			cv2.destroyAllWindows()
			loop.call_soon_threadsafe(loop.stop)
			t.join()

	def video_display_stream(self, width=640, height=480) -> None:
		threading.Thread(target=self._video_show_camera_thread, args=(width, height)).start()

	async def motion_get_current_mode(self) -> str:
		response = await self.conn.datachannel.pub_sub.publish_request_new(
			RTC_TOPIC["MOTION_SWITCHER"], 
			{"api_id": 1001}
		)

		if response['data']['header']['status']['code'] == 0:
			data = json.loads(response['data']['data'])
			current_motion_switcher_mode = data['name']
			print(f"Current motion mode: {current_motion_switcher_mode}")

			return current_motion_switcher_mode
		
		return ""

	async def motion_switch_mode(self, mode: str):
		self.motion_get_current_mode()

		if self.current_motion_switcher_mode != mode:
			print(f"Switching motion mode from {self.current_motion_switcher_mode} to '{mode}'...")
	
			await self.conn.datachannel.pub_sub.publish_request_new(
				RTC_TOPIC["MOTION_SWITCHER"], 
				{
					"api_id": 1002,
					"parameter": {"name": mode}
				}
			)

			await asyncio.sleep(5)
	
	async def motion_perform_normal_action(self, action: str):
		await self.conn.datachannel.pub_sub.publish_request_new(
			RTC_TOPIC["SPORT_MOD"], 
			{"api_id": SPORT_CMD[action]}
		)

		await asyncio.sleep(1)

	async def motion_move(self, forward = 0, side = 0, yaw = 0):
		await self.conn.datachannel.pub_sub.publish_request_new(
			RTC_TOPIC["SPORT_MOD"], 
			{
				"api_id": SPORT_CMD["Move"],
				"parameter": {"x": forward, "y": side, "z": yaw}
			}
		)

		await asyncio.sleep(1)

	def audio_play_mp3_from_file(self, file_name):
		mp3_path = os.path.join(os.path.dirname(__file__), file_name)
		
		logging.info(f"Playing MP3: {mp3_path}")
		player = MediaPlayer(mp3_path)
		
		self.conn.pc.addTrack(player.audio)
	