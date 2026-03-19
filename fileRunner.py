import os
import time
import requests


BASE_URL = "http://127.0.0.1:5000"


def wait_for_idle():
    while True:
        try:
            response = requests.get(f"{BASE_URL}/status")

            if response.json()["status"] == "idle":
                break

        except requests.exceptions.ConnectionError:
            print("Error: The API does not respond. Start main.py first!")
            return False

        time.sleep(1)
    return True


def run_all_tests():
    if not os.path.exists('videos'):
        print("Folder videos doesn't exist!")
        return

    video_files = [f for f in os.listdir('videos') if f.endswith('.mp4')]

    if not video_files:
        print("No videos found in the folder!")
        return
    print(f"Found {len(video_files)} test scenarios. Starting the execution:\n")
    print("-" * 30)

    for file_name in video_files:
        video_id = file_name.replace('.mp4', '')
        print(f"[START] video tested: {video_id}")
        play_response = requests.post(f"{BASE_URL}/play?video_id={video_id}")

        if play_response.status_code == 200:
            print("Video is ON, wait to finish:")
            time.sleep(1)

            if wait_for_idle():
                print(f"Scenario {video_id} has finished .\n")
        else:
            print(f"Video could not be open {video_id}. Error Message: {play_response.json()}")

    print("-" * 30)
    print("All tests done!")


if __name__ == "__main__":
    run_all_tests()